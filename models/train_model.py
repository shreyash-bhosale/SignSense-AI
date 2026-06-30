"""
train_model.py

Train a Random Forest classifier for SignSense AI.

This script:
1. Loads dataset.csv
2. Encodes labels (A-Z)
3. Splits into train/test sets
4. Trains a Random Forest model
5. Evaluates the model
6. Saves the trained model
"""

import os
import pickle
import time

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


# ==========================================================
# Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "asl_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "label_encoder.pkl")


# ==========================================================
# Main
# ==========================================================

def main():

    print("=" * 60)
    print("SignSense AI - Model Training")
    print("=" * 60)

    # ------------------------------------------------------
    # Load Dataset
    # ------------------------------------------------------

    print("\nLoading dataset...")

    dataset = pd.read_csv(DATASET_PATH)

    print(f"Samples : {len(dataset)}")
    print(f"Columns : {len(dataset.columns)}")

    # ------------------------------------------------------
    # Features / Labels
    # ------------------------------------------------------

    X = dataset.drop("label", axis=1)

    y = dataset["label"]

    # ------------------------------------------------------
    # Encode Labels
    # ------------------------------------------------------

    print("\nEncoding labels...")

    label_encoder = LabelEncoder()

    y_encoded = label_encoder.fit_transform(y)

    print("Classes:")
    print(label_encoder.classes_)

    # ------------------------------------------------------
    # Train/Test Split
    # ------------------------------------------------------

    print("\nSplitting dataset...")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded,
    )

    print(f"Training samples : {len(X_train)}")
    print(f"Testing samples  : {len(X_test)}")

    # ------------------------------------------------------
    # Train Model
    # ------------------------------------------------------

    print("\nTraining Random Forest...")

    start = time.time()

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    end = time.time()

    print(f"Training completed in {end-start:.2f} seconds.")

    # ------------------------------------------------------
    # Prediction
    # ------------------------------------------------------

    print("\nEvaluating model...")

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print(f"\nAccuracy: {accuracy*100:.2f}%")

    print("\nClassification Report:\n")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=label_encoder.classes_,
        )
    )

    print("\nConfusion Matrix:\n")

    print(confusion_matrix(y_test, predictions))

    # ------------------------------------------------------
    # Save Model
    # ------------------------------------------------------

    print("\nSaving model...")

    with open(MODEL_PATH, "wb") as file:
        pickle.dump(model, file)

    with open(ENCODER_PATH, "wb") as file:
        pickle.dump(label_encoder, file)

    print("\nModel saved successfully!")

    print(MODEL_PATH)

    print(ENCODER_PATH)

    print("\nTraining Complete!")

    print("=" * 60)


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    main()