import cv2 as cv
import numpy as np

def show_all_cameras_cropped():
    # Beállítások
    BOTTOM_VALUES = [336, 294, 300]
    CROP_HEIGHT = 25
    num_cameras = 3
    
    caps = []
    
    # Kamerák inicializálása
    for i in range(num_cameras):
        cap = cv.VideoCapture(i)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        if not cap.isOpened():
            print(f"Figyelem: A(z) {i}. indexű kamera nem elérhető.")
        caps.append(cap)

    print("Kamerák elindítva. Kilépéshez nyomjon 'q'-t.")

    while True:
        frames = []
        
        for i, cap in enumerate(caps):
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    y_end = BOTTOM_VALUES[i]
                    y_start = max(0, y_end - CROP_HEIGHT)
                    
                    cropped = frame[y_start:y_end, :]
                    
                    cv.imshow(f"Camera {i} - Cropped", cropped)
                else:
                    print(f"Hiba a(z) {i}. kamera olvasásakor.")

        # Kilépés 'q' billentyűre
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    for cap in caps:
        cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    show_all_cameras_cropped()