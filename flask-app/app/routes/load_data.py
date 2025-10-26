import os, glob, uuid, shutil, time
from datetime import datetime, timedelta
from redis import Redis
from rq import Queue
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.import_to_db import process_import_file
from app.services.pushover_alerts import send_alert
from app.extensions import db
from app.models import ImportFile

from app.config import UPLOAD_ROUTE, REDIS_DATABASE_HOST, REDIS_DATABASE_PORT, REDIS_IMPORTS_QUEUE

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
        os.makedirs(data_path, exist_ok=True)
        
        with open(file_path, "wb") as f:
            file.stream.seek(0)
            shutil.copyfileobj(file.stream, f)
            f.flush()
            os.fsync(f.fileno())

        if not os.path.exists(file_path):
            send_alert(f"❌ Error al guardar el archivo de datos <b>{filetype}</b>: El archivo no se guardo y no lanzó ningún error", 1)
            return jsonify(error='File save failed without throw error'), 500
        
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
        redis_conn = Redis(host=REDIS_DATABASE_HOST, port=REDIS_DATABASE_PORT)
        q = Queue(REDIS_IMPORTS_QUEUE, connection=redis_conn)
        
        job = q.enqueue_in(timedelta(minutes=10), process_import_file, import_file_id, username)
    except Exception as e:
        send_alert(f"⚠️ Archivo recibido: <b>{filetype.capitalize()}</b>: Error al poner en cola, prueba a hacerlo manualmente: {e}", 1)
        return jsonify(message="File saved successfully but failed queuing task, try adding it manually"), 206
    
    send_alert(f"Archivo recibido: <b>{filetype.capitalize()}</b>. Será procesado en unos instantes...\nJob ID: {job.id}", 0)
    return jsonify(message="File saved successfully: will be processed as soon as possible"), 202