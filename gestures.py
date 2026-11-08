
import math


FINGER_ANGLE_THRESHOLD = 155
PINCH_THRESHOLD = 0.35
PINCH_RELEASE_THRESHOLD = 0.50

ERASER_RESIZE_THRESHOLD = 0.65


def calculate_angle(point1, point2, point3, width, height):
    ax = (point1.x - point2.x) * width
    ay = (point1.y - point2.y) * height

    bx = (point3.x - point2.x) * width
    by = (point3.y - point2.y) * height

    dot_product = ax * bx + ay * by

    length_a = math.hypot(ax, ay)
    length_b = math.hypot(bx, by)

    if length_a == 0 or length_b == 0:
        return 0

    cosine = dot_product / (length_a * length_b)
    cosine = max(-1.0, min(1.0, cosine))

    return math.degrees(math.acos(cosine))


def is_finger_extended(hand, mcp, pip, tip, width, height):
    angle = calculate_angle(
        hand[mcp], hand[pip], hand[tip], width, height
    )

    return angle > FINGER_ANGLE_THRESHOLD

def calculate_distance(point1, point2, width, height):
    dx = (point1.x - point2.x) * width
    dy = (point1.y - point2.y) * height

    return math.hypot(dx, dy)

def get_pinch_ratio(hand, width, height):
    fingertip_distance = calculate_distance(
        hand[4], hand[8], width, height
    )

    palm_width = calculate_distance(
        hand[5], hand[17], width, height
    )

    if palm_width < 1:
        return float("inf")

    return fingertip_distance / palm_width

def is_draw_gesture(hand, width, height):
    index_up = is_finger_extended(
        hand, 5, 6, 8, width, height
    )

    middle_down = not is_finger_extended(
        hand, 9, 10, 12, width, height
    )

    ring_down = not is_finger_extended(
        hand, 13, 14, 16, width, height
    )

    pinky_down = not is_finger_extended(
        hand, 17, 18, 20, width, height
    )

    return (
        index_up
        and middle_down
        and ring_down
        and pinky_down
    )


def is_open_palm(hand, width, height):
    thumb_up = is_finger_extended(
        hand, 2, 3, 4, width, height
    )

    index_up = is_finger_extended(
        hand, 5, 6, 8, width, height
    )

    middle_up = is_finger_extended(
        hand, 9, 10, 12, width, height
    )

    ring_up = is_finger_extended(hand, 13, 14, 16, width, height)
    pinky_up = is_finger_extended(hand, 17, 18, 20, width, height)

    return (thumb_up and index_up and middle_up and ring_up and pinky_up)

def is_erase_gesture(hand, width, height):
    index_up = is_finger_extended(hand, 5, 6, 8, width, height)
    middle_down = not is_finger_extended(hand, 9, 10, 12, width, height)
    ring_down = not is_finger_extended(hand, 13, 14, 16, width, height)
    pinky_down = not is_finger_extended(hand, 17, 18, 20, width, height)
    thumb_extended = is_finger_extended(hand, 2, 3, 4, width, height)

    return (index_up and middle_down and ring_down and pinky_down and not thumb_extended)

def is_resize_gesture(hand, width, height):
    index_up = is_finger_extended(hand, 5, 6, 8, width, height)
    middle_down = not is_finger_extended(hand, 9, 10, 12, width, height)
    ring_down = not is_finger_extended(hand, 13, 14, 16, width, height)
    pinky_down = not is_finger_extended(hand, 17, 18, 20, width, height)
    thumb_extended = is_finger_extended(hand, 2, 3, 4, width, height)
    thumb_distance = get_pinch_ratio(hand, width, height)

    return (index_up and middle_down and ring_down and pinky_down and thumb_extended and thumb_distance >= ERASER_RESIZE_THRESHOLD)

def is_pinch_gesture(hand, width, height):
    return get_pinch_ratio(hand, width, height) < PINCH_THRESHOLD
