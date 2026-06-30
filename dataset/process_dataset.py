"""
process_dataset.py

Processes the ASL dataset by extracting MediaPipe hand landmarks
and saving them to dataset.csv.

Folder structure:

dataset/
│
├── raw/
│   ├── A/
│   ├── B/
│   ├── ...
│   └── Z/
│
└── dataset.csv
"""

import csv
import os

import cv2
import mediapipe as mp


# -----------------------------
# Paths
# -----------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(CURRENT_DIR, "raw")
CSV_FILE = os.path.join(CURRENT_DIR, "dataset.csv")


# -----------------------------
# MediaPipe
# -----------------------------
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5,
)


# -----------------------------
# CSV Header
# -----------------------------
header = ["label"]

for i in range(21):
    header.extend(
        [
            f"x{i}",
            f"y{i}",
            f"z{i}",
        ]
    )


# -----------------------------
# Create CSV
# -----------------------------
with open(CSV_FILE, "w", newline="") as file:

    writer = csv.writer(file)
    writer.writerow(header)

    total_images = 0
    successful = 0

    # Loop through A-Z folders
    for label in sorted(os.listdir(RAW_DIR)):

        label_path = os.path.join(RAW_DIR, label)

        if not os.path.isdir(label_path):
            continue

        print(f"\nProcessing {label}...")

        for image_name in os.listdir(label_path):

            image_path = os.path.join(label_path, image_name)

            image = cv2.imread(image_path)

            if image is None:
                continue

            total_images += 1

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            results = hands.process(image_rgb)

            if not results.multi_hand_landmarks:
                continue

            hand = results.multi_hand_landmarks[0]

            wrist = hand.landmark[0]

            row = [label]

            # Normalize relative to wrist
            for landmark in hand.landmark:

                row.append(landmark.x - wrist.x)
                row.append(landmark.y - wrist.y)
                row.append(landmark.z - wrist.z)

            writer.writerow(row)

            successful += 1

print("\n====================================")
print("Dataset processing completed.")
print(f"Total images      : {total_images}")
print(f"Successful samples: {successful}")
print(f"Failed            : {total_images - successful}")
print(f"Saved CSV         : {CSV_FILE}")
print("====================================")

hands.close()