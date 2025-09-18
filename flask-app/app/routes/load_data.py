import os, glob, uuid
from datetime import datetime
from redis import Redis
from rq import Queue
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.import_to_db import process_import_file
from app.services.pushover_alerts import send_alert
from app.extensions import db
from app.models import ImportFile

from app.config import UPLOAD_ROUTE

os.makedirs(UPLOAD_ROUTE, exist_ok=True)

load_data_bp = Blueprint('load_data', __name__)


@load_data_bp.route('/upload/<string:filetype>', methods=['POST'])
@jwt_required()
def upload_file(filetype):
    username = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify(error='No file part in request'), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify(error='No file selected to upload'), 400

    date = datetime.now()
    timestamp = date.strftime('%Y%m%d_%H%M%S')
    clean_filename = f"{filetype}_{timestamp}"
    filename = f"{clean_filename}.dbf"
    data_path = os.path.join(current_app.root_path, UPLOAD_ROUTE)
    file_path = os.path.join(data_path, filename)
    
    # Generate uuid
    import_file_id = str(uuid.uuid4())
    
    # Save file
    try:
        file.save(file_path)
        
        import_file = ImportFile(
            id=import_file_id,
            filetype=filetype,
            filename=clean_filename,
            filepath=file_path, 
            uploaded_at=date,
            status="pending",
            status_message="File saved. Waiting to be processed..."
        )
        db.session.add(import_file)
        db.session.commit()
    except Exception as e:
        send_alert(f"❌ Error inesperado al guardar el archivo de datos <b>{filetype}</b>: {e}", 1)
        return jsonify(error='Error saving file'), 500
    
    # Clean old files
    try:
        pattern = os.path.join(data_path, f"{filetype}_*.dbf")
        for file_ in glob.glob(pattern):
            if os.path.basename(file_) != filename:
                os.remove(file_)
    except Exception:
        pass
    
    # Add task to redis queue
    try:
        redis_conn = Redis(host="localhost", port=6379)
        q = Queue(connection=redis_conn)
        
        job = q.enqueue(process_import_file, import_file_id, username)
    except:
        send_alert(f"⚠️ Recibido un nuevo archivo de datos <b>{filetype}</b>: Error al poner en cola, prueba a hacerlo manualmente.", 1)
        return jsonify(message="Error queuing task, try adding it manually"), 206
    
    send_alert(f"Recibido un nuevo archivo de datos <b>{filetype}</b>. Será procesado en unos instantes...", 0)
    return jsonify(message="File saved successfully: will be processed as soon as possible"), 202