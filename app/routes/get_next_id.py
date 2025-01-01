from flask import jsonify
from app import app
import os
import json

def get_next_id():
    current_id = 0
    if os.path.exists('current_id.json'):
        with open('current_id.json', 'r') as file:
            current_id = json.load(file).get('current_id', 0)
    next_id = current_id + 1
    with open('current_id.json', 'w') as file:
        json.dump({'current_id': next_id}, file)
    return next_id

@app.route('/get_next_id', methods=['GET'])
def get_next_id_route():
    next_id = get_next_id()
    return jsonify({'next_id': next_id})