import cv2
import numpy as np

SHAPE_OPTIONS = [
    ("free", "FREE DRAW"),
    ("line", "LINE"),
    ("rectangle", "RECTANGLE"),
    ("circle", "CIRCLE"),
    ("triangle", "TRIANGLE")
]

class ShapeMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.is_open = False
        self.cells = []

        self.panel = None

        self.calculate_layout()

    def calculate_layout(self):
        columns = 3
        rows = 2

        cell_width = max(90, min(180, (self.width - 80) //  columns))
        cell_height = max(75, min(120, (self.height - 120) // rows))

        gap = 12

        grid_width = columns * cell_width + (columns - 1) * gap
        grid_height = rows * cell_height + (rows - 1) * gap

        panel_width = grid_width + 40
        panel_height = grid_height + 85

        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2

        self.panel = (panel_x, panel_y, panel_width, panel_height)

        grid_x = panel_x + 20
        grid_y = panel_y + 65

        self.cells = []

        for i, (shape_type, label) in enumerate(SHAPE_OPTIONS):
            row = i // columns
            col = i % columns

            x1 = grid_x + col * (cell_width + gap)
            y1 = grid_y + row * (cell_height + gap)

            self.cells.append((shape_type, label, x1, y1, x1 + cell_width, y1 + cell_height))

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def draw_icon(self, frame, shape_type, center):
        cx, cy = center

        color = (235, 235, 235)
        thickness = 3

        if shape_type == "free":
            points = [
                (cx - 35, cy + 12),
                (cx - 15, cy - 18),
                (cx + 5, cy + 8),
                (cx + 25, cy - 20),
                (cx + 38, cy + 10)
            ]

            for i in range(len(points) - 1):
                cv2.line(frame, points[i], points[i + 1], color, thickness, cv2.LINE_AA)
        elif shape_type == "line":
            cv2.line(frame, (cx - 35, cy + 20), (cx + 35, cy - 20), color,
                     thickness, cv2.LINE_AA)
        elif shape_type == "rectangle":
            cv2.rectangle(frame, (cx - 35, cy - 22), (cx + 35, cy + 22), color,
                          thickness, cv2.LINE_AA)
        elif shape_type == "circle":
            cv2.circle(frame, center, 25, color, thickness, cv2.LINE_AA)
        elif shape_type == "triangle":
            points = [
                (cx, cy - 28),
                (cx - 32, cy + 25),
                (cx + 32, cy + 25)
            ]
            cv2.polylines(frame, [np.array(points, dtype=np.int32)],
                          True, color, thickness, cv2.LINE_AA)

    def draw(self, frame, selected_shape="free", cursor=None):
        if not self.is_open:
            return frame

        px, py, pw, ph = self.panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (px, py), (px + pw, py + ph),
                      (35, 35, 35), -1)
        cv2.addWeighted(overlay, 0.90, frame, 0.10, 0, frame)
        cv2.putText(frame, "SHAPE TOOLS", (px + 20, py + 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (255, 255, 255), 2)
        cv2.putText(frame, "Pinch to select a tool", (px + 20, py + 52), cv2.FONT_HERSHEY_SIMPLEX,
                    0.45, (190, 190, 190), 1)

        for shape_type, label, x1, y1, x2, y2 in self.cells:
            is_selected = shape_type == selected_shape

            background = ((85, 115, 155) if is_selected else (55, 55, 55))
            cv2.rectangle(frame, (x1, y1), (x2, y2), background, -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (150, 150, 150), 1)

            center = ((x1 + x2) // 2,y1 + 37)
            self.draw_icon(frame, shape_type, center)
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0]

            text_x = (x1 + x2 - text_size[0]) // 2
            cv2.putText(frame, label, (text_x, y2 - 15), cv2.FONT_HERSHEY_SIMPLEX,
                        0.45, (255, 255, 255), 1)

        if cursor is not None:
            cv2.circle(frame, cursor, 8, (255, 255, 255), 2)

        return frame

    def get_hovered_shape(self, cursor):
        if not self.is_open or cursor is None:
            return None

        x, y = cursor
        for shape_type, label, x1, y1, x2, y2 in self.cells:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return shape_type

        return None