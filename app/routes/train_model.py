from flask import request, jsonify
from app import app
import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
import imgaug.augmenters as iaa
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

model_path = 'models/face_recognition_model.h5'

@app.route('/train_model', methods=['POST'])
def train_model_route():
    try:
        preprocess_images('data/raw_images', 'data/processed_images')
        augment_images('data/processed_images', 'data/augmented_images')
        images, labels = load_data('data/augmented_images')
        images = images.reshape(-1, 128, 128, 1)

        # Tách dữ liệu thành tập huấn luyện và tập kiểm tra
        X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

        print(f"Labels: {labels}")  # In ra để kiểm tra

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
        model.fit(X_train, y_train, epochs=10, validation_split=0.2)

        # Đánh giá mô hình với tập kiểm tra
        test_loss, test_accuracy = model.evaluate(X_test, y_test)
        print(f'Test accuracy: {test_accuracy}')

        # Kiểm tra các trường hợp dự đoán sai
        y_pred = model.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        incorrect_indices = np.where(y_pred_classes != y_test)[0]

        for i in incorrect_indices:
            print(f'Actual: {y_test[i]}, Predicted: {y_pred_classes[i]}')
            plt.imshow(X_test[i].reshape(128, 128), cmap='gray')
            plt.title(f'Actual: {y_test[i]}, Predicted: {y_pred_classes[i]}')
            plt.show()

        model.save(model_path)
        return jsonify({'message': 'Đã huấn luyện và lưu mô hình thành công!', 'test_accuracy': test_accuracy})
    except Exception as e:
        return jsonify({'message': f'Có lỗi xảy ra khi huấn luyện mô hình: {str(e)}'}), 500

def preprocess_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            img = cv2.imread(file_path)
            if img is None:
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (128, 128))
            output_path = os.path.join(output_folder, file)
            cv2.imwrite(output_path, resized)

def augment_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    seq = iaa.Sequential([
        iaa.Fliplr(0.5),  # Lật ngang hình ảnh với xác suất 50%
        iaa.Affine(rotate=(-20, 20)),  # Xoay hình ảnh trong khoảng -20 đến 20 độ
        iaa.Multiply((0.8, 1.2)),  # Thay đổi độ sáng của hình ảnh
        iaa.GaussianBlur(sigma=(0, 1.0))  # Làm mờ hình ảnh với độ mờ ngẫu nhiên
    ])

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            img = cv2.imread(file_path)
            if img is None:
                continue
            images_aug = seq(images=[img] * 5)  # Tạo 5 biến thể của mỗi hình ảnh
            for i, img_aug in enumerate(images_aug):
                output_path = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_aug_{i}.jpg")
                cv2.imwrite(output_path, img_aug)

def load_data(data_folder):
    images = []
    labels = []
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            file_path = os.path.join(root, file)
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            img = img / 255.0
            images.append(img)
            label = int(file.split('_')[0]) - 1  # Đảm bảo nhãn bắt đầu từ 0
            labels.append(label)
    return np.array(images), np.array(labels)