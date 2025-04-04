"""
File Handler Utility
Handles file operations for the image sorter
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime


class FileHandler:
    """Utility class for file operations"""

    def __init__(self):
        """Initialize the file handler"""
        self.logger = logging.getLogger('FileHandler')

    def get_image_files(self, directory, recursive=True):
        """
        Get all image files from a directory

        Args:
            directory (str): Directory path to scan
            recursive (bool): Whether to scan subdirectories

        Returns:
            list: List of image file paths
        """
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        image_files = []

        try:
            if recursive:
                for root, _, files in os.walk(directory):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in image_extensions):
                            image_files.append(os.path.join(root, file))
            else:
                for file in os.listdir(directory):
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        image_files.append(os.path.join(directory, file))

            return image_files

        except Exception as e:
            self.logger.error(f"Error getting image files from {directory}: {str(e)}")
            return []

    def create_directory_structure(self, base_dir, categories):
        """
        Create directory structure for sorted images

        Args:
            base_dir (str): Base output directory
            categories (list): List of category names to create

        Returns:
            dict: Dictionary of category paths
        """
        category_paths = {}

        try:
            # Create base directory if it doesn't exist
            os.makedirs(base_dir, exist_ok=True)

            # Create a category directory for each category
            for category in categories:
                category_path = os.path.join(base_dir, category)
                os.makedirs(category_path, exist_ok=True)
                category_paths[category] = category_path

            return category_paths

        except Exception as e:
            self.logger.error(f"Error creating directory structure: {str(e)}")
            return {}

    def copy_file(self, source_path, destination_dir, rename=False):
        """
        Copy a file to a destination directory

        Args:
            source_path (str): Source file path
            destination_dir (str): Destination directory
            rename (bool): Whether to rename the file to avoid conflicts

        Returns:
            str: Path to the copied file, or None on error
        """
        try:
            # Ensure destination directory exists
            os.makedirs(destination_dir, exist_ok=True)

            # Get file name and extension
            file_name = os.path.basename(source_path)

            # Create destination path
            dest_path = os.path.join(destination_dir, file_name)

            # If rename is True and file already exists, add timestamp
            if rename and os.path.exists(dest_path):
                file_name_parts = os.path.splitext(file_name)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_file_name = f"{file_name_parts[0]}_{timestamp}{file_name_parts[1]}"
                dest_path = os.path.join(destination_dir, new_file_name)

            # Copy the file
            shutil.copy2(source_path, dest_path)
            return dest_path

        except Exception as e:
            self.logger.error(f"Error copying file {source_path}: {str(e)}")
            return None

    def move_file(self, source_path, destination_dir, rename=False):
        """
        Move a file to a destination directory

        Args:
            source_path (str): Source file path
            destination_dir (str): Destination directory
            rename (bool): Whether to rename the file to avoid conflicts

        Returns:
            str: Path to the moved file, or None on error
        """
        try:
            # Ensure destination directory exists
            os.makedirs(destination_dir, exist_ok=True)

            # Get file name and extension
            file_name = os.path.basename(source_path)

            # Create destination path
            dest_path = os.path.join(destination_dir, file_name)

            # If rename is True and file already exists, add timestamp
            if rename and os.path.exists(dest_path):
                file_name_parts = os.path.splitext(file_name)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_file_name = f"{file_name_parts[0]}_{timestamp}{file_name_parts[1]}"
                dest_path = os.path.join(destination_dir, new_file_name)

            # Move the file
            shutil.move(source_path, dest_path)
            return dest_path

        except Exception as e:
            self.logger.error(f"Error moving file {source_path}: {str(e)}")
            return None