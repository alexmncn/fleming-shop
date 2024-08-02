
from app.models import article, family

def object_to_json(objects):
    articulos_json = [
        object.to_dict()    
        for object in objects
    ]
    
    return articulos_json or None


def all_articles(page, per_page):
    offset = (page - 1) * per_page
    
    return object_to_json(article.query.limit(per_page).offset(offset).all())


def featured_articles(page, per_page):
    offset = (page - 1) * per_page
    
    return object_to_json(article.query.filter_by(destacado=1).limit(per_page).offset(offset))


def all_families():
    return object_to_json(family.query.all())


def family_articles(family_id, page, per_page):
    offset = (page - 1) * per_page
    
    return object_to_json(article.query.filter_by(codfam=family_id).limit(per_page).offset(offset))