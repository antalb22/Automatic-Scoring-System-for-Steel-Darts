import cv2 as cv

class ContourProcessor:

    @staticmethod
    def find_contours(img):
        edges = cv.Canny(img, 150, 250)
        contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        return contours

    @staticmethod
    def find_differences(base_contours, new_contours, img, tolerance=5):
        for new_cnt in new_contours:
            draw = True
            x2, y2, _, _ = cv.boundingRect(new_cnt)
            for base_cnt in base_contours:
                x1, y1, _, _ = cv.boundingRect(base_cnt)
                if tolerance > (x1 - x2) > -tolerance and tolerance > (y1 - y2) > -tolerance:
                    draw = False
                    break
            if draw:
                cv.drawContours(img, [new_cnt], -1, (0, 0, 255), 1)
        return img

    @staticmethod
    def show_camera_with_contours(frame, contours, window_name="Camera Live"):
        display = frame.copy()
        for cnt in contours:
            cv.drawContours(display, [cnt], -1, (0, 255, 0), 1)
        cv.imshow(window_name, display)