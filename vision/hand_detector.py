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
        Draw hand landmarks, skeleton, bounding boxes,
        and handedness labels.
        """

        if not results.multi_hand_landmarks:
            return

        height, width, _ = frame.shape

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness,
        ):

            # ---------------------------------
            # Draw landmarks and hand skeleton
            # ---------------------------------
            self._mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self._mp_hands.HAND_CONNECTIONS,
                self._mp_drawing_styles.get_default_hand_landmarks_style(),
                self._mp_drawing_styles.get_default_hand_connections_style(),
            )

            # ---------------------------------
            # Bounding Box
            # ---------------------------------
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

            # ---------------------------------
            # Hand Label
            # ---------------------------------
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

    def get_landmarks(self, frame, results) -> list:
        """
        Extract landmark coordinates for all detected hands.

        Returns:
            A list where each element represents one detected hand.
            Each hand contains a list of 21 landmark dictionaries.
        """

        hands_data = []

        if not results.multi_hand_landmarks:
            return hands_data

        height, width, _ = frame.shape

        for hand_landmarks in results.multi_hand_landmarks:

            landmarks = []

            for landmark_id, landmark in enumerate(hand_landmarks.landmark):
                landmarks.append(
                    {
                        "id": landmark_id,
                        "x": int(landmark.x * width),
                        "y": int(landmark.y * height),
                        "z": landmark.z,
                    }
                )

            hands_data.append(landmarks)

        return hands_data

    def get_fingertips(self, frame, results) -> list:
        """
        Extract fingertip coordinates.

        Returns:
            A list of dictionaries, one for each detected hand.
        """

        fingertips = []

        if not results.multi_hand_landmarks:
            return fingertips

        height, width, _ = frame.shape

        fingertip_ids = {
            "thumb": 4,
            "index": 8,
            "middle": 12,
            "ring": 16,
            "pinky": 20,
        }

        for hand_landmarks in results.multi_hand_landmarks:

            hand_data = {}

            for finger_name, landmark_id in fingertip_ids.items():

                landmark = hand_landmarks.landmark[landmark_id]

                hand_data[finger_name] = {
                    "id": landmark_id,
                    "x": int(landmark.x * width),
                    "y": int(landmark.y * height),
                    "z": landmark.z,
                }

            fingertips.append(hand_data)

        return fingertips

    def get_finger_states(self, results) -> list:
        """
        Determine whether each finger is open or closed.

        Returns:
            A list of dictionaries, one for each detected hand.
        """

        finger_states = []

        if not results.multi_hand_landmarks:
            return finger_states

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness,
        ):

            landmarks = hand_landmarks.landmark

            hand_label = handedness.classification[0].label

            # ---------------------------------
            # Thumb
            # ---------------------------------
            thumb_tip = landmarks[4]
            thumb_ip = landmarks[3]

            # Camera is mirrored (cv2.flip(frame, 1))
            if hand_label == "Right":
                thumb_open = thumb_tip.x < thumb_ip.x
            else:
                thumb_open = thumb_tip.x > thumb_ip.x

            # ---------------------------------
            # Other Fingers
            # ---------------------------------
            index_open = landmarks[8].y < landmarks[6].y
            middle_open = landmarks[12].y < landmarks[10].y
            ring_open = landmarks[16].y < landmarks[14].y
            pinky_open = landmarks[20].y < landmarks[18].y

            finger_states.append(
                {
                    "thumb": thumb_open,
                    "index": index_open,
                    "middle": middle_open,
                    "ring": ring_open,
                    "pinky": pinky_open,
                }
            )

        return finger_states

    def close(self) -> None:
        """
        Release MediaPipe resources.
        """

        self._hands.close()