"""
Face Detector Module (OpenCV Version)
Detects faces in images using OpenCV's Haar Cascades
"""

import os
import cv2
import logging
import numpy as np

class FaceDetector:
    """Detects faces in images using OpenCV"""

    def __init__(self, min_face_size=30, scale_factor=1.1, min_neighbors=5):
        """Initialize the face detector"""
        self.min_face_size = min_face_size
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.logger = logging.getLogger('FaceDetector')

        # Load the pre-trained face detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # For face clustering (simplified version of face recognition)
        self.face_images = []
        self.image_paths = []

    def detect(self, image_path):
        """
        Detect faces in an image

        Args:
            image_path (str): Path to the image file

        Returns:
            bool: True if at least one face is detected, False otherwise
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                self.logger.warning(f"Could not load image: {image_path}")
                return False

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=(self.min_face_size, self.min_face_size)
            )

            # Save face images for clustering (if any faces detected)
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    # Extract the face ROI
                    face_roi = gray[y:y+h, x:x+w]
                    # Resize to a standard size for comparison
                    face_roi = cv2.resize(face_roi, (100, 100))
                    # Store for later clustering
                    self.face_images.append(face_roi)
                    self.image_paths.append(image_path)

            return len(faces) > 0

        except Exception as e:
            self.logger.error(f"Error detecting faces in {image_path}: {str(e)}")
            return False

    def cluster_faces(self, num_clusters=5):
        """
        Group similar faces using basic clustering

        Args:
            num_clusters (int): Number of person clusters to create

        Returns:
            dict: Dictionary mapping person_id to list of image paths
        """
        if not self.face_images:
            return {}

        try:
            # Convert face images to feature vectors (flattened images)
            features = np.array([img.flatten() for img in self.face_images])

            # Normalize features
            features = features.astype(np.float32)
            means = np.mean(features, axis=0)
            stds = np.std(features, axis=0)
            stds[stds == 0] = 1  # Avoid division by zero
            features = (features - means) / stds

            # Perform K-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            _, labels, _ = cv2.kmeans(features, num_clusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

            # Group images by cluster
            people = {}
            for i, label in enumerate(labels.flatten()):
                person_id = int(label) + 1  # Start person IDs from 1
                if person_id not in people:
                    people[person_id] = []

                # Add image to person's cluster if not already there
                img_path = self.image_paths[i]
                if img_path not in people[person_id]:
                    people[person_id].append(img_path)

            return people

        except Exception as e:
            self.logger.error(f"Error clustering faces: {str(e)}")
            return {}