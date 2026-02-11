import cv2

def check_cameras(limit=3):
    for i in range(limit):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cv2.imshow(f'Camera Index: {i}', frame)
                print(f"Kamera található az indexen: {i}")
            cap.release()
    
    print("Nyomj meg egy gombot a kilépéshez...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

check_cameras()