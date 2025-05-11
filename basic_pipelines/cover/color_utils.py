import cv2
import numpy as np

def create_color_mask(hsv, lower_color, upper_color):
    return cv2.inRange(hsv, lower_color, upper_color)

def red_mask(hsv):
    lower_red = np.array([0, 100, 100], dtype=np.uint8)
    upper_red = np.array([10, 255, 255], dtype=np.uint8)
    return create_color_mask(hsv, lower_red, upper_red)