import cv2 as cv
import time
from game.core.ContourProcessor import ContourProcessor
from game.core.DartAnalyzer import DartAnalyzer

class ImageProcessor:

    @staticmethod
    def rescale(img, scale):
        width = int(img.shape[1] * scale)
        height = int(img.shape[0] * scale)
        return cv.resize(img, (width, height), interpolation=cv.INTER_AREA)

    @staticmethod
    def to_grayscale(img):
        return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    @staticmethod
    def crop(img, top, bottom, left, right):
        return img[top:bottom, left:right]

    @staticmethod
    def load_image(path, scale=0.5, crop_params=None, grayScale = True):
        img = cv.imread(path)
        img = ImageProcessor.rescale(img, scale)
        if grayScale:
            img = ImageProcessor.to_grayscale(img)
        if crop_params:
            img = ImageProcessor.crop(img, *crop_params)
        return img

    @staticmethod
    def calibrate_crop_width(i):
        cap = globals()[f"cap{i}"]

        print(f"Kalibráció kamera {i}: szúrja be a nyilakat a megfelelő helyekre és nyomjon 'r'-t.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Nem sikerült képet olvasni.")
                continue
            cv.imshow("Live Calibration Image", frame)
            key = cv.waitKey(1) & 0xFF
            if key == ord('r'):
                break

        leftSide = "Bal"
        rightSide = "Jobb"
        leftCord = ImageProcessor.calibrate_crop_width_side(leftSide, i)
        rightCord = ImageProcessor.calibrate_crop_width_side(rightSide, i)
        rightCord = (2*frame.shape[1]//3) + rightCord
        return leftCord, rightCord


    @staticmethod
    def calibrate_crop_width_side(side, i):
        cap = globals()[f"cap{i}"]
        crop_params = globals()[f"crop_params{i}"]

        prev_time = 0
        delay = 1
        last_x = None

        while True:
            current_time = time.time()

            if current_time - prev_time >= delay:
                ret, frame = cap.read()
                if not ret:
                    print(f"Nem sikerült képet olvasni a kamera {i}-ről.")
                    continue

                frame = ImageProcessor.crop(frame, *crop_params)

                if side == "Bal":
                    side_third = frame[:, :frame.shape[1] // 3]
                else:
                    side_third = frame[:, 2 * frame.shape[1] // 3:]

                side_contours = ContourProcessor.find_contours(ImageProcessor.to_grayscale(side_third))
                side_x = DartAnalyzer.get_x_coordinate(side_contours)
                current_x = side_x

                cv.imshow(f"Live Calibration Image ({side} - Cam {i})", side_third)
                ContourProcessor.show_camera_with_contours(side_third, side_contours, f"SideContours_{side}_Cam{i}")
                print(f"{side} side current_x = {current_x}")

                if last_x is not None and abs(current_x - last_x) < 0.1 and current_x != -1:
                    print(f"{side} oldali nyíl x koordináta (Cam {i}): {side_x}")
                    cv.destroyAllWindows()
                    return current_x
                else:
                    last_x = current_x

                prev_time = current_time

            if cv.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv.destroyAllWindows()
                break