"""
gesture_recognizer.py

Rule-based gesture recognizer for SignSense AI.

This module recognizes a few common static hand gestures using
the finger states returned by HandDetector.
"""


class GestureRecognizer:
    """
    Recognizes simple hand gestures.

    Finger states format:

    {
        "thumb": True,
        "index": False,
        "middle": False,
        "ring": False,
        "pinky": False
    }
    """

    def __init__(self):
        """Initialize the gesture recognizer."""
        self.gestures = {
            (False, False, False, False, False): "FIST",
            (True, True, True, True, True): "OPEN PALM",
            (True, False, False, False, False): "THUMBS UP",
            (False, True, False, False, False): "POINT",
            (False, True, True, False, False): "PEACE",
            (True, True, False, False, False): "GUN",
            (False, True, False, False, True): "ROCK",
            (True, True, False, False, True): "I LOVE YOU",
            (True, False, True, True, True): "OK",
        }

    def recognize(self, finger_states: dict) -> str:
        """
        Recognize a hand gesture.

        Args:
            finger_states: Dictionary returned by HandDetector.

        Returns:
            Gesture name as a string.
        """

        key = (
            finger_states["thumb"],
            finger_states["index"],
            finger_states["middle"],
            finger_states["ring"],
            finger_states["pinky"],
        )

        return self.gestures.get(key, "UNKNOWN")

    def available_gestures(self):
        """
        Return all supported gesture names.
        """

        return list(self.gestures.values())