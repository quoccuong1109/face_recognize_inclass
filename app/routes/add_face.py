from flask import request, jsonify, render_template
from app import app
import os
import json
import cv2

def get_next_id():
    current_id = 0
    if os.path.exists('current_id.json'):
        with open('current_id.json', 'r') as file:
            current_id = json.load(file).get('current_id', 0)
    next_id = current_id + 1
    with open('current_id.json', 'w') as file:
        json.dump({'current_id': next_id}, file)
    return next_id

@app.route('/add_face', methods=['GET', 'POST'])
def add_face():
    if request.method == 'POST':
        user_id = get_next_id()
        user_name = request.form['user_name']
        success = collect_face_data(user_id, user_name)
        if success:
            return jsonify({'message': f'Đã thêm dữ liệu khuôn mặt thành công cho người dùng {user_name} (ID: {user_id})!'})
        else:
            return jsonify({'message': 'Có lỗi xảy ra khi thêm dữ liệu khuôn mặt.'}), 500
    return render_template('add_face.html')

def collect_face_data(user_id, user_name):
    try:
        raw_images_dir = 'data/raw_images'
        user_dir = os.path.join(raw_images_dir, f'user_{user_id}_{user_name}')
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            raise Exception("Không thể mở camera")

        count = 0
        while count < 10:  # Chụp 10 tấm ảnh
            success, frame = camera.read()
            if not success:
                raise Exception("Không thể đọc khung hình từ camera")

            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(frame, 1.1, 4)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                face_img = frame[y:y+h, x:x+w]
                img_path = os.path.join(user_dir, f'{user_id}_face_{count}.jpg')
                cv2.imwrite(img_path, face_img)
                count += 1

            cv2.imshow('Thu thập dữ liệu khuôn mặt', frame)
            cv2.waitKey(1000)  # Chờ 1 giây giữa các lần chụp

        camera.release()
        cv2.destroyAllWindows()
        
        # Log the new user to students.json
        students_data = []
        if os.path.exists('students.json'):
            with open('students.json', 'r') as file:
                try:
                    students_data = json.load(file)
                except json.JSONDecodeError:
                    pass
        
        students_data.append({'id': user_id, 'name': user_name})
        
        with open('students.json', 'w') as file:
            json.dump(students_data, file)

        print(f"Đã thu thập {count} hình ảnh khuôn mặt cho người dùng {user_name} (ID: {user_id})")
        
        return True

    except Exception as e:
        print(f"Lỗi: {e}")
        return False