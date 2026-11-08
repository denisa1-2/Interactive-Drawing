import cv2 
import math

def draw_shape(image, shape_type, start_point, end_point, color, thickness=5):
    x1, y1 = start_point
    x2, y2 = end_point

    if shape_type == "line":
        cv2.line(image, start_point, end_point, color, thickness, cv2.LINE_AA)
    elif shape_type == "rectangle":
        top_left = (min(x1, x2), min(y1, y2))
        bottom_right = (max(x1, x2), max(y1, y2))
        cv2.rectangle(image, top_left, bottom_right, color, thickness, cv2.LINE_AA)
    elif shape_type == "circle":
        radius = int(math.hypot(x2 - x1, y2 - y1))
        cv2.circle(image, start_point, max(1, radius), color, thickness, cv2.LINE_AA)
    elif shape_type == "triangle":
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)

        top_point = ((left + right) // 2, top)
        left_point = (left, bottom)
        right_point = (right, bottom)

        cv2.line(image, top_point, left_point, color, thickness, cv2.LINE_AA)
        cv2.line(image, left_point, right_point, color, thickness, cv2.LINE_AA)
        cv2.line(image, right_point, top_point, color, thickness, cv2.LINE_AA)
    else:
        raise ValueError(f"Unsupported shape type: {shape_type}")

    return image
        