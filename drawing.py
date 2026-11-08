
import cv2
import numpy as np
from shapes import draw_shape


class DrawingCanvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.drawing_layer = np.zeros(
            (height, width, 3),
            dtype=np.uint8
        )

        self.drawing_mask = np.zeros(
            (height, width),
            dtype=np.uint8
        )

        self.brush_color = (0, 0, 0)
        self.brush_thickness = 5

        self.eraser_size = 40
        self.min_eraser_size = 10
        self.max_eraser_size = 100

        self.previous_point = None
        self.previous_eraser_point = None

        self.shape_start_point = None

    def draw(self, point):
        if self.previous_point is not None:
            cv2.line(
                self.drawing_layer,
                self.previous_point,
                point,
                self.brush_color,
                self.brush_thickness
            )

            cv2.line(
                self.drawing_mask,
                self.previous_point,
                point,
                255,
                self.brush_thickness
            )
        else:
            cv2.circle(
                self.drawing_layer,
                point,
                self.brush_thickness // 2,
                self.brush_color,
                -1
            )

            cv2.circle(
                self.drawing_mask,
                point,
                self.brush_thickness // 2,
                255,
                -1
            )

        self.previous_point = point

    def erase(self, point):
        if self.previous_eraser_point is not None:
            cv2.line(
                self.drawing_mask,
                self.previous_eraser_point,
                point,
                0,
                self.eraser_size
            )
        else:
            cv2.circle(self.drawing_mask, point, self.eraser_size // 2, 0, -1)

        self.previous_eraser_point = point

    def stop_erasing(self):
        self.previous_eraser_point = None

    def set_eraser_size(self, size):
        self.eraser_size = max(self.min_eraser_size, min(self.max_eraser_size, int(size)))

    def draw_eraser_cursor(self, frame, point):
        if point is None:
            return frame

        cv2.circle(frame, point, self.eraser_size // 2, (255, 255, 255), 2)
        cv2.circle(frame, point, 3, (0, 0, 255), -1)

        return frame

    def stop_drawing(self):
        self.previous_point = None

    def set_color(self, color):
        self.brush_color = color

    def clear(self):
        self.drawing_layer[:] = 0
        self.drawing_mask[:] = 0
        self.previous_point = None
        self.previous_eraser_point = None
        self.shape_start_point = None

    def apply_to_frame(self, frame):
        frame[self.drawing_mask > 0] = self.drawing_layer[
            self.drawing_mask > 0
        ]

        return frame

    def start_shape(self, point):
        self.shape_start_point = point
        self.stop_drawing()

    def preview_shape(self, frame, point, shape_type):
        if self.shape_start_point is None or point is None:
            return frame

        preview = frame.copy()

        draw_shape(preview, shape_type, self.shape_start_point, point, self.brush_color,
                   self.brush_thickness)

        return preview

    def confirm_shape(self, point, shape_type):
        if self.shape_start_point is None or point is None:
            return

        draw_shape(self.drawing_layer, shape_type, self.shape_start_point, point,
                   self.brush_color, self.brush_thickness)
        draw_shape(self.drawing_mask, shape_type, self.shape_start_point, point,
                   255, self.brush_thickness)
        self.shape_start_point = None

    def cancel_shape(self):
        self.shape_start_point = None
