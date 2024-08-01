
from app.models import article


def articles_to_json(articulos):
    articulos_json = [
        articulo.to_dict()    
        for articulo in articulos
    ]
    
    return articulos_json or None


def all_articles(page, per_page):
    offset = (page - 1) * per_page
    
    return articles_to_json(article.query.limit(per_page).offset(offset).all())


def featured_articles(page, per_page):
    offset = (page - 1) * per_page

    return articles_to_json(article.query.filter_by(destacado=1).limit(per_page).offset(offset))