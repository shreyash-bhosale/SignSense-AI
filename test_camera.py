from camera.camera import Camera

camera = Camera()

camera.open()

frame = camera.read()

print("Frame shape:", frame.shape)

camera.release()

print("✅ Camera test successful!")