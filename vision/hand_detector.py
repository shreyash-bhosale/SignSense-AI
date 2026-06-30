"""
hand_detector.py

This module contains the HandDetector class, which is responsible for
detecting hands using MediaPipe and drawing landmarks on video frames.
"""

from typing import Any

import cv2
import mediapipe as mp


class HandDetector:
    """
    Wrapper around MediaPipe Hands for real-time hand detection.
    """

    def __init__(
        self,
        static_image_mode: bool =False,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        """
        Initialize the MediaPipe Hands detector.
        """

        self._mp_hands = mp.solutions.hands
        self._mp_drawing = mp.solutions.drawing_utils
        self._mp_drawing_styles = mp.solutions.drawing_styles

        self._hands = self._mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(self, frame) -> Any:
        """
        Process a BGR frame and return MediaPipe detection results.
        """

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        results = self._hands.process(rgb_frame)

        rgb_frame.flags.writeable = True

        return results

    def draw_landmarks(self, frame, results) -> None:
        """
        Draw landmarks, bounding boxes, and handedness labels.
        """

        if not results.multi_hand_landmarks:
            return

        height, width, _ = frame.shape

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness,
        ):

            # -------------------------------
            # Draw landmarks
            # -------------------------------
            self._mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self._mp_hands.HAND_CONNECTIONS,
                self._mp_drawing_styles.get_default_hand_landmarks_style(),
                self._mp_drawing_styles.get_default_hand_connections_style(),
            )

            # -------------------------------
            # Bounding Box
            # -------------------------------
            x_coordinates = []
            y_coordinates = []

            for landmark in hand_landmarks.landmark:
                x_coordinates.append(int(landmark.x * width))
                y_coordinates.append(int(landmark.y * height))

            x_min = min(x_coordinates)
            x_max = max(x_coordinates)
            y_min = min(y_coordinates)
            y_max = max(y_coordinates)

            padding = 20

            cv2.rectangle(
                frame,
                (x_min - padding, y_min - padding),
                (x_max + padding, y_max + padding),
                (0, 255, 0),
                2,
            )

            # -------------------------------
            # Hand Label
            # -------------------------------
            label = handedness.classification[0].label
            confidence = handedness.classification[0].score

            cv2.putText(
                frame,
                f"{label} ({confidence:.2f})",
                (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

    def close(self) -> None:
        """
        Release MediaPipe resources.
        """

        self._hands.close()