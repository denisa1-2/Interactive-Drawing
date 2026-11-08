
import cv2


PALETTE_COLORS = [
    "#E53935", "#F4511E", "#FB8C00",
    "#FDD835", "#7CB342", "#00897B",
    "#00ACC1", "#1E88E5", "#3949AB",
    "#8E24AA", "#D81B60", "#F48FB1",
    "#FF8A80", "#FFCC80", "#FFF59D",
    "#C5E1A5", "#80DEEA", "#90CAF9",
    "#CE93D8", "#A1887F", "#FFFFFF",
    "#BDBDBD", "#616161", "#000000"
]


class ColorPalette:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.is_open = False
        self.cells = []
        self.panel = None

        self.calculate_layout()

    def hex_to_bgr(self, hex_color):
        return (
            int(hex_color[5:7], 16),
            int(hex_color[3:5], 16),
            int(hex_color[1:3], 16)
        )

    def calculate_layout(self):
        columns = 6
        rows = 4

        cell_size = max(
            18,
            min(
                56,
                (self.width - 60) // columns,
                (self.height - 120) // (rows + 1)
            )
        )

        gap = 5

        grid_width = columns * cell_size + (columns - 1) * gap
        grid_height = rows * cell_size + (rows - 1) * gap

        panel_width = grid_width + 32
        panel_height = grid_height + 85

        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2

        self.panel = (
            panel_x,
            panel_y,
            panel_width,
            panel_height
        )

        grid_x = panel_x + 16
        grid_y = panel_y + 57

        self.cells = []

        for i in range(len(PALETTE_COLORS)):
            row = i // columns
            col = i % columns

            x1 = grid_x + col * (cell_size + gap)
            y1 = grid_y + row * (cell_size + gap)

            self.cells.append((
                x1,
                y1,
                x1 + cell_size,
                y1 + cell_size
            ))

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def draw(self, frame, selected_color, cursor=None):
        if not self.is_open:
            return frame

        px, py, pw, ph = self.panel

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (px, py),
            (px + pw, py + ph),
            (35, 35, 35),
            -1
        )

        cv2.addWeighted(
            overlay,
            0.88,
            frame,
            0.12,
            0,
            frame
        )

        cv2.putText(
            frame,
            "COLOR PALETTE",
            (px + 16, py + 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Pinch to select",
            (px + 16, py + 44),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (190, 190, 190),
            1
        )

        for i, (x1, y1, x2, y2) in enumerate(self.cells):
            color = self.hex_to_bgr(PALETTE_COLORS[i])

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                -1
            )

            if color == selected_color:
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 255, 255),
                    2
                )

        if cursor is not None:
            cv2.circle(
                frame,
                cursor,
                8,
                (255, 255, 255),
                2
            )

        return frame

    def get_hovered_color(self, cursor):
        if not self.is_open or cursor is None:
            return None

        x, y = cursor

        for i, (x1, y1, x2, y2) in enumerate(self.cells):
            if x1 <= x <= x2 and y1 <= y <= y2:
                return self.hex_to_bgr(PALETTE_COLORS[i])

        return None
