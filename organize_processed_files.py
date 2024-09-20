import os
import shutil
import re

def extract_serial_number(filename):
    match = re.search(r'(\d+)', filename)
    return match.group(1) if match else None

def find_matching_folders(output_root, serial_number):
    matching_folders = []
    for root, dirs, files in os.walk(output_root):
        if serial_number in os.path.basename(root):
            matching_folders.append(root)
    return matching_folders

def process_files(input_folders, output_root):
    total_files = 0
    copied_files = 0

    for input_folder in input_folders:
        for root, dirs, files in os.walk(input_folder):
            for filename in files:
                if filename.endswith(('.jpg', '.psd')):
                    total_files += 1
                    file_path = os.path.join(root, filename)
                    serial_number = extract_serial_number(filename)
                    if serial_number:
                        print(f"Found file with serial number {serial_number}: {file_path}")
                        matching_folders = find_matching_folders(output_root, serial_number)
                        if matching_folders:
                            print(f"  Matching folders found: {', '.join(matching_folders)}")
                            for matching_folder in matching_folders:
                                src_path = file_path
                                dst_path = os.path.join(matching_folder, filename)
                                shutil.copy2(src_path, dst_path)
                                copied_files += 1
                                print(f"    Copied to: {dst_path}")
                        else:
                            print(f"  No matching folders found for serial number {serial_number}")
                    else:
                        print(f"No serial number found in filename: {filename}")
    
    print(f"\nProcess completed.")
    print(f"Total files processed: {total_files}")
    print(f"Files copied: {copied_files}")

# Usage
input_folders = ['tmp/out/images']
output_folder = 'tmp/all_products'
process_files(input_folders, output_folder)