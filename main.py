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

models = ["u2net", "isnet-general-use"]

def process_images(input_directory, output_directory):

    output_directory_tmp = output_directory + "/tmp/"
    sessionU2net = new_session(models[0])
    sessionIsinet = new_session(models[1])

    if not os.path.exists(output_directory_tmp):
        os.makedirs(output_directory_tmp)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            original_image_path = os.path.join(input_directory, filename)
            filesTemp = []
            try:
                # Remove the background from the image
                for name in models:        
                    
                    # Create unique path for processed image masks
                    processed_image_path = os.path.join(output_directory_tmp, name + "-" + filename)
                    filesTemp.append(processed_image_path)
                    
                    if name == "u2net":
                        session = sessionU2net
                    elif name == "isnet-general-use":
                        session = sessionIsinet

                    
                    # Remove the images background
                    remove_bg(original_image_path, processed_image_path, session)
                    
                    # Print filename and path
                    print(f"Processed {filename} successfully.")
                    print(f"Output {processed_image_path} successfully.")
                
                # merge the different mask into one coherent one    
                merge(filesTemp, output_directory_tmp, filename, original_image_path, output_directory)
            
            except Exception as e:
                print(f"Failed to process {filename}. Error: {e}")

    print("All images have been processed.")

def merge(files, output_directory_tmp, filename, original_image_path, output_directory):
    
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
    path_to_image = os.path.join(output_directory_tmp, "merge_" + filename)
    Image.fromarray(np.uint8(result_image)).save(path_to_image, 'PNG')
    
    conture(path_to_image, original_image_path, output_directory_tmp, filename, output_directory)


def conture(path_to_image, original_image_path, output_directory_tmp, filename, output_directory):
    # Read the image
    img = cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE)
    
    # Apply threshold
    _, binary = cv2.threshold(img, 10, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled_contours = np.zeros_like(img)
    cv2.drawContours(filled_contours, contours, -1, (255), thickness=cv2.FILLED)
    
    # Apply Gaussian blur
    blur_size = 11
    blurred_image = cv2.GaussianBlur(filled_contours, (blur_size, blur_size), 0)
    
    # Create the processed image output path
    output_path = os.path.join(output_directory_tmp, filename)
    cv2.imwrite(output_path, blurred_image)
    print(f"Processed image saved as {output_path}") 

    # Copy images to the final folder
    organize_files(output_path, original_image_path, output_directory)

def remove_bg(src_img_path, out_img_path, session):
    with open(src_img_path, 'rb') as img_file:
        img = img_file.read()

    # only needed for SAM model
    input_points = np.array([[3000, 2000]])
    input_labels = np.array([1])
    
    processed_img = remove(img, post_process_mask=True, session=session, only_mask=True, alpha_matting=True, alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10, alpha_matting_erode_size=15)
    
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



def organize_files(mask_path, image_path, output_dir):
    def get_next_folder_name(base_path, prefix):
        # Get list of subfolders
        subfolders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f)) and f.startswith(prefix)]
        if not subfolders:
            return f"{prefix}_0-10"

        # Sort folders based on the numerical range they cover
        subfolders.sort(key=lambda x: int(x.split('_')[-1].split('-')[0]))

        # Check each folder for number of files
        for folder in subfolders:
            folder_path = os.path.join(base_path, folder)
            if len(os.listdir(folder_path)) < 10:
                return folder

        # If all existing folders are full, create a new one
        last_range = subfolders[-1].split('_')[-1]
        start = int(last_range.split('-')[-1]) + 1
        end = start + 9
        return f"{prefix}_{start}-{end}"

    def move_file(file_path, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        shutil.move(file_path, folder_path)

    images_dir = os.path.join(output_dir, 'images')
    masks_dir = os.path.join(output_dir, 'masks')

    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    if not os.path.exists(masks_dir):
        os.makedirs(masks_dir)

    # Organize the image
    image_folder_name = get_next_folder_name(images_dir, 'images')
    image_folder_path = os.path.join(images_dir, image_folder_name)
    move_file(image_path, image_folder_path)

    # Organize the mask
    mask_folder_name = get_next_folder_name(masks_dir, 'masks')
    mask_folder_path = os.path.join(masks_dir, mask_folder_name)
    move_file(mask_path, mask_folder_path)

# Example usage:
# organize_files('path/to/image.jpg', 'path/to/mask.jpg', 'path/to/output_dir')


if __name__ == '__main__':
    if len(sys.argv) > 1 and (sys.argv[1] == '--h' or sys.argv[1] == '--help'):
        print_help()
        sys.exit(0)

    if len(sys.argv) != 3 and DEBUG == False:
        print( BLUE + "Usage:" + NOCOLOR + "python script.py <input_folder> <output_folder>")
        sys.exit(1)

    if DEBUG:
        process_images("./in/hdr.tag3", "./out_tag3")
    else:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        process_images(input_dir, output_dir)
    
