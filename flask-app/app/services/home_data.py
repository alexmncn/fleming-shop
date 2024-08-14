import datetime
from sqlalchemy import desc

from app.models import article, family

new_articles_range = 30 # in days


def all_articles_total():
    return article.query.count()


def all_articles(page, per_page):
    offset = (page - 1) * per_page
    
    articles = article.query.limit(per_page).offset(offset).all()
    return [article.to_dict_reduced() for article in articles]


def search_articles(search):
    articles = article.query.filter(
        (article.detalle.ilike(f'%{search}%')) | 
        (article.ref.ilike(f'%{search}%'))
    ).all()
    return [article.to_dict_reduced() for article in articles]
    


def featured_articles_total():
    return article.query.filter_by(destacado=1).count()


def featured_articles(page, per_page):
    offset = (page - 1) * per_page
    
    articles = article.query.filter_by(destacado=1).limit(per_page).offset(offset)
    return [article.to_dict_reduced() for article in articles]


def new_articles_total():
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
    
    return article.query.filter(article.factualizacion>=time_threshold).order_by(desc(article.factualizacion)).count()


def new_articles(page, per_page):
    offset = (page - 1) * per_page
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
    
    articles = article.query.filter(article.factualizacion>=time_threshold).order_by(desc(article.factualizacion)).limit(per_page).offset(offset)
    
    if articles is None:
        articles = article.query.all().order_by(desc(article.factualizacion)).limit(per_page)
    
    return [article.to_dict_reduced() for article in articles]
    

def all_families():
    families = family.query.all()
    return [family.to_dict() for family in families]


def family_articles(family_id, page, per_page):
    offset = (page - 1) * per_page
    
    articles = article.query.filter_by(codfam=family_id).limit(per_page).offset(offset)
    return [article.to_dict_reduced() for article in articles]

def family_articles_total(family_id):
    return article.query.filter_by(codfam=family_id).count()