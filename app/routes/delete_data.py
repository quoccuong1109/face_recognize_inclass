import os
import json
import shutil
from flask import Blueprint, jsonify, request

delete_data_bp = Blueprint('delete_data', __name__)

@delete_data_bp.route('/delete_data', methods=['POST'])
def delete_data():
    log_dir = 'log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file_path = os.path.join(log_dir, 'error_log.json')
    
    try:
        # Xác nhận trước khi xóa dữ liệu
        confirm = request.json.get('confirm', False)
        if not confirm:
            return jsonify({'message': 'Xác nhận xóa dữ liệu không thành công.'}), 400

        # Reset ID về 1
        with open('current_id.json', 'w') as file:
            json.dump({'current_id': 1}, file)

        # Xóa nội dung trong tệp students.json
        with open('students.json', 'w') as file:
            json.dump([], file)

        # Xóa tất cả các hình ảnh và thư mục con trong thư mục data
        data_folders = ['data/processed_images', 'data/raw_images']
        for folder in data_folders:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                os.makedirs(folder)  # Tạo lại thư mục rỗng sau khi xóa

        # Ghi log thành công
        with open(log_file_path, 'a') as log_file:
            log_entry = {'message': 'Đã xóa hết dữ liệu học sinh, reset ID về 1 và xóa các hình ảnh đã chụp thành công!'}
            json.dump(log_entry, log_file)
            log_file.write('\n')

        return jsonify({'message': 'Đã xóa hết dữ liệu học sinh, reset ID về 1 và xóa các hình ảnh đã chụp thành công!'})
    except Exception as e:
        # Ghi lỗi ra file log
        try:
            with open(log_file_path, 'a') as log_file:
                log_entry = {'error': str(e)}
                json.dump(log_entry, log_file)
                log_file.write('\n')
        except Exception as log_error:
            print(f"Không thể ghi lỗi vào file log: {log_error}")
        
        # Thông báo loại lỗi trên màn hình website
        return jsonify({'message': f'Có lỗi xảy ra khi xóa dữ liệu: {str(e)}'}), 500

if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(delete_data_bp)
    app.run(debug=True)