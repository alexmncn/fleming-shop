import os, glob
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.import_to_db import update_articles, update_families, update_stocks, update_cierre, update_movimt, update_hticketl
from app.services.pushover_alerts import send_alert

from app.config import UPLOAD_ROUTE

os.makedirs(UPLOAD_ROUTE, exist_ok=True)

load_data_bp = Blueprint('load_data', __name__)


@load_data_bp.route('/upload/<string:filetype>', methods=['POST'])
@jwt_required()
def upload_file(filetype):
    if 'file' not in request.files:
        return jsonify(error='No file part in request'), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify(error='No file selected to upload'), 400

    valid_types = {
        'articles': update_articles,
        'families': update_families,
        'stocks': update_stocks,
        'cierre': update_cierre,
        'movimt': update_movimt,
        'hticketl': update_hticketl,
    }

    if filetype not in valid_types:
        return jsonify(error='Invalid file type'), 400

    filename = file.filename
    clean_filename, extension = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{clean_filename}_{timestamp}{extension}"
    file_path = os.path.join(UPLOAD_ROUTE, new_filename)

    try:
        file.save(file_path)

        pattern = os.path.join(UPLOAD_ROUTE, f"{clean_filename}_*.dbf")
        for file_ in glob.glob(pattern):
            if os.path.basename(file_) != new_filename:
                os.remove(file_)
    except Exception:
        return jsonify(error='Error saving file'), 500

    update_func = valid_types[filetype]
    try:
        status, info, resume = update_func(new_filename)
    except Exception as e:
        message = f"❌ Error inesperado en la actualización de <b>{filetype}</b>: {str(e)}"
        send_alert(message, 0)
        return jsonify(error=str(e)), 500

    # Construcción del mensaje, siempre se ejecuta si no hay excepción
    if status == 0:
        message = f"✅ <b>Importacion de {filetype.capitalize()}</b>\n{resume}"
    else:
        message = f"⚠️ <b>Importacion de {filetype.capitalize()}</b>\n{info}"

    try:
        send_alert(message, 0)
    except Exception as e:
        pass

    if status == 0:
        return jsonify(message=info, resume=resume), 200
    else:
        return jsonify(error=info), 400

