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
        static_image_mode: bool = False,
        max_num_hands: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:

        self._mp_hands = mp.solutions.hands
        self._mp_drawing = mp.solutions.drawing_utils
        self._mp_drawing_styles = mp.solutions.drawing_styles

        self._hands = self._mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    # ----------------------------------------------------------
    # Process Frame
    # ----------------------------------------------------------

    def process(self, frame) -> Any:

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False

        results = self._hands.process(rgb)

        rgb.flags.writeable = True

        return results

    # ----------------------------------------------------------
    # Draw Hand
    # ----------------------------------------------------------

    def draw_landmarks(self, frame, results):

        if not results.multi_hand_landmarks:
            return

        h, w, _ = frame.shape

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness,
        ):

            self._mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self._mp_hands.HAND_CONNECTIONS,
                self._mp_drawing_styles.get_default_hand_landmarks_style(),
                self._mp_drawing_styles.get_default_hand_connections_style(),
            )

            xs = []
            ys = []

            for landmark in hand_landmarks.landmark:
                xs.append(int(landmark.x * w))
                ys.append(int(landmark.y * h))

            xmin = min(xs)
            xmax = max(xs)
            ymin = min(ys)
            ymax = max(ys)

            padding = 20

            cv2.rectangle(
                frame,
                (xmin - padding, ymin - padding),
                (xmax + padding, ymax + padding),
                (0, 255, 0),
                2,
            )

            label = handedness.classification[0].label
            score = handedness.classification[0].score

            cv2.putText(
                frame,
                f"{label} ({score:.2f})",
                (xmin, ymin - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

    # ----------------------------------------------------------
    # Get Normalized Landmarks
    # ----------------------------------------------------------

    def get_landmarks(self, frame, results) -> list:
        """
        Returns landmarks normalized relative to the wrist.

        This format matches dataset.csv exactly.
        """

        hands_data = []

        if not results.multi_hand_landmarks:
            return hands_data

        for hand_landmarks in results.multi_hand_landmarks:

            wrist = hand_landmarks.landmark[0]

            landmarks = []

            for landmark_id, landmark in enumerate(hand_landmarks.landmark):

                landmarks.append(
                    {
                        "id": landmark_id,
                        "x": landmark.x - wrist.x,
                        "y": landmark.y - wrist.y,
                        "z": landmark.z - wrist.z,
                    }
                )

            hands_data.append(landmarks)

        return hands_data

    # ----------------------------------------------------------
    # Get Fingertips
    # ----------------------------------------------------------

    def get_fingertips(self, frame, results):

        fingertips = []

        if not results.multi_hand_landmarks:
            return fingertips

        h, w, _ = frame.shape

        fingertip_ids = {
            "thumb": 4,
            "index": 8,
            "middle": 12,
            "ring": 16,
            "pinky": 20,
        }

        for hand_landmarks in results.multi_hand_landmarks:

            hand = {}

            for finger, idx in fingertip_ids.items():

                landmark = hand_landmarks.landmark[idx]

                hand[finger] = {
                    "id": idx,
                    "x": int(landmark.x * w),
                    "y": int(landmark.y * h),
                    "z": landmark.z,
                }

            fingertips.append(hand)

        return fingertips

    # ----------------------------------------------------------
    # Finger States
    # ----------------------------------------------------------

    def get_finger_states(self, results):

        states = []

        if not results.multi_hand_landmarks:
            return states

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness,
        ):

            lm = hand_landmarks.landmark

            hand = handedness.classification[0].label

            if hand == "Right":
                thumb = lm[4].x < lm[3].x
            else:
                thumb = lm[4].x > lm[3].x

            index = lm[8].y < lm[6].y
            middle = lm[12].y < lm[10].y
            ring = lm[16].y < lm[14].y
            pinky = lm[20].y < lm[18].y

            states.append(
                {
                    "thumb": thumb,
                    "index": index,
                    "middle": middle,
                    "ring": ring,
                    "pinky": pinky,
                }
            )

        return states

    # ----------------------------------------------------------
    # Close
    # ----------------------------------------------------------

    def close(self):

        self._hands.close()