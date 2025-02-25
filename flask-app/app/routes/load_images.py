import os, time
import boto3
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.config import IMAGES_ROUTE, S3_BUCKET  # Asegúrate de tener estas variables configuradas
from app.services.images import image_to_webp
from app.services.pushover_alerts import send_alert

load_images_bp = Blueprint('load_images', __name__)


@load_images_bp.route('/upload/articles/images', methods=['POST'])
@jwt_required()
def upload_article_images():
    image_route = os.path.join(IMAGES_ROUTE, 'articles')
    
    if 'file' not in request.files:
        return jsonify(error='No file part in request'), 400

    file = request.files['file']
    codebar = request.args.get('codebar', None, int)

    if file.filename == '':
        return jsonify(error='No file selected to upload'), 400

    if file:
        filename = file.filename
        extension = filename.rsplit('.', 1)[1].lower()
        
        if codebar:
            new_filename = f'{codebar}.{extension}'
        else:
            new_filename = filename
            
        if extension != 'webp':
            temp_route = os.path.join(image_route, 'tmp')
        else:
            temp_route = image_route
            
        if not os.path.exists(temp_route):
            os.makedirs(temp_route)
            
        file_path = os.path.join(temp_route, new_filename)
            
        try:
            file.save(file_path)
        except Exception:
            send_alert(f'Error guardando la imagen para el articulo con <b>codebar: {codebar}</b>', 1)
            return jsonify(error='Error saving image.'), 500
            
        if extension != 'webp':
            time.sleep(2)
            status = image_to_webp(file_path, image_route, new_filename)
            
            if status is False:
                send_alert(f'Error convirtiendo la imagen <b>{new_filename}</b>', 1)
                return jsonify(error='Error converting image to webp format'), 500
            
            os.remove(file_path)
            
            new_filename = new_filename.rsplit('.', 1)[0] + '.webp'
            file_path = os.path.join(image_route, new_filename)
            
        # Inicializa el cliente S3
        s3 = boto3.client('s3')
                    
        # Subir el archivo a S3 en la ruta "images/articles/<new_filename>"
        s3_route = f'images/articles/{new_filename}'
        try:
            s3.upload_file(file_path, S3_BUCKET, s3_route, ExtraArgs={"ACL": "public-read"})
        except Exception as e:
            print(e)
            return jsonify(error='Error uploading image to S3.'), 500

        # Eliminamos la imagen localmente
        if os.path.exists(file_path):
            os.remove(file_path)
                    
        send_alert(f'Nueva imagen para el articulo con <b>codebar: {codebar}</b>', 0)
                    
        return jsonify(message='The image has been uploaded successfully'), 200
    
    send_alert(f'Error subiendo una imagen para el articulo <b>codebar: {codebar}</b>', 1)
    
    return jsonify(error='A server error occurred uploading the image'), 500