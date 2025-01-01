import os
from flask import Blueprint, jsonify
from pathlib import Path

delete_data_bp = Blueprint('delete_data', __name__)

@delete_data_bp.route('/delete_data', methods=['POST'])
def delete_data():
    try:
        # Đường dẫn tới thư mục raw_images
        raw_images_path = Path('data/raw_images')
        
        # Xóa tất cả các tệp và thư mục con trong raw_images
        for item in raw_images_path.glob('*'):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                for sub_item in item.glob('*'):
                    if sub_item.is_file():
                        sub_item.unlink()
                    elif sub_item.is_dir():
                        shutil.rmtree(sub_item)
                item.rmdir()
        
        return jsonify({'message': 'Dữ liệu đã được xóa thành công!'})
    except Exception as e:
        return jsonify({'message': 'Có lỗi xảy ra khi xóa dữ liệu.', 'error': str(e)}), 500