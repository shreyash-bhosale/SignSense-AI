"""
main.py

SignSense AI

Real-time ASL Alphabet Recognition using:
- MediaPipe Hands
- Random Forest Classifier
"""

import time

import cv2

from camera.camera import Camera
from utils.fps import FPSCounter
from vision.hand_detector import HandDetector
from vision.sign_predictor import SignPredictor


def main():

    camera = Camera()
    hand_detector = HandDetector()
    fps_counter = FPSCounter()
    predictor = SignPredictor()

    camera.open()

    print("===================================")
    print("      SignSense AI Started")
    print("===================================")
    print("Press Q to quit.\n")

    prediction = "No Hand"
    confidence = 0.0

    last_prediction_time = time.time()

    try:

        while True:

            # -----------------------------------
            # Read Frame
            # -----------------------------------
            frame = camera.read()

            frame = cv2.flip(frame, 1)

            # -----------------------------------
            # Detect Hands
            # -----------------------------------
            results = hand_detector.process(frame)

            hand_detector.draw_landmarks(frame, results)

            landmarks = hand_detector.get_landmarks(frame, results)

            # -----------------------------------
            # Predict Every 0.5 Seconds
            # -----------------------------------
            if time.time() - last_prediction_time >= 0.5:

                if landmarks:

                    prediction, confidence = predictor.predict(
                        landmarks[0]
                    )

                    print(
                        f"Prediction: {prediction} "
                        f"({confidence * 100:.2f}%)"
                    )

                else:

                    prediction = "No Hand"
                    confidence = 0.0

                last_prediction_time = time.time()

            # -----------------------------------
            # Display Prediction
            # -----------------------------------
            cv2.putText(
                frame,
                f"Prediction : {prediction}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Confidence : {confidence * 100:.2f}%",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            fps = fps_counter.get_fps()

            cv2.putText(
                frame,
                f"FPS : {fps}",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2,
            )

            cv2.imshow("SignSense AI", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:

        hand_detector.close()
        camera.release()
        cv2.destroyAllWindows()

        print("\nSignSense AI Closed.")


if __name__ == "__main__":
    main()