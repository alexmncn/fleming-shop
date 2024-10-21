import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.services.import_to_db import update_articles, update_families, update_stocks

from app.config import UPLOAD_ROUTE

os.makedirs(UPLOAD_ROUTE, exist_ok=True)

load_data_bp = Blueprint('load_data', __name__)


@load_data_bp.route('/upload/articles', methods=['POST'])
@jwt_required()
def upload_articles_():
    if 'file' not in request.files:
        return jsonify(error='No file part in request'), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify(error='No file selected to upload'), 400

    if file:
        print(f'Archivo recibido: {file.filename}')
        filename = file.filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
        file_path = os.path.join(UPLOAD_ROUTE, new_filename)
        file.save(file_path)
        
        
        update_articles(new_filename)
        
        return jsonify(message='OK'), 200
    
    return jsonify(error='Request error')


@load_data_bp.route('/upload/families', methods=['POST'])
@jwt_required()
def upload_families_():
    if 'file' not in request.files:
        return jsonify(error='No file part in request'), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify(error='No file selected to upload'), 400

    if file:
        filename = file.filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
        file_path = os.path.join(UPLOAD_ROUTE, new_filename)
        file.save(file_path)
        
        update_families(new_filename)
        
        return jsonify(message='OK'), 200
    
    return jsonify(error='Request error')


@load_data_bp.route('/upload/stocks', methods=['POST'])
@jwt_required()
def upload_stocks_():
    if 'file' not in request.files:
        return jsonify(error='No file part in request'), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify(error='No file selected to upload'), 400

    if file:
        filename = file.filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
        file_path = os.path.join(UPLOAD_ROUTE, new_filename)
        file.save(file_path)
        
        update_stocks(new_filename)
        
        return jsonify(message='OK'), 200
    
    return jsonify(error='Request error')