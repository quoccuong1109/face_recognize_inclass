import os
import json
import shutil
from flask import Blueprint, jsonify, request

delete_data_bp = Blueprint('delete_data', __name__)

@delete_data_bp.route('/delete_data', methods=['POST'])
def delete_data():
    try:
        # Xóa model hiện tại
        model_path = 'models/face_recognition_model.h5'
        if os.path.exists(model_path):
            os.remove(model_path)
        else:
            print(f"Model path {model_path} does not exist.")

        # Xóa dữ liệu ảnh hiện có
        data_folders = ['data/processed_images', 'data/raw_images']
        for folder in data_folders:
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder):
                    for dir in dirs:
                        os.chmod(os.path.join(root, dir), 0o777)
                    for file in files:
                        os.chmod(os.path.join(root, file), 0o777)
                shutil.rmtree(folder)
                os.makedirs(folder)  # Tạo lại thư mục rỗng sau khi xóa
            else:
                print(f"Data folder {folder} does not exist.")

        # Reset ID về 1
        with open('current_id.json', 'w', encoding='utf-8') as file:
            json.dump({'current_id': 1}, file, ensure_ascii=False)

        # Xóa nội dung trong tệp students.json
        with open('students.json', 'w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False)

        return jsonify({'message': 'Đã xóa hết dữ liệu học sinh, reset ID về 1 và xóa các hình ảnh đã chụp thành công!'})
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'message': f'Có lỗi xảy ra khi xóa dữ liệu: {str(e)}'}), 500

if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(delete_data_bp)
    app.run(debug=True)