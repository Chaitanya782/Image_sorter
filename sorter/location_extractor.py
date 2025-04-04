"""
Location Extractor Module
Extracts location information from image EXIF data
"""

import os
import exifread
import logging
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


class LocationExtractor:
    """Extracts location data from image EXIF metadata"""

    def __init__(self):
        """Initialize the location extractor"""
        self.logger = logging.getLogger('LocationExtractor')

    def extract(self, image_path):
        """
        Extract location data from an image

        Args:
            image_path (str): Path to the image file

        Returns:
            str: Location name if available, otherwise None
        """
        try:
            # Extract GPS coordinates from EXIF
            gps_info = self._get_gps_info(image_path)

            if gps_info and 'latitude' in gps_info and 'longitude' in gps_info:
                # Format location as "lat,long"
                location = f"{gps_info['latitude']:.6f}_{gps_info['longitude']:.6f}"
                return location

            return None

        except Exception as e:
            self.logger.error(f"Error extracting location from {image_path}: {str(e)}")
            return None

    def _get_gps_info(self, image_path):
        """
        Get GPS information from image EXIF data

        Args:
            image_path (str): Path to the image file

        Returns:
            dict: GPS information including latitude and longitude, or None
        """
        try:
            with open(image_path, 'rb') as f:
                # Extract EXIF data
                exif_tags = exifread.process_file(f)

                # Check if image has GPS data
                if not any(tag for tag in exif_tags.keys() if tag.startswith('GPS')):
                    return None

                # Get GPS data
                gps_latitude = self._get_gps_coordinate(
                    exif_tags.get('GPS GPSLatitude'),
                    exif_tags.get('GPS GPSLatitudeRef')
                )

                gps_longitude = self._get_gps_coordinate(
                    exif_tags.get('GPS GPSLongitude'),
                    exif_tags.get('GPS GPSLongitudeRef')
                )

                if gps_latitude is not None and gps_longitude is not None:
                    return {
                        'latitude': gps_latitude,
                        'longitude': gps_longitude
                    }

            return None

        except Exception as e:
            self.logger.error(f"Error reading GPS info from {image_path}: {str(e)}")
            return None

    def _get_gps_coordinate(self, coordinate_tag, ref_tag):
        """Convert GPS coordinates from EXIF format to decimal degrees"""
        if coordinate_tag is None or ref_tag is None:
            return None

        try:
            # Convert the GPS coordinate from the EXIF tag
            coords = [float(x.num) / float(x.den) for x in coordinate_tag.values]

            # Calculate decimal degrees
            degrees = coords[0]
            minutes = coords[1] / 60.0
            seconds = coords[2] / 3600.0

            coordinate = degrees + minutes + seconds

            # If reference is South or West, make the coordinate negative
            if ref_tag.values in ['S', 'W']:
                coordinate = -coordinate

            return coordinate

        except Exception as e:
            self.logger.error(f"Error converting GPS coordinate: {str(e)}")
            return None

    def _get_location_name(self, latitude, longitude):
        """
        Get location name from coordinates (placeholder for geocoding service)

        In a full implementation, this would use a geocoding service like Google Maps,
        OpenStreetMap Nominatim, etc. to convert coordinates to a location name.
        """
        # This is a placeholder - in a real app you'd use a geocoding service
        return f"location_{latitude:.3f}_{longitude:.3f}"