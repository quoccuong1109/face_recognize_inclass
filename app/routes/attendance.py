import os
import json
from flask import request, jsonify, render_template, Response
import cv2
import numpy as np
import joblib
from app import app

model_path = 'models/face_recognition_model.pkl'
students_file = 'students.json'

# Kiểm tra nếu model tồn tại
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    model = None

# Đọc dữ liệu học sinh từ tệp JSON
students_data = []
if os.path.exists(students_file):
    with open(students_file, 'r', encoding='utf-8') as file:
        try:
            students_data = json.load(file)
        except json.JSONDecodeError:
            students_data = []

@app.route('/diemdanh_tudong')
def diemdanh_tudong():
    return render_template('diemdanh_tudong.html')

@app.route('/attendance_feed')
def attendance_feed():
    return Response(gen_attendance_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_attendance_frames():
    if not model:
        raise Exception("Model chưa được huấn luyện. Vui lòng huấn luyện mô hình trước khi điểm danh.")

    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        names = []
        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (128, 128))
            face_img = face_img / 255.0
            face_img = face_img.reshape(1, -1)
            
            predicted_id = model.predict(face_img)[0]
            predicted_prob = model.predict_proba(face_img)[0]
            confidence = np.max(predicted_prob) * 100  # Tính toán tỷ lệ chính xác
            name = next((student['name'] for student in students_data if student['id'] == predicted_id), "Unknown")
            names.append(name)
            
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, f'{name} ({confidence:.2f}%)', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    camera.release()

@app.route('/get_attendance', methods=['GET'])
def get_attendance():
    return jsonify({'students': students_data})