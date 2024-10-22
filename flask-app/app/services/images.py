import os
from PIL import Image


def image_to_webp(image_path, save_path, image_name):
    image = Image.open(image_path)
    
    new_image_name = image_name.rsplit('.', 1)[0].lower() + '.webp'
    new_image_path = os.path.join(save_path, new_image_name)
    
    try:
        image.save(new_image_path, 'WEBP', quality=85)
    except:
        return False
        
    return True