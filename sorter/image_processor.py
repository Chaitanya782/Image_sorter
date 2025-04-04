"""
Image Processor Module
Core functionality for processing and categorizing images
"""

import os
import logging
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from .face_detector import FaceDetector
from .location_extractor import LocationExtractor
from .duplicate_finder import DuplicateFinder
from .scenery_classifier import SceneryClassifier


class ImageProcessor:
    """Main image processing class that orchestrates the sorting process"""

    def __init__(self, config=None):
        """Initialize the image processor with its components"""
        self.config = config or {}

        # Initialize the various detector components
        self.face_detector = FaceDetector()
        self.location_extractor = LocationExtractor()
        self.duplicate_finder = DuplicateFinder()
        self.scenery_classifier = SceneryClassifier()

        # Setup logging
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('ImageProcessor')

        # Results storage
        self.results = {
            'faces': [],
            'people': {},  # Dictionary to store images by person ID
            'locations': [],
            'duplicates': [],
            'scenery': []
        }

    def process_directory(self, directory_path, output_dir=None, max_workers=4):
        """Process all images in a directory and sort them"""
        self.logger.info(f"Processing directory: {directory_path}")

        # Ensure output directory exists
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            for category in self.results.keys():
                os.makedirs(os.path.join(output_dir, category), exist_ok=True)

        # Get all image files
        image_files = self._get_image_files(directory_path)
        self.logger.info(f"Found {len(image_files)} image files")

        # Process images in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(tqdm(executor.map(self.process_image, image_files),
                      total=len(image_files),
                      desc="Processing Images"))

        # Find duplicates (needs to be done after processing all images)
        if image_files:
            self.results['duplicates'] = self.duplicate_finder.find_duplicates()

        # Cluster faces into person groups (if faces were detected)
        if self.results['faces']:
            self.results['people'] = self.face_detector.cluster_faces()

        # Organize results
        if output_dir:
            self._organize_results(output_dir)

        return self.results

    def process_image(self, image_path):
        """Process a single image and classify it"""
        self.logger.debug(f"Processing image: {image_path}")

        try:
            # Check for faces
            has_face = self.face_detector.detect(image_path)
            if has_face:
                self.results['faces'].append(image_path)

            # Extract location data
            location = self.location_extractor.extract(image_path)
            if location:
                self.results['locations'].append((image_path, location))

            # Add to duplicate checker
            self.duplicate_finder.add_image(image_path)

            # Classify scenery
            is_scenery = self.scenery_classifier.classify(image_path)
            if is_scenery:
                self.results['scenery'].append(image_path)

        except Exception as e:
            self.logger.error(f"Error processing {image_path}: {str(e)}")

    def _get_image_files(self, directory):
        """Get all image files from a directory"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        image_files = []

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(os.path.join(root, file))

        return image_files

    def _organize_results(self, output_dir):
        """Organize the results by copying or moving files to category folders"""
        import shutil

        # Handle face images (general face category)
        for img_path in self.results['faces']:
            dest = os.path.join(output_dir, 'faces', os.path.basename(img_path))
            shutil.copy2(img_path, dest)

        # Handle person-specific images
        for person_id, images in self.results['people'].items():
            # Create a folder for each person
            person_dir = os.path.join(output_dir, 'people', f'person_{person_id}')
            os.makedirs(person_dir, exist_ok=True)

            for img_path in images:
                dest = os.path.join(person_dir, os.path.basename(img_path))
                shutil.copy2(img_path, dest)

        # Handle location images
        for img_path, location in self.results['locations']:
            # Create subfolder for location if needed
            location_dir = os.path.join(output_dir, 'locations', location)
            os.makedirs(location_dir, exist_ok=True)
            dest = os.path.join(location_dir, os.path.basename(img_path))
            shutil.copy2(img_path, dest)

        # Handle duplicate images
        for duplicate_group in self.results['duplicates']:
            # Create a group folder for each set of duplicates
            group_dir = os.path.join(output_dir, 'duplicates', f"group_{hash(tuple(duplicate_group))}")
            os.makedirs(group_dir, exist_ok=True)

            for img_path in duplicate_group:
                dest = os.path.join(group_dir, os.path.basename(img_path))
                shutil.copy2(img_path, dest)

        # Handle scenery images
        for img_path in self.results['scenery']:
            dest = os.path.join(output_dir, 'scenery', os.path.basename(img_path))
            shutil.copy2(img_path, dest)