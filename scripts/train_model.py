import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
import os

def create_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')  # Giả sử bạn có 10 học sinh
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def load_data(data_dir):
    # Thực hiện load và tiền xử lý dữ liệu ở đây
    pass

if __name__ == "__main__":
    model = create_model()
    train_data = load_data('data/processed_images')
    model.fit(train_data, epochs=10)
    model.save('models/face_recognition_model.h5')