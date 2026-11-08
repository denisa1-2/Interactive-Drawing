
import cv2
import time

from hand_tracking import HandTracker
from gestures import (
    is_draw_gesture,
    is_open_palm,
    is_erase_gesture,
    is_resize_gesture,
    get_pinch_ratio,
    PINCH_THRESHOLD,
    PINCH_RELEASE_THRESHOLD
)
from drawing import DrawingCanvas
from color_palette import ColorPalette
from shape_menu import ShapeMenu

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
WINDOW_NAME = "Interactive Drawing"

PALM_HOLD_TIME = 0.5
ERASER_RESIZE_SENSITIVITY = 100


def get_fingertip(hand, width, height):
    x = int(hand[8].x * width)
    y = int(hand[8].y * height)

    x = max(0, min(width - 1, x))
    y = max(0, min(height - 1, y))

    return (x, y)


def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("Error: Could not open the camera!")

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    success, frame = camera.read()

    if not success:
        camera.release()
        raise RuntimeError("Error: Could not read frame!")

    height, width = frame.shape[:2]

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, FRAME_WIDTH, FRAME_HEIGHT)

    canvas = DrawingCanvas(width, height)
    palette = ColorPalette(width, height)
    shape_menu = ShapeMenu(width, height)

    selected_shape = "free"

    right_palm_start = None
    left_palm_start = None

    right_palm_armed = True
    left_palm_armed = True

    right_pinch_active = False
    left_pinch_active = False

    resize_start_distance = None
    resize_start_size = None

    is_fullscreen = False
    tracker = None

    try:
        tracker = HandTracker()

        while True:
            success, frame = camera.read()

            if not success:
                print("Error: Could not read frame!")
                break

            frame = cv2.flip(frame, 1)

            hands = tracker.detect(frame)
            right_hand = hands["Right"]
            left_hand = hands["Left"]

            current_time = time.monotonic()

            is_drawing = False
            is_erasing = False
            is_resizing = False

            right_cursor = None
            left_cursor = None

            right_pinch_started = False
            left_pinch_started = False

            right_pinch_ratio = None
            left_pinch_ratio = None

            if right_hand is not None:
                right_cursor = get_fingertip(right_hand, width, height)
                right_pinch_ratio = get_pinch_ratio(right_hand, width, height)

                if right_pinch_ratio > PINCH_RELEASE_THRESHOLD:
                    right_pinch_active = False

                if right_pinch_ratio < PINCH_THRESHOLD and not right_pinch_active:
                    right_pinch_active = True
                    right_pinch_started = True

                right_open_palm = is_open_palm(right_hand, width, height)

                if not right_open_palm:
                    right_palm_start = None
                    right_palm_armed = True

                elif not palette.is_open and not shape_menu.is_open and right_palm_armed:
                    if right_palm_start is None:
                        right_palm_start = current_time

                    elif current_time - right_palm_start >= PALM_HOLD_TIME:
                        palette.open()
                        right_palm_armed = False
                        right_palm_start = None
                        right_pinch_active = False
                        canvas.stop_drawing()
                        canvas.cancel_shape()

            else:
                canvas.stop_drawing()
                canvas.cancel_shape()
                right_palm_start = None
                right_palm_armed = True
                right_pinch_active = False

            if left_hand is not None:
                left_cursor = get_fingertip(left_hand, width, height)
                left_pinch_ratio = get_pinch_ratio(left_hand, width, height)

                if left_pinch_ratio > PINCH_RELEASE_THRESHOLD:
                    left_pinch_active = False

                if left_pinch_ratio < PINCH_THRESHOLD and not left_pinch_active:
                    left_pinch_active = True
                    left_pinch_started = True

                left_open_palm = is_open_palm(left_hand, width, height)

                if not left_open_palm:
                    left_palm_start = None
                    left_palm_armed = True

                elif not shape_menu.is_open and not palette.is_open and left_palm_armed:
                    if left_palm_start is None:
                        left_palm_start = current_time

                    elif current_time - left_palm_start >= PALM_HOLD_TIME:
                        shape_menu.open()
                        left_palm_armed = False
                        left_palm_start = None
                        left_pinch_active = False
                        canvas.stop_drawing()
                        canvas.stop_erasing()
                        canvas.cancel_shape()

            else:
                canvas.stop_erasing()
                left_palm_start = None
                left_palm_armed = True
                left_pinch_active = False

            if palette.is_open:
                canvas.stop_drawing()
                canvas.stop_erasing()

                if right_pinch_started:
                    new_color = palette.get_hovered_color(right_cursor)

                    if new_color is not None:
                        canvas.set_color(new_color)
                        palette.close()
                        right_palm_start = None
                        right_palm_armed = False
                        right_pinch_active = True

            elif shape_menu.is_open:
                canvas.stop_drawing()
                canvas.stop_erasing()

                if left_pinch_started:
                    new_shape = shape_menu.get_hovered_shape(left_cursor)

                    if new_shape is not None:
                        selected_shape = new_shape
                        shape_menu.close()
                        canvas.cancel_shape()
                        left_palm_start = None
                        left_palm_armed = False
                        left_pinch_active = True

            else:
                if right_hand is not None:
                    if selected_shape == "free":
                        is_drawing = is_draw_gesture(right_hand, width, height)

                        if is_drawing:
                            canvas.draw(right_cursor)
                        else:
                            canvas.stop_drawing()

                    else:
                        canvas.stop_drawing()

                        if canvas.shape_start_point is not None and right_pinch_started:
                            canvas.confirm_shape(right_cursor, selected_shape)

                        elif canvas.shape_start_point is None and not right_pinch_active and is_draw_gesture(right_hand, width, height):
                            canvas.start_shape(right_cursor)

                if left_hand is not None:
                    is_resizing = is_resize_gesture(left_hand, width, height)
                    is_erasing = is_erase_gesture(left_hand, width, height)

                    if is_resizing:
                        canvas.stop_erasing()

                        current_distance = left_pinch_ratio

                        if resize_start_distance is None:
                            resize_start_distance = current_distance
                            resize_start_size = canvas.eraser_size

                        distance_change = current_distance - resize_start_distance
                        new_size = resize_start_size + distance_change * ERASER_RESIZE_SENSITIVITY

                        canvas.set_eraser_size(new_size)

                    else:
                        resize_start_distance = None
                        resize_start_size = None

                        if is_erasing:
                            canvas.erase(left_cursor)
                        else:
                            canvas.stop_erasing()

            if palette.is_open or shape_menu.is_open:
                canvas.stop_erasing()
                resize_start_distance = None
                resize_start_size = None

            if left_hand is None:
                resize_start_distance = None
                resize_start_size = None

            frame = canvas.apply_to_frame(frame)

            if selected_shape != "free" and canvas.shape_start_point is not None and right_cursor is not None and not palette.is_open and not shape_menu.is_open:
                frame = canvas.preview_shape(frame, right_cursor, selected_shape)

            if palette.is_open:
                frame = palette.draw(frame, canvas.brush_color, right_cursor)

            elif shape_menu.is_open:
                frame = shape_menu.draw(frame, selected_shape, left_cursor)

            else:
                if right_cursor is not None:
                    if is_drawing or (selected_shape != "free" and canvas.shape_start_point is not None):
                        cv2.circle(frame, right_cursor, 6, (0, 255, 0), -1)

                if left_cursor is not None and (is_erasing or is_resizing):
                    canvas.draw_eraser_cursor(frame, left_cursor)

            if palette.is_open:
                status = "COLOR PALETTE"
            elif shape_menu.is_open:
                status = "SHAPE MENU"
            elif is_drawing and is_erasing:
                status = "DRAWING + ERASING"
            elif is_resizing:
                status = "RESIZING ERASER"
            elif is_erasing:
                status = "ERASING"
            elif canvas.shape_start_point is not None:
                status = "SHAPE PREVIEW - PINCH TO CONFIRM"
            elif is_drawing:
                status = "DRAWING"
            else:
                status = "NOT DRAWING"

            cv2.putText(frame, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Tool: {selected_shape.upper()}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            cv2.putText(frame, f"Eraser Size: {canvas.eraser_size} px", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

            cv2.circle(frame, (width - 30, 30), 13, canvas.brush_color, -1)
            cv2.circle(frame, (width - 30, 30), 13, (180, 180, 180), 2)

            cv2.putText(frame, "C - Clear | F - Fullscreen | Q - Quit", (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("f"):
                is_fullscreen = not is_fullscreen

                if is_fullscreen:
                    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(WINDOW_NAME, FRAME_WIDTH, FRAME_HEIGHT)

            if key == ord("q"):
                break

            if key == ord("c"):
                canvas.clear()

    finally:
        if tracker is not None:
            tracker.close()

        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
