
import mediapipe as mp
import cv2
import time
from pathlib import Path


class HandTracker:
    def __init__(self):
        model_path = Path(__file__).resolve().parent / "hand_landmarker.task"

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(model_path)
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.detector = mp.tasks.vision.HandLandmarker.create_from_options(
            options
        )

        self.start_time = time.monotonic()
        self.last_timestamp = -1

    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        timestamp = int((time.monotonic() - self.start_time) * 1000)
        timestamp = max(timestamp, self.last_timestamp + 1)
        self.last_timestamp = timestamp

        result = self.detector.detect_for_video(
            mp_image,
            timestamp
        )

        hands = {"Left": None, "Right": None}

        for i, landmarks in enumerate(result.hand_landmarks):
            hand_label = result.handedness[i][0].category_name
            hand_label = "Left" if hand_label == "Right" else "Right"

            if hand_label in hands:
                hands[hand_label] = landmarks

        return hands

    def close(self):
        self.detector.close()
