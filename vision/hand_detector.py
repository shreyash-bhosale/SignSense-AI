"""
hand_detector.py

This module contains the HandDetector class, which is responsible for
initializing and managing MediaPipe Hands for real-time hand detection.
"""

import cv2
import mediapipe as mp


class HandDetector:
    """
    A wrapper around MediaPipe Hands.

    This class initializes the MediaPipe Hands solution and provides
    methods for detecting hands and drawing landmarks.
    """

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        """
        Initialize the MediaPipe Hands detector.
        """

        # MediaPipe Hands module
        self._mp_hands = mp.solutions.hands

        # MediaPipe drawing utilities
        self._mp_drawing = mp.solutions.drawing_utils

        # Default drawing styles
        self._mp_drawing_styles = mp.solutions.drawing_styles

        # Hand detector instance
        self._hands = self._mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(self, frame):
        """
        Process a BGR frame and return MediaPipe detection results.
        """

        # Convert OpenCV's BGR image to RGB.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Improve performance by marking the image as read-only.
        rgb_frame.flags.writeable = False

        # Run hand detection.
        results = self._hands.process(rgb_frame)

        # Allow writing to the image again.
        rgb_frame.flags.writeable = True

        return results

    def draw_landmarks(self, frame, results):
        """
        Draw hand landmarks and connections on the frame.
        """

        if not results.multi_hand_landmarks:
            return

        for hand_landmarks in results.multi_hand_landmarks:
            self._mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self._mp_hands.HAND_CONNECTIONS,
                self._mp_drawing_styles.get_default_hand_landmarks_style(),
                self._mp_drawing_styles.get_default_hand_connections_style(),
            )

    def close(self) -> None:
        """
        Release MediaPipe resources.
        """
        self._hands.close()