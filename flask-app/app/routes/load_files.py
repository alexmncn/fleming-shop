from flask import Blueprint, request, send_file, jsonify, current_app, send_from_directory
import os

from app.config import INTERNAL_API_KEY, SCRIPTS_ROUTE

load_files_bp = Blueprint("load_files", __name__)


@load_files_bp.route('/files/scripts/enviar_datos', methods=['GET', 'POST'])
def manage_script():
    base_path = current_app.root_path
    expected_path = os.path.join(base_path, SCRIPTS_ROUTE, 'enviar_datos.py')

    if request.headers.get("X-Internal-API-Key") != INTERNAL_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        if os.path.exists(expected_path):
            return send_file(expected_path, mimetype='text/x-python')
        return jsonify({"error": "Script not found"}), 404

    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify(error='No file part in request'), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify(error='No file selected to upload'), 400
        
        try:
            os.makedirs(os.path.dirname(expected_path), exist_ok=True)
            
            file.save(expected_path)
            return jsonify({"message": "Script actualizado con éxito"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@load_files_bp.route("/files/turnstile.html")
def turnstile_page():
    return send_from_directory("data/files", "turnstile.html")