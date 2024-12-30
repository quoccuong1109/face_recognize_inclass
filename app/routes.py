from flask import request, jsonify, render_template, Response
from app import app
import os
import json
import cv2

model_path = 'models/face_recognition_model.h5'
students_file = 'students.json'

def get_next_id():
    current_id = 0
    if os.path.exists('current_id.json'):
        with open('current_id.json', 'r') as file:
            current_id = json.load(file).get('current_id', 0)
    next_id = current_id + 1
    with open('current_id.json', 'w') as file:
        json.dump({'current_id': next_id}, file)
    return next_id

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_face', methods=['GET', 'POST'])
def add_face():
    if request.method == 'POST':
        user_id = get_next_id()
        user_name = request.form['user_name']
        success = collect_face_data(user_id, user_name)
        if success:
            return jsonify({'message': 'Đã thêm dữ liệu khuôn mặt thành công!'})
        else:
            return jsonify({'message': 'Có lỗi xảy ra khi thêm dữ liệu khuôn mặt.'}), 500
    return render_template('add_face.html')

@app.route('/delete_data', methods=['POST'])
def delete_data():
    num_students = 0
    if os.path.exists(students_file):
        with open(students_file, 'r') as file:
            try:
                students = json.load(file)
                num_students = len(students)
            except json.JSONDecodeError:
                print("Lỗi: Không thể đọc tệp JSON")
                return jsonify({'message': 'Lỗi: Không thể đọc tệp JSON'}), 500

    for folder in ['data/raw_images', 'data/processed_images']:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    if os.path.exists(model_path):
        os.remove(model_path)

    if os.path.exists(students_file):
        os.remove(students_file)

    if os.path.exists('current_id.json'):
        os.remove('current_id.json')

    return jsonify({'message': f'Đã xóa dữ liệu của {num_students} học sinh và đặt lại ID thành công!'})

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.release()

@app.route('/get_next_id', methods=['GET'])
def get_next_id_route():
    next_id = get_next_id()
    return jsonify({'next_id': next_id})

def collect_face_data(user_id, user_name):
    try:
        # Tạo thư mục lưu trữ dữ liệu khuôn mặt nếu chưa tồn tại
        raw_images_dir = 'data/raw_images'
        user_dir = os.path.join(raw_images_dir, f'user_{user_id}_{user_name}')
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        # Mở camera
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            raise Exception("Không thể mở camera")

        print("Bắt đầu thu thập dữ liệu khuôn mặt. Nhấn 'q' để dừng.")

        count = 0
        while True:
            success, frame = camera.read()
            if not success:
                raise Exception("Không thể đọc khung hình từ camera")

            # Phát hiện khuôn mặt
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(frame, 1.1, 4)

            for (x, y, w, h) in faces:
                # Vẽ hình chữ nhật quanh khuôn mặt
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Lưu khung hình chứa khuôn mặt vào thư mục
                face_img = frame[y:y+h, x:x+w]
                img_path = os.path.join(user_dir, f'face_{count}.jpg')
                cv2.imwrite(img_path, face_img)
                count += 1

            # Hiển thị khung hình
            cv2.imshow('Thu thập dữ liệu khuôn mặt', frame)

            # Nhấn 'q' để dừng
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Giải phóng camera và đóng tất cả các cửa sổ
        camera.release()
        cv2.destroyAllWindows()

        print(f"Đã thu thập {count} hình ảnh khuôn mặt cho người dùng {user_name} (ID: {user_id})")
        return True

    except Exception as e:
        print(f"Lỗi: {e}")
        return False