import time
import cv2

from camera.camera import Camera
from utils.fps import FPSCounter
from vision.hand_detector import HandDetector


def main():
    """
    Main application for SignSense AI.
    """

    camera = Camera()
    fps_counter = FPSCounter()
    hand_detector = HandDetector()

    camera.open()

    print("✅ SignSense AI started.")
    print("Press 'Q' to quit.")

    # Print results every 5 seconds
    last_print_time = time.time()

    try:
        while True:
            # -----------------------------
            # Read camera frame
            # -----------------------------
            frame = camera.read()

            # Mirror the frame
            frame = cv2.flip(frame, 1)

            # -----------------------------
            # Hand Detection
            # -----------------------------
            results = hand_detector.process(frame)

            # -----------------------------
            # Landmark Extraction
            # -----------------------------
            landmarks = hand_detector.get_landmarks(frame, results)

            # -----------------------------
            # Fingertip Extraction
            # -----------------------------
            fingertips = hand_detector.get_fingertips(frame, results)

            # -----------------------------
            # Finger State Detection
            # -----------------------------
            finger_states = hand_detector.get_finger_states(results)

            # -----------------------------
            # Print every 5 seconds
            # -----------------------------
            current_time = time.time()

            if current_time - last_print_time >= 5:
                if finger_states:
                    print("\n========== Finger States ==========")

                    for hand_number, state in enumerate(finger_states, start=1):
                        print(f"Hand {hand_number}")

                        for finger, status in state.items():
                            print(
                                f"  {finger.capitalize():<7}: {'UP' if status else 'DOWN'}"
                            )

                        print("-----------------------------------")

                else:
                    print("\nNo hands detected.")

                last_print_time = current_time

            # -----------------------------
            # Draw Hand Landmarks
            # -----------------------------
            hand_detector.draw_landmarks(frame, results)

            # -----------------------------
            # FPS Counter
            # -----------------------------
            fps = fps_counter.get_fps()

            cv2.putText(
                frame,
                f"FPS: {fps}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            # -----------------------------
            # Show Window
            # -----------------------------
            cv2.imshow("SignSense AI", frame)

            # Quit when Q is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        hand_detector.close()
        camera.release()
        cv2.destroyAllWindows()
        print("👋 SignSense AI closed.")


if __name__ == "__main__":
    main()