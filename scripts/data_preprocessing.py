import os
import cv2
import numpy as np

def preprocess_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            img = cv2.imread(file_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (128, 128))
            output_path = os.path.join(output_folder, file)
            cv2.imwrite(output_path, resized)

input_folder = 'data/raw_images'
output_folder = 'data/processed_images'
preprocess_images(input_folder, output_folder)