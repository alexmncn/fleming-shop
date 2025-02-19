import os, glob
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.import_to_db import update_articles, update_families, update_stocks
from app.services.pushover_alerts import send_alert

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
        filename = file.filename
        clean_filename, extension = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{clean_filename}_{timestamp}{extension}"
        file_path = os.path.join(UPLOAD_ROUTE, new_filename)
        
        username = get_jwt_identity()
        
        try:
            file.save(file_path)
            
            pattern = os.path.join(UPLOAD_ROUTE, f"{clean_filename}_*.dbf") # Get old file versions

            for file_ in glob.glob(pattern):
                file_name = os.path.basename(file_)

                if file_name != new_filename: # Remove all except the new one
                    os.remove(file_)
        except Exception as e:
            return jsonify(error='Error saving file'), 500
        
        status, info, resume = update_articles(new_filename, username)
        
        try:
            message = f'<b>Importación de Artículos:</b>\n {resume}'
            send_alert(message, 0)
        except:
            pass
        
        if status:
            return jsonify(message=info), 200
        else:
            return jsonify(error=info), 500
    
    return jsonify(error='Request error'), 400


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
        clean_filename, extension = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{clean_filename}_{timestamp}{extension}"
        file_path = os.path.join(UPLOAD_ROUTE, new_filename)
        
        try:
            file.save(file_path)
            
            pattern = os.path.join(UPLOAD_ROUTE, f"{clean_filename}_*.dbf") # Get old file versions

            for file_ in glob.glob(pattern):
                file_name = os.path.basename(file_)

                if file_name != new_filename: # Remove all except the new one
                    os.remove(file_)
        except Exception as e:
            return jsonify(error='Error saving file'), 500
        
        status, info, resume = update_families(new_filename)
        
        try:
            message = f'<b>Importación de Familias:</b>\n {resume}'
            send_alert(message, 0)
        except:
            pass
        
        if status:
            return jsonify(message=info), 200
        else:
            return jsonify(error=info), 500
    
    return jsonify(error='Request error'), 400



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
        clean_filename, extension = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{clean_filename}_{timestamp}{extension}"
        file_path = os.path.join(UPLOAD_ROUTE, new_filename)
        
        try:
            file.save(file_path)
            
            pattern = os.path.join(UPLOAD_ROUTE, f"{clean_filename}_*.dbf") # Get old file versions

            for file_ in glob.glob(pattern):
                file_name = os.path.basename(file_)

                if file_name != new_filename: # Remove all except the new one
                    os.remove(file_)
        except Exception as e:
            return jsonify(error='Error saving file'), 500
        
        status, info, resume = update_stocks(new_filename)
        
        try:
            message = f'<b>Importación de Stocks:</b>\n {resume}'
            send_alert(message, 0)
        except:
            pass
        
        if status:
            return jsonify(message=info), 200
        else:
            return jsonify(error=info), 500
    
    return jsonify(error='Request error'), 400
