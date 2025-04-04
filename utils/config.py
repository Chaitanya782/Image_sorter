"""
Configuration Module
Handles configuration settings for the image sorter
"""

import os
import json
import logging
from pathlib import Path


class Config:
    """Configuration manager for the image sorter"""

    DEFAULT_CONFIG = {
        "face_detection": {
            "enabled": True,
            "min_face_size": 20,
            "confidence_threshold": 0.6
        },
        "location": {
            "enabled": True
        },
        "duplicates": {
            "enabled": True,
            "hash_size": 8,
            "threshold": 5
        },
        "scenery": {
            "enabled": True,
            "confidence_threshold": 0.4
        },
        "general": {
            "max_workers": 4,
            "copy_mode": True  # True for copy, False for move
        }
    }

    def __init__(self, config_path=None):
        """
        Initialize the configuration manager

        Args:
            config_path (str, optional): Path to the configuration file
        """
        self.logger = logging.getLogger('Config')

        # Set default config path if not provided
        if config_path is None:
            # Get user's home directory
            home_dir = str(Path.home())
            config_dir = os.path.join(home_dir, '.image_sorter')
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, 'config.json')

        self.config_path = config_path
        self.config = self.load()

    def load(self):
        """
        Load configuration from file

        Returns:
            dict: Configuration dictionary
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)

                # Merge with default config to ensure all keys exist
                merged_config = self.DEFAULT_CONFIG.copy()
                self._merge_dict(merged_config, loaded_config)
                return merged_config
            else:
                # If config file doesn't exist, create it with default values
                self.save(self.DEFAULT_CONFIG)
                return self.DEFAULT_CONFIG.copy()

        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return self.DEFAULT_CONFIG.copy()

    def save(self, config=None):
        """
        Save configuration to file

        Args:
            config (dict, optional): Configuration to save, uses current config if None

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use provided config or current config
            config_to_save = config if config is not None else self.config

            with open(self.config_path, 'w') as f:
                json.dump(config_to_save, f, indent=4)

            return True

        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")
            return False

    def get(self, key, default=None):
        """
        Get a configuration value

        Args:
            key (str): Configuration key (can use dot notation, e.g., 'face_detection.enabled')
            default: Default value if key doesn't exist

        Returns:
            The configuration value or default
        """
        try:
            # Handle dot notation (e.g., 'face_detection.enabled')
            if '.' in key:
                parts = key.split('.')
                value = self.config
                for part in parts:
                    value = value.get(part)
                    if value is None:
                        return default
                return value
            else:
                return self.config.get(key, default)

        except Exception as e:
            self.logger.error(f"Error getting config value for {key}: {str(e)}")
            return default

    def set(self, key, value):
        """
        Set a configuration value

        Args:
            key (str): Configuration key (can use dot notation, e.g., 'face_detection.enabled')
            value: Value to set

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Handle dot notation (e.g., 'face_detection.enabled')
            if '.' in key:
                parts = key.split('.')
                target = self.config
                for part in parts[:-1]:
                    if part not in target:
                        target[part] = {}
                    target = target[part]
                target[parts[-1]] = value
            else:
                self.config[key] = value

            # Save the updated config
            return self.save()

        except Exception as e:
            self.logger.error(f"Error setting config value for {key}: {str(e)}")
            return False

    def _merge_dict(self, target, source):
        """
        Recursively merge source dictionary into target dictionary

        Args:
            target (dict): Target dictionary to merge into
            source (dict): Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dict(target[key], value)
            else:
                target[key] = value