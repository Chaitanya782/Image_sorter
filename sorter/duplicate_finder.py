"""
Duplicate Finder Module
Identifies duplicate or visually similar images
"""

import os
import logging
import numpy as np
from PIL import Image
import imagehash
from collections import defaultdict


class DuplicateFinder:
    """Finds duplicate or visually similar images using perceptual hashing"""

    def __init__(self, hash_size=8, threshold=5):
        """
        Initialize the duplicate finder

        Args:
            hash_size (int): Size of the hash, larger values provide more detail
            threshold (int): Maximum hamming distance to consider as duplicate
        """
        self.hash_size = hash_size
        self.threshold = threshold
        self.image_hashes = {}
        self.logger = logging.getLogger('DuplicateFinder')

    def add_image(self, image_path):
        """
        Add an image to the duplicate finder

        Args:
            image_path (str): Path to the image file
        """
        try:
            # Calculate image hash
            img_hash = self._calculate_hash(image_path)
            if img_hash:
                self.image_hashes[image_path] = img_hash

        except Exception as e:
            self.logger.error(f"Error adding image {image_path}: {str(e)}")

    def find_duplicates(self):
        """
        Find duplicate images based on perceptual hashing

        Returns:
            list: Groups of duplicate images
        """
        if not self.image_hashes:
            return []

        # Group image paths by hash
        hash_groups = defaultdict(list)
        for img_path, img_hash in self.image_hashes.items():
            hash_groups[img_hash].append(img_path)

        # Find similar hashes
        duplicate_groups = []
        processed_hashes = set()

        for hash_val, paths in hash_groups.items():
            # Skip if already processed this hash
            if hash_val in processed_hashes:
                continue

            # If multiple paths with exactly the same hash, add as a duplicate group
            if len(paths) > 1:
                duplicate_groups.append(paths)
                processed_hashes.add(hash_val)
            else:
                # Find similar hashes within threshold
                similar_group = paths.copy()

                for other_hash, other_paths in hash_groups.items():
                    if other_hash in processed_hashes or other_hash == hash_val:
                        continue

                    # Compare hash distance
                    if self._hamming_distance(hash_val, other_hash) <= self.threshold:
                        similar_group.extend(other_paths)
                        processed_hashes.add(other_hash)

                if len(similar_group) > 1:
                    duplicate_groups.append(similar_group)

                processed_hashes.add(hash_val)

        return duplicate_groups

    def _calculate_hash(self, image_path):
        """Calculate perceptual hash for an image"""
        try:
            with Image.open(image_path) as img:
                # Convert to grayscale to focus on structure rather than color
                img = img.convert('L')

                # Calculate perceptual hash
                # We use a combination of different hash algorithms for better accuracy
                phash = imagehash.phash(img, hash_size=self.hash_size)
                dhash = imagehash.dhash(img, hash_size=self.hash_size)

                # Return combined hash as string
                return str(phash) + str(dhash)

        except Exception as e:
            self.logger.error(f"Error calculating hash for {image_path}: {str(e)}")
            return None

    def _hamming_distance(self, hash1, hash2):
        """Calculate hamming distance between two hashes"""
        # Count the number of differing bits
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))