import cv2 as cv

@staticmethod
def find_contours(img):
        edges = cv.Canny(img, 150, 250)
        contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        return contours

@staticmethod
def show_camera_with_contours(frame, contours, window_name="Camera Live"):
        display = frame.copy()
        for cnt in contours:
            cv.drawContours(display, [cnt], -1, (0, 255, 0), 1)

        cv.imshow(window_name, display)

@staticmethod
def show_camera3_live():
        cap = cv.VideoCapture(2)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)


        print("Camera 3 élőkép elindítva...")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Nem érkezik kép a 3-as kamerából!")
                break

            # Kontúrok keresése
            contours = find_contours(frame)

            # Kontúrokkal ellátott kép kirajzolása
            show_camera_with_contours(
                frame,
                contours,
                window_name="Camera 3 - Contours"
            )

            # ESC kilép
            if cv.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv.destroyAllWindows()

def nothing(x):
    pass

# === Ablak létrehozása ===
cv.namedWindow("Crop Filter")

# Trackbarok létrehozása (max értékeket majd frissítjük a kamera alapján)
cv.createTrackbar("Top", "Crop Filter", 0, 720, nothing)
cv.createTrackbar("Bottom", "Crop Filter", 0, 720, nothing)
cv.createTrackbar("Left", "Crop Filter", 0, 1280, nothing)
cv.createTrackbar("Right", "Crop Filter", 0, 1280, nothing)

# === Kamera beállítás ===

#show_camera3_live()

cap = cv.VideoCapture(2)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("Nem sikerült megnyitni a kamerát.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Hiba a képkocka olvasásakor.")
        break

    h, w = frame.shape[:2]

    # Trackbar értékek lekérése
    top = cv.getTrackbarPos("Top", "Crop Filter")
    bottom = cv.getTrackbarPos("Bottom", "Crop Filter")
    left = cv.getTrackbarPos("Left", "Crop Filter")
    right = cv.getTrackbarPos("Right", "Crop Filter")

    # Határok korrigálása
    top = min(top, h-1)
    bottom = min(bottom, h-1-top)
    left = min(left, w-1)
    right = min(right, w-1-left)

    # Kép vágása
    cropped = frame[top:h-bottom, left:w-right]

    # Info kiírás
    ch, cw = cropped.shape[:2]
    text = f"Méret: {cw}x{ch}"
    cv.putText(cropped, text, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Egy pixel érték (középen)
    if ch > 0 and cw > 0:
        px = cropped[ch//2, cw//2]  # BGR
        ptext = f"Pixel közép: {px.tolist()}"
        cv.putText(cropped, ptext, (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Megjelenítés
    cv.imshow("Crop Filter", cropped)

    # Kilépés: 'q'
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()