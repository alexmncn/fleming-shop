from sqlalchemy import asc, desc
from flask_jwt_extended import get_jwt

from app.models import Article, Family

def_article_filter = [Article.hidden == False]
def_family_filter = [Family.hidden == False]

def apply_articles_auth_filter(query, jwt):
    if jwt:
        return query
    return query.filter(*def_article_filter)

def apply_families_auth_filter(query, jwt):
    if jwt:
        return query
    return query.filter(*def_family_filter)


def apply_articles_ordering(query, order_by='codebar', direction='asc'):
    valid_fields = {
        'codebar': Article.codebar,
        'pvp': Article.pvp,
        'detalle': Article.detalle,
        'date': Article.date_created
    }

    if order_by and order_by.lower() in valid_fields:
        column = valid_fields[order_by.lower()]
        if direction.lower() == 'desc':
            return query.order_by(desc(column))
        else:
            return query.order_by(asc(column))
    return query 


def apply_pagination(query, page, per_page):
    if page is not None and per_page is not None:
        offset = (page - 1) * per_page
        return query.limit(per_page).offset(offset)
    return query
