"""
sign_predictor.py

Loads the trained SignSense AI model and predicts
ASL alphabet letters from MediaPipe landmarks.
"""

import os
import pickle

import numpy as np


class SignPredictor:
    """
    Predict ASL alphabet letters using the trained model.
    """

    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        model_path = os.path.join(
            base_dir,
            "..",
            "models",
            "asl_model.pkl",
        )

        encoder_path = os.path.join(
            base_dir,
            "..",
            "models",
            "label_encoder.pkl",
        )

        with open(model_path, "rb") as file:
            self.model = pickle.load(file)

        with open(encoder_path, "rb") as file:
            self.encoder = pickle.load(file)

    def predict(self, landmarks):
        """
        Predict ASL alphabet.

        Args:
            landmarks:
                Output from HandDetector.get_landmarks()

        Returns:
            (prediction, confidence)
        """

        if not landmarks:
            return "No Hand", 0.0

        # ------------------------------------
        # Build feature vector
        # ------------------------------------
        features = []

        for landmark in landmarks:
            features.append(landmark["x"])
            features.append(landmark["y"])
            features.append(landmark["z"])

        features = np.array(features, dtype=np.float32).reshape(1, -1)

        # ------------------------------------
        # Prediction
        # ------------------------------------
        prediction = self.model.predict(features)[0]

        probabilities = self.model.predict_proba(features)[0]

        confidence = float(np.max(probabilities))

        label = self.encoder.inverse_transform([prediction])[0]

        return label, confidence