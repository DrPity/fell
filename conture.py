import cv2
import numpy as np
import os
import sys
from PIL import Image
from psd_tools.api.psd_image import PSDImage
from psd_tools.api.layers import Group, Layer

def process_mask_image(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, "conture" + filename)
            img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
            _, binary = cv2.threshold(img, 10, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            filled_contours = np.zeros_like(img)
            cv2.drawContours(filled_contours, contours, -1, (255), thickness=cv2.FILLED)
            blur_size = 11
            blurred_image = cv2.GaussianBlur(filled_contours, (blur_size, blur_size), 0)
            cv2.imwrite(output_path, blurred_image)
            apply_mask_to_image(os.path.join("./in/hdr.tag2/" + filename), os.path.join("./final/" + filename), "./psd/")
            print(f"Processed image saved as {output_path}")

def apply_mask_to_image(image_path, mask, output_path):
    image = Image.open(image_path).convert("RGBA")
    mask_image =  Image.open(mask).convert("RGBA")

    # Ensure the mask and image are the same size
    if image.size != mask_image.size:
        mask_image = mask_image.resize(image.size, Image.ANTIALIAS)

    # Apply the mask to the image
    masked_image = Image.composite(image, Image.new("RGBA", image.size), mask_image)

    # Create PSD structure
    psd = PSDImage.new(mode='RGBA', size=image.size)

    # Add original image layer
    original_layer = Layer(name='Original Image', image=image)

    # Add mask layer
    mask_layer = Layer(name='Mask', image=mask_image.convert("RGBA"))

    # Add masked image layer
    masked_layer = Layer(name='Masked Image', image=masked_image)

    # Add layers to PSD
    psd.append(original_layer)
    psd.append(mask_layer)
    psd.append(masked_layer)

    # Save PSD
    psd.save(output_path)


if __name__ == "__main__":
    process_mask_image("/Users/themachine1337/Workspace/03_business/02_Fell/fell/final","/Users/themachine1337/Workspace/03_business/02_Fell/fell/finalout")
    # if len(sys.argv) != 3:
    #     print("Usage: python mask_processor.py <input_folder> <output_folder>")
    # else:
    #     input_folder = sys.argv[1]
    #     output_folder = sys.argv[2]
    #     os.makedirs(output_folder, exist_ok=True)
    #     process_mask_image(input_folder, output_folder)