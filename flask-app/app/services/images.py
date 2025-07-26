import uuid, os
from flask import url_for, jsonify
from werkzeug.utils import secure_filename

from app.utils.images import save_temp_image, convert_to_webp_and_clean, save_final_image
from app.services.pushover_alerts import send_alert

from app.extensions import db
from app.models import ArticleImage


def process_uploaded_image(file, codebar, is_main):
    # Validación, renombrado, guardado temporal
    image_id = str(uuid.uuid4())
    filename = f"{image_id}.webp"
    original_filename = secure_filename(file.filename)

    # Convertir y procesar imagen
    tmp_path = save_temp_image(file, original_filename)
    processed_img = convert_to_webp_and_clean(tmp_path)
    final_path = save_final_image(processed_img, filename)

    # Registrar en DB
    register_image_in_db(image_id, codebar, filename, is_main, final_path)

    return url_for('images.get_article_image', image_id=image_id)


def register_image_in_db(image_id, codebar, filename, is_main, final_path):
    # Comprobar si ya hay imágenes para este codebar, sino hacerla main
    existing_images = ArticleImage.query.filter_by(article_codebar=codebar).count()
    if existing_images == 0:
        is_main = True
    elif is_main:
        # Si ya hay imágenes y la nueva debe ser main, quitar is_main a la anterior
        main_image = ArticleImage.query.filter_by(article_codebar=codebar, is_main=True).first()
        if main_image:
            main_image.is_main = False
            db.session.add(main_image)
    
    image = ArticleImage(
        id=image_id,
        article_codebar=codebar,
        filename=filename,
        is_main=is_main
    )

    try:
        db.session.add(image)
        db.session.commit()
    except Exception as e:
        os.remove(final_path)  # Limpieza
        send_alert(f'Error registrando imagen en DB para artículo <b>{codebar}</b>: {str(e)}', 1)
        return jsonify(error='Database error'), 500