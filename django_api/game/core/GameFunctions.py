import threading

import cv2 as cv
import math

import numpy as np

from game.core.ContourProcessor import ContourProcessor
from game.core.DartAnalyzer import DartAnalyzer
from game.core.ImageProcessor import ImageProcessor

class GameFunctions:
    cameras = None
    _camera_lock = threading.Lock()

    @staticmethod
    def turnOnCameras(num_cameras=3, resolution=(1280, 720), needCalibration=False):
        with GameFunctions._camera_lock:
            if GameFunctions.cameras is not None:
                print("Kamerák már be vannak kapcsolva, újraindítás nem szükséges.")
                return GameFunctions.cameras
            img_height = 3
            bottom_values = [336, 296, 300]
            default_crop_params = {
                1: (333, 336, 220, 1081),
                2: (293, 296, 205, 1074),
                3: (297, 302, 216, 1063)
            }

            cameras = []

            for i in range(1, num_cameras + 1):
                bottom = bottom_values[i - 1]

                cap = cv.VideoCapture(i - 1)
                cap.set(cv.CAP_PROP_FRAME_WIDTH, resolution[0])
                cap.set(cv.CAP_PROP_FRAME_HEIGHT, resolution[1])

                if needCalibration:
                    leftCordHelper, rightCordHelper = ImageProcessor.calibrate_crop_width(i)
                    left = math.floor(leftCordHelper)
                    right = math.ceil(rightCordHelper)
                    crop_params = (bottom - img_height, bottom, left, right)
                else:
                    crop_params = default_crop_params[i]
                    left = crop_params[2]
                    right = crop_params[3]

                cameras.append({
                    "id": i,
                    "cap": cap,
                    "crop_params": crop_params,
                    "left": left,
                    "right": right,
                    "img_width": right - left
                })
                GameFunctions.cameras = cameras
                print(f"Kamera {i} sikeresen beállítva")
        return cameras

    @staticmethod
    def turnOffCameras(num_cameras = 3):
        for i in range(1, num_cameras + 1):
            cap_name = f"cap{i}"
            if cap_name in globals():
                cap = globals()[cap_name]
                if cap.isOpened():
                    cap.release()

    @staticmethod
    def getRefImage(cameras):
        ref_imgs = []
        ref_contours_list = []
        white_imgs = []

        for cam in cameras:
            cap = cam["cap"]
            crop_params = cam["crop_params"]

            while True:
                ret, frame = cap.read()
                if not ret:
                    print(f"Kamera {cam['id']}: nem sikerült képet olvasni.")
                    continue

                ref_img = ImageProcessor.crop(frame, *crop_params)
                ref_img = ImageProcessor.rescale(ref_img, 1)
                ref_img_gray = ImageProcessor.to_grayscale(ref_img)
                ref_contours = ContourProcessor.find_contours(ref_img_gray)
                white_img = np.full_like(ref_img_gray, 255)

                ref_imgs.append(ref_img_gray)
                ref_contours_list.append(ref_contours)
                white_imgs.append(white_img)

                print(f"Kamera {cam['id']}: referencia kép elmentve.")
                break

        return {
            "ref_imgs": ref_imgs,
            "ref_contours_list": ref_contours_list,
            "white_imgs": white_imgs
        }

