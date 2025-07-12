import os
from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
import uuid

from app.config import IMAGES_ROUTE
from app.utils.images import image_to_webp
from app.services.pushover_alerts import send_alert
from app.extensions import db

from app.models import ArticleImage

images_bp = Blueprint('images', __name__)

ARTICLES_IMAGES_ROUTE = os.path.join(IMAGES_ROUTE, 'articles')

@images_bp.route('/images/articles/upload', methods=['POST'])
@jwt_required()
def upload_article_images():
    file = request.files.get('file')
    codebar = request.form.get('codebar')
    is_main = request.form.get('is_main', '0') in ['1', 'true', 'True']

    # Validaciones iniciales
    if not file or file.filename == '':
        return jsonify(error='No file provided'), 400
    if not codebar:
        return jsonify(error='Missing article codebar'), 400

    # Procesar nombre seguro
    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit('.', 1)[-1].lower()

    if extension not in ['jpg', 'jpeg', 'png', 'webp']:
        return jsonify(error='Unsupported file format'), 400

    # Generar UUID
    image_id = str(uuid.uuid4())
    new_filename = f"{image_id}.webp"
    tmp_folder = os.path.join(ARTICLES_IMAGES_ROUTE, 'tmp')
    final_folder = ARTICLES_IMAGES_ROUTE
    os.makedirs(tmp_folder, exist_ok=True)
    os.makedirs(final_folder, exist_ok=True)

    # Guardar temporalmente
    temp_path = os.path.join(tmp_folder, original_filename)
    try:
        file.save(temp_path)
    except Exception:
        send_alert(f'Error guardando imagen temporal para el artículo <b>{codebar}</b>', 1)
        return jsonify(error='Error saving temporary file'), 500

    # Convertir a webp
    final_path = os.path.join(final_folder, new_filename)
    if extension != 'webp':
        try:
            image_to_webp(temp_path, final_folder, new_filename)
            os.remove(temp_path)
        except Exception:
            send_alert(f'Error convirtiendo imagen <b>{original_filename}</b> a webp', 1)
            return jsonify(error='Image conversion failed'), 500
    else:
        # Si ya es webp, mover directamente
        os.rename(temp_path, final_path)

    # Comprobar si ya hay imágenes para este codebar, sino hacerla main
    existing_images = ArticleImage.query.filter_by(article_codebar=codebar).count()
    if existing_images == 0:
        is_main = True

    # Registrar en la base de datos
    image = ArticleImage(
        id=image_id,
        article_codebar=codebar,
        filename=new_filename,
        is_main=is_main
    )

    try:
        session = db.session
        session.add(image)
        session.commit()
    except Exception as e:
        os.remove(final_path)  # Limpieza
        send_alert(f'Error registrando imagen en DB para artículo <b>{codebar}</b>: {str(e)}', 1)
        return jsonify(error='Database error'), 500

    send_alert(f'Se ha subido una nueva imagen para el artículo <b>{codebar}</b>', 0)

    return jsonify(message='Imagen subida correctamente', image_url=image.url), 200  


@images_bp.route('/images/articles/<image_id>', methods=['GET'])
def get_article_image(image_id):
    image = ArticleImage.query.get_or_404(image_id)
    article_images_route = os.path.join(IMAGES_ROUTE, 'articles')
    return send_file(os.path.join(article_images_route, image.article_codebar, image.filename))
