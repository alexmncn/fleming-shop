import os, uuid
from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from app.config import IMAGES_ROUTE
from app.services.images import process_uploaded_image
from app.services.pushover_alerts import send_alert

from app.extensions import db
from app.models import ArticleImage

images_bp = Blueprint('images', __name__)


@images_bp.route('/images/articles/upload', methods=['POST'])
@jwt_required()
def upload_article_images():
    file = request.files.get('file')
    codebar = request.form.get('codebar')
    is_main = request.form.get('is_main', '0') in ['1', 'true', 'True']
    convert = request.form.get('convert', '0') in ['1', 'true', 'True']
    keep_original = request.form.get('keep_original', '0') in ['1', 'true', 'True']

    if not file or not codebar:
        return jsonify(error='Missing data'), 400

    try:
        image_url = process_uploaded_image(file, codebar, is_main, convert, keep_original)
        return jsonify(message='Image uploaded successfully', image_url=image_url), 200
    except Exception as e:
        send_alert(f"Error procesando imagen: {e}", 1)
        return jsonify(error="Internal server error"), 500


@images_bp.route('/images/articles/<image_id>', methods=['GET'])
def get_article_image(image_id):
    image = ArticleImage.query.get_or_404(image_id)
    images_directory = os.path.join(current_app.root_path, IMAGES_ROUTE)
    articles_images_directory = os.path.join(images_directory, 'articles')
    return send_file(os.path.join(articles_images_directory, image.filename))


@images_bp.route('/images/articles/<image_id>', methods=['DELETE'])
@jwt_required()
def delete_article_image(image_id):
    image = ArticleImage.query.get_or_404(image_id)
    images_directory = os.path.join(current_app.root_path, IMAGES_ROUTE)
    articles_images_directory = os.path.join(images_directory, 'articles')
    image_path = os.path.join(articles_images_directory, image.filename)

    try:
        if os.path.exists(image_path):
            os.remove(image_path)
        db.session.delete(image)
        db.session.commit()
        return jsonify(message=f'Image with id {image_id} deleted successfully'), 200
    except Exception as e:
        send_alert(f"Error eliminando imagen con id {image_id}: {e}", 1)
        return jsonify(error="Internal server error"), 500