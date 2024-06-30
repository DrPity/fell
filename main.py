import os
import sys
import io
import numpy as np
import cv2
from rembg import remove, new_session
from PIL import Image
import shutil

BLUE = '\033[94m'
GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
NOCOLOR = '\033[0m'

DEBUG = True

def process_images(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            original_image_path = os.path.join(input_directory, filename)
            filesTemp = []
            try:
                # Remove the background from the image
                for name in ["u2net", "isnet-general-use"]:        
                    
                    # Create unique path for processed image masks
                    processed_image_path = os.path.join(output_directory, name + "-" + filename)
                    filesTemp.append(processed_image_path)
                    
                    # Remove the images background
                    remove_bg(original_image_path, processed_image_path, name)
                    
                    # Print filename and path
                    print(f"Processed {filename} successfully.")
                    print(f"Output {processed_image_path} successfully.")
                
                # merge the different mask into one coherent one    
                merge(filesTemp, output_directory, filename)
            
            except Exception as e:
                print(f"Failed to process {filename}. Error: {e}")

    print("All images have been processed.")

def merge(files, directory, filename):
    
    # Read the masks in grayscale
    mask1 = cv2.imread(files[0], cv2.IMREAD_GRAYSCALE)
    mask2 = cv2.imread(files[1], cv2.IMREAD_GRAYSCALE)

    # Threshold the masks to create binary masks
    _, binary_mask1 = cv2.threshold(mask1, 128, 255, cv2.THRESH_BINARY)
    _, binary_mask2 = cv2.threshold(mask2, 128, 255, cv2.THRESH_BINARY)

    # Combine the masks using bitwise AND
    result = cv2.bitwise_and(binary_mask1, binary_mask2)

    # Convert the result to a PIL image and save it
    result_image = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
    path_to_image = os.path.join(directory, filename)
    Image.fromarray(np.uint8(result_image)).save(path_to_image, 'PNG')
    copy_image(path_to_image, "./final")

def remove_bg(src_img_path, out_img_path, model):
    with open(src_img_path, 'rb') as img_file:
        img = img_file.read()

    model_name = model

    # only needed for SAM model
    input_points = np.array([[3000, 2000]])
    input_labels = np.array([1]
                            )
    session = new_session(model_name)
    processed_img = remove(img, session=session, only_mask=True, alpha_matting=True, alpha_matting_foreground_threshold=300,alpha_matting_background_threshold=5, alpha_matting_erode_size=10)
    
    # only need for SAM model
    # processed_img = remove(img, session=session, input_points=input_points, input_labels=input_labels)
    
    # save the removed background as a mask
    img_result = Image.open(io.BytesIO(processed_img))
    img_result = img_result.convert('RGB')
    img_result.save(out_img_path, 'JPEG')

def print_help():
    """
    Prints help information about how to use the script.
    """
    help_text = """
    Usage: python script.py <input_folder> <output_folder>
    Options:
    --h, --help        Show this help message and exit.

    This script processes images by removing the backg  round. Specify the directory
    containing the images and the directory where the processed images should be saved.
    """
    print(help_text)

def copy_image(source_path, destination_path):
    try:
        shutil.copy(source_path, destination_path)
        print(f"Image copied from {source_path} to {destination_path}")
    except Exception as e:
        print(f"Error copying image: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and (sys.argv[1] == '--h' or sys.argv[1] == '--help'):
        print_help()
        sys.exit(0)

    if len(sys.argv) != 3 and DEBUG == False:
        print( BLUE + "Usage:" + NOCOLOR + "python script.py <input_folder> <output_folder>")
        sys.exit(1)

    if DEBUG:
        process_images("./in/hdr.tag2", "./outFoo/hdr2")
    else:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        process_images(input_dir, output_dir)
    
