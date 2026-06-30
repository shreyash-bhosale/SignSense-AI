import cv2

from camera.camera import Camera
from utils.fps import FPSCounter
from vision.hand_detector import HandDetector


def main():
    camera = Camera()
    fps_counter = FPSCounter()
    hand_detector = HandDetector()

    camera.open()

    print("✅ SignSense AI started.")
    print("Press 'Q' to quit.")

    try:
        while True:
            frame = camera.read()
            results = hand_detector.process(frame)
            hand_detector.draw_landmarks(frame, results)

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

            cv2.imshow("SignSense AI", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        hand_detector.close()
        camera.release()
        cv2.destroyAllWindows()
        print("👋 SignSense AI closed.")


if __name__ == "__main__":
    main()
