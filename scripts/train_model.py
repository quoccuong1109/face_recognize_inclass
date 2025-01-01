import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

def load_data(data_folder):
    images = []
    labels = []
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            file_path = os.path.join(root, file)
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            img = img / 255.0
            images.append(img)
            label = int(file.split('_')[0])
            labels.append(label)
    return np.array(images), np.array(labels)

data_folder = 'data/processed_images'
images, labels = load_data(data_folder)
images = images.reshape(-1, 128, 128, 1)

model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 1)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(len(set(labels)), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(images, labels, epochs=10, validation_split=0.2)

model.save('models/face_recognition_model.h5')