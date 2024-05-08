import fileinput
import os
import subprocess
from backgroundremover.bg import remove


def process_images():

    input_directory = './in'
    output_directory = './out'

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            original_image_path = os.path.join(input_directory, filename)
            processed_image_path = os.path.join(output_directory, filename)

            try:
                # Remove the background from the image
                remove_bg(original_image_path,processed_image_path)
                print(f"Processed {filename} successfully.")
            except Exception as e:
                print(f"Failed to process {filename}. Error: {e}")

    print("All images have been processed.")


def remove_bg(src_img_path, out_img_path):
    model_choices = ["u2net", "u2net_human_seg", "u2netp"]
    f = open(src_img_path, "rb")
    data = f.read()
    img = remove(data, model_name=model_choices[0],
                 alpha_matting=True,
                #  alpha_matting_foreground_threshold=240,
                #  alpha_matting_background_threshold=10,
                #  alpha_matting_erode_structure_size=10,
                 alpha_matting_foreground_threshold=240,
                 alpha_matting_background_threshold=12,
                 alpha_matting_erode_structure_size=10,
                 alpha_matting_base_size=1000)
    f.close()
    f = open(out_img_path, "wb")
    f.write(img)
    f.close()


if __name__ == '__main__':
    process_images()