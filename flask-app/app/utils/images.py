import os, io
from PIL import Image
from rembg import remove
from flask import current_app

from app.config import IMAGES_ROUTE


def save_temp_image(file, name):
    images_directory = os.path.join(current_app.root_path, IMAGES_ROUTE)
    articles_images_directory = os.path.join(images_directory, 'articles')
    tmp_dir = os.path.join(articles_images_directory, 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    path = os.path.join(tmp_dir, name)
    file.save(path)
    return path

def convert_to_webp_and_clean(input_path):
    image = remove_background(input_path)
    image = crop_to_content(image)
    image = resize_and_center(image, size=(1000, 1000))
    
    return image

def save_final_image(image, filename):
    images_directory = os.path.join(current_app.root_path, IMAGES_ROUTE)
    articles_images_directory = os.path.join(images_directory, 'articles')
    final_dir = articles_images_directory
    os.makedirs(final_dir, exist_ok=True)
    final_path = os.path.join(final_dir, filename)
    image.save(final_path, format='WEBP', quality=85)
    return final_path

def remove_background(input_path):
    with open(input_path, 'rb') as f:
        input_data = f.read()
    output_data = remove(input_data)
    image = Image.open(io.BytesIO(output_data)).convert("RGBA")
    return image

def crop_to_content(image: Image.Image) -> Image.Image:
    """Recorta la imagen al contenido visible (no transparente)."""
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)

    return image

def resize_and_center(image: Image.Image, size=(1000, 1000), margin_ratio=0) -> Image.Image:
    """
    Redimensiona la imagen manteniendo proporción, la centra en un fondo blanco
    """
    target_w, target_h = size

    # Calcular tamaño máximo de imagen útil restando márgenes
    margin_w = int(target_w * margin_ratio)
    margin_h = int(target_h * margin_ratio)
    max_w = target_w - 2 * margin_w
    max_h = target_h - 2 * margin_h

    # Redimensionar imagen manteniendo aspecto
    image.thumbnail((max_w, max_h), Image.LANCZOS)

    # Crear fondo blanco
    background = Image.new("RGB", size, (255, 255, 255))

    # Calcular posición centrada
    x = (target_w - image.width) // 2
    y = (target_h - image.height) // 2

    background.paste(image, (x, y), mask=image if image.mode == "RGBA" else None)

    return background