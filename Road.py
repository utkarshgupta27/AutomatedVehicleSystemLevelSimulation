import pygame
import cv2, os
import threading
import numpy as np
import tensorflow as tf  # assuming your YOLO model is in TensorFlow
import time
import pygame
from constants import *

global minLineLength, maxLineGap
minLineLength = 20
maxLineGap = 4

class Road:

    def __init__(self):
        # Defining some sample road properties
        self.road_types = ["asphalt", "gravel", "dirt", "snow"]
        self.roughness = {
            "asphalt": 0.1,   # Roughness scale: 0 (smooth) to 1 (very rough)
            "gravel": 0.6,
            "dirt": 0.8,
            "snow": 0.7
        }
        self.friction = {
            "asphalt": 0.9,   # Friction scale: 0 (no friction) to 1 (high friction)
            "gravel": 0.5,
            "dirt": 0.4,
            "snow": 0.3
        }

    def get_road_properties(self, position):
        """
        This function returns road properties based on a given position.
        For simplicity, the road type changes every 100 units of position.
        You can modify the logic to be more sophisticated if needed.
        """

        # Based on position, determine which type of road it is
        road_type = self.road_types[position // 100 % len(self.road_types)]

        return {
            "road_type": road_type,
            "roughness": self.roughness[road_type],
            "friction": self.friction[road_type]
        }
    @staticmethod
    def lane_decider(surface):
        pygame_image = pygame.surfarray.array3d(surface)
        return pygame_image

    def calculate_lane_center_and_slope(self, lines):
        if lines is None:
            return None, None

        x_center_accum = 0
        y_center_accum = 0
        slopes = []

        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            x_center_accum += (x1 + x2) / 2
            y_center_accum += (y1 + y2) / 2

            # Calculate slope and avoid division by zero
            if x2 - x1 != 0:
                slopes.append((y2 - y1) / (x2 - x1))

        # Calculate average center and slope
        lane_center = (int(x_center_accum / len(lines)), int(y_center_accum / len(lines)))
        avg_slope = sum(slopes) / len(slopes) if slopes else 0

        return lane_center, avg_slope

    @staticmethod
    def pygame_surface_to_opencv_image(surface):
        """Convert a pygame surface to an OpenCV image."""
        opencv_image = pygame.surfarray.array3d(surface).transpose([1, 0, 2])
        return opencv_image
    
    def detect_lanes_pygame(self, image, minLineLength=95, maxLineGap=100, canny_thresholds=(255, 255),solid_line_threshold=200.0):
        road_image = self.pygame_surface_to_opencv_image(image)
        gray = cv2.cvtColor(road_image[:, :, ::-1], cv2.COLOR_BGR2GRAY)
        contrasted = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        blurred = cv2.GaussianBlur(contrasted, (5, 5), 0) 
        canny = cv2.Canny(blurred, *canny_thresholds)
        
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(canny, kernel, iterations=1)

        height, width = road_image.shape[:2]

        rectangle_top_left = (-50, height//2-30)
        rectangle_bottom_right = (width+150, 2*height//3-20)
        rectangle = np.array([[rectangle_top_left, (rectangle_bottom_right[0], rectangle_top_left[1]), rectangle_bottom_right, (rectangle_top_left[0], rectangle_bottom_right[1])]])
        polygons = np.array(rectangle, dtype=np.int32)

        mask = np.zeros_like(dilated)
        cv2.fillPoly(mask, polygons, 255)
        masked_image = cv2.bitwise_and(dilated, mask)  # Use dilated here
        lines = cv2.HoughLinesP(masked_image, 2, np.pi/180, 100, np.array([]), minLineLength=minLineLength, maxLineGap=maxLineGap)
        line_image = np.zeros(road_image.shape, dtype=road_image.dtype)

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line.reshape(4)
                length = ((x2 - x1)**2 + (y2 - y1)**2)**0.5

                if length > solid_line_threshold:  # Solid line
                    cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 10)
                else:  # Dashed line
                    cv2.line(line_image, (x1, y1), (x2, y2), (0, 0, 255), 10)
                combined_image = cv2.addWeighted(road_image, 0.8, line_image, 1, 1)
                # Draw the ROI polygon for debugging purposes
            cv2.polylines(combined_image, [polygons], isClosed=True, color=(255, 255, 0), thickness=2)
        return lines, combined_image

    def car_position_in_lane(self,lines, car_image_np, combined_image):
        
        lane_center,avg_slope=self.calculate_lane_center_and_slope(lines)
            # If we have a valid center, draw the car there.
        if lane_center:
            # car_image_np = self.pygame_surface_to_opencv_image(car_scaled)
            car_height, car_width = car_image_np.shape[:2]
            top_left_corner = (lane_center[0] - car_width // 2, lane_center[1] - car_height // 2)
            combined_image[top_left_corner[1]: top_left_corner[1] + car_height, top_left_corner[0]: top_left_corner[0] + car_width] = car_image_np
        
        return combined_image

if __name__=="__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(current_dir, "assets\\")

    rd = Road()
    pygame_image = pygame.image.load(assets_path + "city\\" + "4Wayroad800x600.png")

    while True:  # Loop until a break condition is met
        if pygame_image.get_size() != (800, 600):
            scaled_pygame_image = pygame.transform.scale(pygame_image, (WIDTH, HEIGHT))
            com_img = rd.detect_lanes_pygame(scaled_pygame_image)
        else:
            com_img = rd.detect_lanes_pygame(pygame_image)

        cv2.imshow('Image', com_img)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # Escape key to break
            break

    cv2.destroyAllWindows()

    # Example:
    # road = Road()
    # position = 150  # Sample position
    # print(road.get_road_properties(position))
