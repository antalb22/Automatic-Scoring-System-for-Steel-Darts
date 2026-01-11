import threading
import time
import uuid

import requests

from game.core.ContourProcessor import ContourProcessor
from game.core.DartAnalyzer import DartAnalyzer
from game.core.GameFunctions import GameFunctions
from game.core.ImageProcessor import ImageProcessor

API_BASE_URL = "http://192.168.0.24:5173/api"  # http://localhost:5173/api
THROW_URL = f"{API_BASE_URL}/autothrows"
END_GAME_URL = f"{API_BASE_URL}/endgame"

TOLERANCE = 0.5
DETECTION_DELAY = 0.05
TIMEOUT_MULTIPLIER = 15
ROUND_PAUSE_SECONDS = 4

stop_simulation = threading.Event()


def simulate_throws(game):
    game_id = game.get("gameId")
    cameras = GameFunctions.cameras

    if not cameras:
        print("Hiba: Nincsenek kamerák inicializálva!")
        return

    ref_data = GameFunctions.getRefImage(cameras)
    original_ref_contours_list = ref_data["ref_contours_list"]
    white_imgs = ref_data["white_imgs"]

    print("Automatikus játék indult")
    current_round = 1

    while not stop_simulation.is_set():
        print(f"\n--- 🎯 {current_round}. KÖR KEZDŐDIK ---")

        angles_for_cams = [[], [], []]
        confirmed_xs = [[], [], []]
        detected_flags = [False, False, False]
        prev_xs = [None, None, None]
        detection_times = [0, 0, 0]
        darts_in_round = 0
        prev_time = time.time()
        ref_contours_list = [tuple(item for item in c) for c in original_ref_contours_list]

        while darts_in_round < 3 and not stop_simulation.is_set():

            if stop_simulation.is_set():
                print("🛑 Leállítás érzékelve.")
                return

            current_time = time.time()
            all_detected = all(detected_flags)

            if current_time - prev_time >= DETECTION_DELAY:
                if all_detected:
                    for cam_idx in range(3):
                        cam_xs = confirmed_xs[cam_idx][darts_in_round]
                        if not cam_xs:
                            continue

                        img_width = cameras[cam_idx]["img_width"]
                        angle = DartAnalyzer.calculate_angle(int(cam_xs), img_width)
                        angle_func = getattr(DartAnalyzer, f"angleforCam{cam_idx + 1}")
                        angles_for_cams[cam_idx].append(angle_func(angle))

                    if all(len(a) > darts_in_round for a in angles_for_cams):
                        angle1 = angles_for_cams[0][darts_in_round]
                        angle2 = angles_for_cams[1][darts_in_round]
                        angle3 = angles_for_cams[2][darts_in_round]

                        coord1, coord2, coord3 = DartAnalyzer.get_dart_coordinates(angle1, angle2, angle3)
                        x, y = DartAnalyzer.triangulate_dart(coord1, coord2, coord3)

                        throw_data = {
                            "playerId": 1,
                            "gameId": game_id,
                            "x": x,
                            "y": y,
                            "throwId": str(uuid.uuid4())
                        }

                        try:
                            response = requests.post(THROW_URL, json=throw_data, timeout=2)
                            print("Dobás elküldve." if response.ok else f"Hiba: {response.status_code}")
                        except Exception as e:
                            print(f"Hiba a küldésnél: {e}")

                        if stop_simulation.is_set():
                            print("🛑 Leállítás érzékelve (dobás után).")
                            return

                        darts_in_round += 1
                        detected_flags = [False, False, False]
                        prev_xs = [None, None, None]
                        continue

                for i in range(3):
                    if not detected_flags[i]:
                        cap = cameras[i]["cap"]
                        crop_params = cameras[i]["crop_params"]

                        ret, frame = cap.read()
                        if not ret:
                            continue

                        processed = ImageProcessor.crop(frame, *crop_params)
                        processed_gray = ImageProcessor.to_grayscale(processed)
                        live_contours = ContourProcessor.find_contours(processed_gray)

                        ref_contours = ref_contours_list[i]
                        diff_img = ContourProcessor.find_differences(ref_contours, live_contours, white_imgs[i].copy())
                        diff_img_contours = ContourProcessor.find_contours(diff_img)

                        current_x = DartAnalyzer.get_x_coordinate(diff_img_contours)

                        if current_x != -1:
                            print(f"Cam{i + 1} nyíl: X={current_x:.2f}")

                        if prev_xs[i] is not None and abs(current_x - prev_xs[i]) <= TOLERANCE and current_x != -1:
                            detected_flags[i] = True
                            confirmed_xs[i].append(current_x)
                            detection_times[i] = current_time
                            print(f"🎯 Kamera {i + 1} rögzítve: X={current_x:.2f}")
                            ref_contours_list[i] = live_contours
                        else:
                            prev_xs[i] = current_x

                if sum(detected_flags) >= 2:
                    max_det_time = max(t for t, d in zip(detection_times, detected_flags) if d)
                    if current_time - max_det_time > DETECTION_DELAY * TIMEOUT_MULTIPLIER:
                        for i in range(3):
                            if not detected_flags[i]:
                                print(f"⏱️ Kamera {i + 1} timeout -> -1")
                                confirmed_xs[i].append(-1)
                                detected_flags[i] = True

                prev_time = current_time

        print(f"--- 🏁 {current_round}. kör vége ---")

        steps = int(ROUND_PAUSE_SECONDS / 0.1)
        for _ in range(steps):
            if stop_simulation.is_set():
                print("🛑 Leállítás érzékelve (szünetben).")
                return
            time.sleep(0.1)

        current_round += 1

    print("Játék leállítva.")
