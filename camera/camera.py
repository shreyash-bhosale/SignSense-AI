"""
Camera module for SignSense AI.
Handles webcam initialization, frame capture, and cleanup.
"""

import cv2


class Camera:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    def open(self):
        """Open the webcam."""
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise Exception("❌ Unable to open webcam.")

    def read(self):
        """Read a frame."""
        if self.cap is None:
            raise Exception("Camera has not been opened.")

        success, frame = self.cap.read()

        if not success:
            raise Exception("Failed to capture frame.")

        return frame

    def release(self):
        """Release the webcam."""
        if self.cap:
            self.cap.release()