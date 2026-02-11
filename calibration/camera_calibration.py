import cv2 as cv
import numpy as np
import math
import time

# === KONFIGURÁCIÓ ===
BOTTOM_VALUES = [336, 294, 300]
IMG_HEIGHT = 10
NUM_CAMERAS = 3
RESOLUTION = (1280, 720)

class ImageProcessor:
    @staticmethod
    def to_grayscale(img):
        return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    @staticmethod
    def crop(img, top, bottom, left, right):
        return img[top:bottom, left:right]

    @staticmethod
    def calibrate_crop_width(i, cap, initial_crop):
        print(f"\n>>> KALIBRÁCIÓ - Kamera {i}")
        print("Művelet: Szúrja be a nyilakat a két szélére, majd nyomjon 'r'-t a képablakon.")
        
        while True:
            ret, frame = cap.read()
            if not ret: continue
            
            cv.imshow(f"Kamera {i} - Teljes kep (Nyomjon 'r'-t ha kesz)", frame)
            if cv.waitKey(1) & 0xFF == ord('r'):
                cv.destroyWindow(f"Kamera {i} - Teljes kep (Nyomjon 'r'-t ha kesz)")
                break

        left_val = ImageProcessor.calibrate_crop_width_side("Bal", i, cap, initial_crop)
        right_val = ImageProcessor.calibrate_crop_width_side("Jobb", i, cap, initial_crop)

        ret, frame = cap.read()
        offset = (2 * frame.shape[1] // 3)
        return left_val, offset + right_val

    @staticmethod
    def calibrate_crop_width_side(side, i, cap, crop_params):
        print(f"--- {side} oldal detektálása... (Várjon amíg stabilizálódik)")
        last_x = None
        prev_time = 0
        
        while True:
            current_time = time.time()
            if current_time - prev_time >= 0.5:
                ret, frame = cap.read()
                if not ret: continue

                cropped = ImageProcessor.crop(frame, *crop_params)
                
                if side == "Bal":
                    side_img = cropped[:, :cropped.shape[1] // 3]
                else:
                    side_img = cropped[:, 2 * cropped.shape[1] // 3:]

                gray = ImageProcessor.to_grayscale(side_img)
                edges = cv.Canny(gray, 150, 250)
                contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                
                current_x = DartAnalyzer.get_x_coordinate(contours)
                
                display = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)
                cv.drawContours(display, contours, -1, (0, 255, 0), 2)
                cv.imshow(f"Kalibracio - Cam {i} {side}", display)

                if last_x is not None and abs(current_x - last_x) < 0.2 and current_x != -1:
                    cv.destroyWindow(f"Kalibracio - Cam {i} {side}")
                    return current_x
                
                last_x = current_x
                prev_time = current_time

            if cv.waitKey(1) & 0xFF == ord('q'):
                return -1

class DartAnalyzer:
    @staticmethod
    def get_x_coordinate(contours):
        x_sum, count, y_max = 0, 0, float('-inf')
        if not contours: return -1
        
        for cnt in contours:
            for point in cnt:
                y = point[0][1]
                if y > y_max: y_max = y
        
        for cnt in contours:
            for point in cnt:
                x, y = point[0]
                if abs(y - y_max) <= 0.5:
                    x_sum += x
                    count += 1
        return x_sum / count if count else -1

def run_calibration():
    final_results = {}

    for i in range(1, NUM_CAMERAS + 1):
        cap = cv.VideoCapture(i - 1)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, RESOLUTION[0])
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, RESOLUTION[1])

        if not cap.isOpened():
            print(f"Hiba: Kamera {i} nem található!")
            continue

        bottom = BOTTOM_VALUES[i - 1]
        initial_crop = (bottom - IMG_HEIGHT, bottom, 0, RESOLUTION[0])

        try:
            left_raw, right_raw = ImageProcessor.calibrate_crop_width(i, cap, initial_crop)
            
            left = math.floor(left_raw)
            right = math.ceil(right_raw)
            
            final_results[i] = {
                "crop_params": (bottom - IMG_HEIGHT, bottom, left, right),
                "left": left,
                "right": right,
                "width": right - left
            }
            print(f"Kamera {i} kalibrálva: L={left}, R={right}")
        
        except Exception as e:
            print(f"Hiba történt a(z) {i}. kamera kalibrálásakor: {e}")
        finally:
            cap.release()

    # === VÉGSŐ LOGOLÁS ===
    print("\n" + "="*50)
    print("MÁSOLHATÓ KALIBRÁCIÓS ÉRTÉKEK")
    print("="*50)
    print("default_crop_params = {")
    for cam_id, data in final_results.items():
        comma = "," if cam_id < len(final_results) else ""
        print(f"    {cam_id}: {data['crop_params']}{comma}  # Width: {data['width']}")
    print("}")
    print("="*50)

if __name__ == "__main__":
    run_calibration()
    cv.destroyAllWindows()