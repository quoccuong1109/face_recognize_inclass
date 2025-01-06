from flask import request, jsonify
from app import app
import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

model_path = 'models/face_recognition_model.h5'

@app.route('/train_model', methods=['POST'])
def train_model_route():
    try:
        preprocess_images('data/raw_images', 'data/processed_images')
        images, labels = load_data('data/processed_images')
        images = images.reshape(-1, 128, 128, 1)

        # Đảm bảo rằng nhãn bắt đầu từ 0
        labels = np.array(labels) - 1

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

        model.save(model_path)
        return jsonify({'message': 'Đã huấn luyện và lưu mô hình thành công!'})
    except Exception as e:
        return jsonify({'message': f'Có lỗi xảy ra khi huấn luyện mô hình: {str(e)}'}), 500

def preprocess_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file).replace('\\', '/')
            print(f"Đang kiểm tra tệp: {file_path}")
            img = cv2.imread(file_path)
            if img is None:
                print(f"Không thể mở hoặc đọc tệp: {file_path}")
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (128, 128))
            output_path = os.path.join(output_folder, file).replace('\\', '/')
            cv2.imwrite(output_path, resized)

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