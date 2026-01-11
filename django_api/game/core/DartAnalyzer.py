import math


class DartAnalyzer:

    @staticmethod
    def get_x_coordinate(contours):
        x_sum, count = 0, 0
        y_max = float('-inf')
        for cnt in contours:
            for point in cnt:
                _, y = point[0]
                if y > y_max:
                    y_max = y

        for cnt in contours:
            for point in cnt:
                x, y = point[0]
                if abs(y - y_max) <= 0.5:
                    x_sum += x
                    count += 1

        return x_sum / count if count else -1

    @staticmethod
    def calculate_angle(x_coord, img_width, view_angle=58.1):
        if x_coord == -1:
            return -1
        return view_angle - (view_angle / img_width * x_coord)

    @staticmethod
    def angleforCam1(angle):
        if angle != -1:
            angle = angle + 240.9
        return angle

    @staticmethod
    def angleforCam2(angle):
        if angle != -1:
            angle = angle + 120.9
        return angle

    @staticmethod
    def angleforCam3(angle):
        if angle != -1:
            angle = angle + 0.9
        return angle

    '''@staticmethod
    def adjust_camera_angle(angle, camera_offset):
        """Adjusts the calculated angle for different camera positions."""
        if (angle == -1):
            return -1
        return angle + camera_offset'''

    @staticmethod
    def get_dart_coordinates(angle_cam1, angle_cam2, angle_cam3):
        cam_positions = {
            "cam1": (0, 35),
            "cam2": (30.3, -17.5),
            "cam3": (-30.3, -17.5)
        }

        cam1_slope = math.tan(math.radians(angle_cam1))
        cam2_slope = math.tan(math.radians(angle_cam2))
        cam3_slope = math.tan(math.radians(angle_cam3))

        m1, c1 = DartAnalyzer.line_equation(cam_positions["cam1"], cam1_slope)
        m2, c2 = DartAnalyzer.line_equation(cam_positions["cam2"], cam2_slope)
        m3, c3 = DartAnalyzer.line_equation(cam_positions["cam3"], cam3_slope)

        intersection1 = DartAnalyzer.find_intersection(m1, c1, m2, c2)
        intersection2 = DartAnalyzer.find_intersection(m2, c2, m3, c3)
        intersection3 = DartAnalyzer.find_intersection(m3, c3, m1, c1)

        if angle_cam1 == -1:
            intersection1 = 'FalseData'
            intersection3 = 'FalseData'

        if angle_cam2 == -1:
            intersection1 = 'FalseData'
            intersection2 = 'FalseData'

        if angle_cam3 == -1:
            intersection2 = 'FalseData'
            intersection3 = 'FalseData'

        return intersection1, intersection2, intersection3

    @staticmethod
    def line_equation(point, slope):
        x, y = point
        return slope, y - slope * x

    @staticmethod
    def find_intersection(m1, c1, m2, c2):
        x = (c2 - c1) / (m1 - m2)
        y = m1 * x + c1
        return x, y

    @staticmethod
    def triangulate_dart(coord1, coord2, coord3):
        if coord1 == 'FalseData':
            if coord2 == 'FalseData':
                return coord3
            else:
                return coord2
        if coord2 == 'FalseData' and coord3 == 'FalseData':
            return coord1

        coord1X, coord1Y = coord1
        coord2X, coord2Y = coord2
        coord3X, coord3Y = coord3

        coordXAvg = (coord1X + coord2X + coord3X) / 3
        coordYAvg = (coord1Y + coord2Y + coord3Y) / 3
        return coordXAvg, coordYAvg

    @staticmethod
    def get_dart_score(dart_coordinates):

        BOARD_RADIUS = 17
        BULLSEYE_RADIUS = 0.635
        OUTER_BULL_RADIUS = 1.6
        TRIPLE_RING_INNER = 9.9
        TRIPLE_RING_OUTER = 10.7
        DOUBLE_RING_INNER = 16.2
        DOUBLE_RING_OUTER = 17
        ANGLE_PER_SECTION = 18
        DARTBOARD_NUMBERS = [6, 13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10]

        scores = []

        for x, y in dart_coordinates:
            distance = math.sqrt(x ** 2 + y ** 2)
            angle = math.degrees(math.atan2(y, x))

            if angle < 0:
                angle += 360

            if distance <= BULLSEYE_RADIUS:
                scores.append(50)
                continue
            elif distance <= OUTER_BULL_RADIUS:
                scores.append(25)
                continue

            segment_index = int((angle + (ANGLE_PER_SECTION / 2)) // ANGLE_PER_SECTION) % 20
            base_score = DARTBOARD_NUMBERS[segment_index]

            if TRIPLE_RING_INNER <= distance <= TRIPLE_RING_OUTER:
                scores.append(f"T{base_score}")
            elif DOUBLE_RING_INNER <= distance <= DOUBLE_RING_OUTER:
                scores.append(f"D{base_score}")
            elif distance > BOARD_RADIUS:
                scores.append("No Score")
            else:
                scores.append(base_score)
        return scores
