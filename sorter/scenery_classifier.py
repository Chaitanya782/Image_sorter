"""
Scenery Classifier Module
Classifies images as scenery/background vs other types of images
"""

import os
import logging
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import cv2

class SceneryClassifier:
    """Classifies images as scenery/landscape/background using a pre-trained model"""

    # Categories that are typically associated with scenery/background
    SCENERY_CATEGORIES = [
        'seashore', 'coast', 'beach', 'lakeside', 'lakeshore', 'mountain',
        'valley', 'volcano', 'alp', 'cliff', 'promontory', 'volcano',
        'coral reef', 'sandbar', 'forest', 'rainforest', 'jungle', 'woodland',
        'desert', 'plain', 'prairie', 'mesa', 'canyon', 'sky', 'natural_elevation',
        'waterfall', 'glacier', 'river', 'lake', 'pond', 'tree', 'field',
        'sunset', 'sunrise', 'horizon', 'landscape'
    ]

    def __init__(self, confidence_threshold=0.4):
        """
        Initialize the scenery classifier with a pre-trained model

        Args:
            confidence_threshold (float): Minimum confidence to classify as scenery
        """
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger('SceneryClassifier')

        # Initialize model lazily (only when needed)
        self.model = None

    def _load_model(self):
        """Load the pre-trained model if not already loaded"""
        if self.model is None:
            try:
                # Load MobileNetV2 pre-trained on ImageNet
                # We use MobileNetV2 because it's relatively small and fast
                self.model = MobileNetV2(weights='imagenet', include_top=True)
                self.logger.info("Loaded MobileNetV2 model")
            except Exception as e:
                self.logger.error(f"Error loading model: {str(e)}")
                raise

    def classify(self, image_path):
        """
        Classify an image as scenery or not

        Args:
            image_path (str): Path to the image file

        Returns:
            bool: True if the image is classified as scenery, False otherwise
        """
        try:
            # Load model on first use
            if self.model is None:
                self._load_model()

            # Load and preprocess the image
            img = image.load_img(image_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)

            # Make prediction
            predictions = self.model.predict(img_array)
            decoded_predictions = decode_predictions(predictions, top=5)[0]

            # Check if any of the top predictions is in our scenery categories
            for _, label, confidence in decoded_predictions:
                if confidence >= self.confidence_threshold:
                    # Check if label is in our scenery categories
                    if any(scenery_cat in label.lower() for scenery_cat in self.SCENERY_CATEGORIES):
                        return True

                    # Additional check: if it's a scene rather than an object
                    if not self._is_likely_object_focused(image_path):
                        return True

            return False

        except Exception as e:
            self.logger.error(f"Error classifying {image_path}: {str(e)}")
            return False

    def _is_likely_object_focused(self, image_path):
        """
        Check if the image likely has a main object in focus (not scenery)
        This is a simple heuristic based on edge detection

        Args:
            image_path (str): Path to the image file

        Returns:
            bool: True if the image likely has a main object in focus
        """
        try:
            # Load image and convert to grayscale
            img = cv2.imread(image_path)
            if img is None:
                return False

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur and Canny edge detection
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)

            # Count number of edge pixels
            edge_pixels = np.count_nonzero(edges)
            total_pixels = edges.shape[0] * edges.shape[1]
            edge_ratio = edge_pixels / total_pixels

            # If edge ratio is high, it's likely to have distinct objects
            # This is a simplification - more sophisticated methods would be better
            return edge_ratio > 0.05

        except Exception as e:
            self.logger.error(f"Error analyzing edges in {image_path}: {str(e)}")
            return False