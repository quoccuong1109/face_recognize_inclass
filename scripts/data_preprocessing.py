import cv2
import os

def detect_and_crop_faces(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    for filename in os.listdir(input_dir):
        if filename.endswith('.jpg'):
            image_path = os.path.join(input_dir, filename)
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            for (x, y, w, h) in faces:
                face = image[y:y+h, x:x+w]
                face_path = os.path.join(output_dir, filename)
                cv2.imwrite(face_path, face)

if __name__ == "__main__":
    detect_and_crop_faces('data/raw_images', 'data/processed_images')