import datetime
from sqlalchemy import desc

from app.models import article, family


def all_articles(page, per_page):
    offset = (page - 1) * per_page
    
    articles = article.query.limit(per_page).offset(offset).all()
    return [article.to_dict_reduced() for article in articles]


def featured_articles(page, per_page):
    offset = (page - 1) * per_page
    
    articles = article.query.filter_by(destacado=1).limit(per_page).offset(offset)
    return [article.to_dict_reduced() for article in articles]


def new_articles(page, per_page):
    offset = (page - 1) * per_page
    range = 14 # in days
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=range)
    
    articles = article.query.filter(article.factualizacion>=time_threshold).order_by(desc(article.factualizacion)).limit(per_page).offset(offset)
    return [article.to_dict_reduced() for article in articles]
    

def all_families():
    families = family.query.all()
    return [family.to_dict() for family in families]


def family_articles(family_id, page, per_page):
    offset = (page - 1) * per_page
    
    articles = article.query.filter_by(codfam=family_id).limit(per_page).offset(offset)
    return [article.to_dict_reduced() for article in articles]