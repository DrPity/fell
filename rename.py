import os
import shutil
import re

def organize_photos(root_dir, extension=""):
    # Dictionary to store photos by serial number
    serial_photos = {}

    # Walk through all directories and files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        serial_number = os.path.basename(dirpath)
        
        # Check if the folder name is a valid serial number (assuming it's numeric)
        if not serial_number.isdigit():
            continue

        for filename in filenames:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                # If the photo is already named with the serial number, skip it
                if filename.startswith(serial_number):
                    continue
                
                # Add the photo to the dictionary
                if serial_number not in serial_photos:
                    serial_photos[serial_number] = []
                serial_photos[serial_number].append(os.path.join(dirpath, filename))

    # Rename and move photos
    for serial_number, photos in serial_photos.items():
        for i, photo_path in enumerate(photos, 1):
            # Get the file extension
            _, file_extension = os.path.splitext(photo_path)
            
            # Create the new filename
            new_filename = f"{serial_number}_{i:03d}{extension}{file_extension}"
            
            # Create the new path (in the same directory as the original file)
            new_path = os.path.join(os.path.dirname(photo_path), new_filename)
            
            # Rename and move the file
            shutil.move(photo_path, new_path)
            print(f"Moved: {photo_path} -> {new_path}")

# Usage
root_directory = "./m/"
additional_extension = "_m"  # Change this to your desired additional extension
organize_photos(root_directory, additional_extension)