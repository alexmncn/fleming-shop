import datetime
from sqlalchemy import desc

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


def new_articles(page, per_page):
    offset = (page - 1) * per_page
    range = 14 # in days
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=range)
    
    articles = article.query.filter(article.factualizacion>=time_threshold).order_by(desc(article.factualizacion)).limit(per_page).offset(offset)
    
    return object_to_json(articles)
    

def all_families():
    return object_to_json(family.query.all())


def family_articles(family_id, page, per_page):
    offset = (page - 1) * per_page
    
    return object_to_json(article.query.filter_by(codfam=family_id).limit(per_page).offset(offset))