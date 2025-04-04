"""
Image Sorter GUI Application
Desktop interface for the image sorter application
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import logging
from sorter.image_processor import ImageProcessor

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

class ImageSorterApp:
    """Main GUI application for the image sorter"""

    def __init__(self):
        """Initialize the GUI application"""
        self.root = ctk.CTk()
        self.root.title("AI Image Sorter")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)

        self.logger = logging.getLogger('GUI')

        # Variables
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.process_duplicates = tk.BooleanVar(value=True)
        self.process_faces = tk.BooleanVar(value=True)
        self.process_scenery = tk.BooleanVar(value=True)
        self.process_location = tk.BooleanVar(value=True)

        # Image processor
        self.processor = ImageProcessor()

        # Status tracking
        self.processing = False
        self.results = None

        # Setup UI
        self._setup_ui()

    def run(self):
        """Run the application main loop"""
        self.root.mainloop()

    def _setup_ui(self):
        """Set up the user interface"""
        # Main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="AI Image Sorter",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=10)

        # Directory selection frame
        dir_frame = ctk.CTkFrame(self.main_frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=10)

        # Input directory
        input_label = ctk.CTkLabel(dir_frame, text="Input Directory:")
        input_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")

        input_entry = ctk.CTkEntry(dir_frame, textvariable=self.input_dir, width=400)
        input_entry.grid(row=0, column=1, padx=5, pady=10)

        input_button = ctk.CTkButton(
            dir_frame,
            text="Browse...",
            command=self._browse_input_dir
        )
        input_button.grid(row=0, column=2, padx=5, pady=10)

        # Output directory
        output_label = ctk.CTkLabel(dir_frame, text="Output Directory:")
        output_label.grid(row=1, column=0, padx=5, pady=10, sticky="w")

        output_entry = ctk.CTkEntry(dir_frame, textvariable=self.output_dir, width=400)
        output_entry.grid(row=1, column=1, padx=5, pady=10)

        output_button = ctk.CTkButton(
            dir_frame,
            text="Browse...",
            command=self._browse_output_dir
        )
        output_button.grid(row=1, column=2, padx=5, pady=10)

        # Options frame
        options_frame = ctk.CTkFrame(self.main_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        options_label = ctk.CTkLabel(
            options_frame,
            text="Sorting Options:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        options_label.pack(anchor="w", padx=10, pady=5)

        # Checkboxes for sorting options
        face_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Sort Faces",
            variable=self.process_faces
        )
        face_checkbox.pack(anchor="w", padx=20, pady=5)

        location_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Sort by Location",
            variable=self.process_location
        )
        location_checkbox.pack(anchor="w", padx=20, pady=5)

        duplicate_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Detect Duplicates",
            variable=self.process_duplicates
        )
        duplicate_checkbox.pack(anchor="w", padx=20, pady=5)

        scenery_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Sort Scenery/Background",
            variable=self.process_scenery
        )
        scenery_checkbox.pack(anchor="w", padx=20, pady=5)

        # Progress frame
        progress_frame = ctk.CTkFrame(self.main_frame)
        progress_frame.pack(fill=tk.X, padx=10, pady=10)

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=10)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(progress_frame, text="Ready")
        self.status_label.pack(pady=5)

        # Results frame
        results_frame = ctk.CTkFrame(self.main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        results_label = ctk.CTkLabel(
            results_frame,
            text="Results:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        results_label.pack(anchor="w", padx=10, pady=5)

        # Create a scrollable frame for results
        self.results_scroll = ctk.CTkScrollableFrame(results_frame)
        self.results_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Button frame
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.process_button = ctk.CTkButton(
            button_frame,
            text="Start Processing",
            command=self._start_processing,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.process_button.pack(side=tk.RIGHT, padx=10)

        # Reset button
        reset_button = ctk.CTkButton(
            button_frame,
            text="Reset",
            command=self._reset,
            width=100,
            height=40
        )
        reset_button.pack(side=tk.RIGHT, padx=10)

    def _browse_input_dir(self):
        """Open file dialog to select input directory"""
        dir_path = filedialog.askdirectory(title="Select Input Directory")
        if dir_path:
            self.input_dir.set(dir_path)

    def _browse_output_dir(self):
        """Open file dialog to select output directory"""
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir.set(dir_path)

    def _start_processing(self):
        """Start the image processing in a separate thread"""
        if self.processing:
            return

        input_dir = self.input_dir.get().strip()
        output_dir = self.output_dir.get().strip()

        if not input_dir:
            messagebox.showerror("Error", "Please select an input directory.")
            return

        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return

        if not os.path.isdir(input_dir):
            messagebox.showerror("Error", "Input directory does not exist.")
            return

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Update UI state
        self.processing = True
        self.process_button.configure(state="disabled")
        self.status_label.configure(text="Processing...")
        self.progress_bar.set(0)

        # Clear previous results
        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        # Start processing in a separate thread
        thread = threading.Thread(target=self._process_images)
        thread.daemon = True
        thread.start()

    def _process_images(self):
        """Process images in a separate thread"""
        try:
            # Set up processor based on options
            config = {
                "process_faces": self.process_faces.get(),
                "process_location": self.process_location.get(),
                "process_duplicates": self.process_duplicates.get(),
                "process_scenery": self.process_scenery.get()
            }

            # Initialize a new processor for each run
            self.processor = ImageProcessor(config)

            # Process the directory
            self.results = self.processor.process_directory(
                self.input_dir.get(),
                self.output_dir.get()
            )

            # Update UI in the main thread
            self.root.after(0, self._update_results)

        except Exception as e:
            self.logger.error(f"Error processing images: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self._reset_ui)

    def _update_results(self):
        """Update the results display"""
        if not self.results:
            self.status_label.configure(text="No results found.")
            self._reset_ui()
            return

        # Update results display
        results_text = ""

        # Faces
        if self.process_faces.get() and 'faces' in self.results:
            face_label = ctk.CTkLabel(
                self.results_scroll,
                text=f"Found {len(self.results['faces'])} images with faces",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            face_label.pack(anchor="w", padx=5, pady=5)

        # Locations
        if self.process_location.get() and 'locations' in self.results:
            location_count = len(self.results['locations'])
            location_label = ctk.CTkLabel(
                self.results_scroll,
                text=f"Found {location_count} images with location data",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            location_label.pack(anchor="w", padx=5, pady=5)

        # Duplicates
        if self.process_duplicates.get() and 'duplicates' in self.results:
            duplicate_groups = len(self.results['duplicates'])
            total_duplicates = sum(len(group) for group in self.results['duplicates'])

            duplicate_label = ctk.CTkLabel(
                self.results_scroll,
                text=f"Found {total_duplicates} duplicate images in {duplicate_groups} groups",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            duplicate_label.pack(anchor="w", padx=5, pady=5)

        # Scenery
        if self.process_scenery.get() and 'scenery' in self.results:
            scenery_label = ctk.CTkLabel(
                self.results_scroll,
                text=f"Found {len(self.results['scenery'])} scenery/background images",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            scenery_label.pack(anchor="w", padx=5, pady=5)

        # Add view results button
        view_button = ctk.CTkButton(
            self.results_scroll,
            text="Open Output Directory",
            command=lambda: os.startfile(self.output_dir.get()) if os.name == 'nt' else os.system(f'open "{self.output_dir.get()}"')
        )
        view_button.pack(pady=10)

        # Update status
        self.status_label.configure(text="Processing completed successfully.")
        self.progress_bar.set(1)

        # Reset UI state
        self._reset_ui()

    def _reset_ui(self):
        """Reset the UI state after processing"""
        self.processing = False
        self.process_button.configure(state="normal")

    def _reset(self):
        """Reset the application to its initial state"""
        # Clear input fields
        self.input_dir.set("")
        self.output_dir.set("")

        # Reset progress
        self.progress_bar.set(0)
        self.status_label.configure(text="Ready")

        # Clear results
        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        # Reset state
        self.processing = False
        self.process_button.configure(state="normal")
        self.results = None