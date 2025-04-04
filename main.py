#!/usr/bin/env python3
"""
Image Sorter - Main Application Entry Point
This script launches the image sorter application.
"""

import os
import sys
from gui.app import ImageSorterApp

def main():
    """Main entry point for the application"""
    app = ImageSorterApp()
    app.run()

if __name__ == "__main__":
    # Add the current directory to the path so we can import modules
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()