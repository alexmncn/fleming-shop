import datetime
from sqlalchemy import asc, desc
from sqlalchemy.dialects import mysql

from app.models import Article, Family

def_article_filter = [Article.hidden == False]
def_family_filter = [Family.hidden == False]


def apply_articles_auth_filter(query, jwt):
    if jwt:
        return query
    return query.filter(*def_article_filter)


def get_raw_sql_articles_auth_filter():
    return ' AND '.join([str(condition.compile(dialect=mysql.dialect())) for condition in def_article_filter])


def apply_families_auth_filter(query, jwt):
    if jwt:
        return query
    return query.filter(*def_family_filter)


def get_raw_sql_families_auth_filter():
    return ' AND '.join([str(condition.compile(dialect=mysql.dialect())) for condition in def_family_filter])


def apply_articles_ordering(query, order_by, direction):
    valid_fields = {
        'codebar': Article.codebar,
        'pvp': Article.pvp,
        'detalle': Article.detalle,
        'date': Article.date_created
    }

    if not order_by or order_by.lower() not in valid_fields:
        return query

    column = valid_fields[order_by.lower()]
    direction_func = desc if direction.lower() == 'desc' else asc

    # Caso especial: si ordenamos por fecha, añadimos 'detalle' como secundario
    if order_by.lower() == 'date':
        return query.order_by(direction_func(column), asc(Article.detalle))

    return query.order_by(direction_func(column))

def get_raw_sql_articles_ordering(order_by, direction):
    valid_fields = {
        'codebar': 'codebar',
        'pvp': 'pvp',
        'detalle': 'detalle',
        'date': 'date_created',
    }
    
    direction = direction.lower()
    if direction not in ['asc', 'desc']:
        direction = 'asc'

    column = valid_fields.get(order_by, None)
    if column:
        return f"ORDER BY {column} {direction.upper()}"
    else:
        return ""


def apply_pagination(query, page, per_page):
    if page is not None and per_page is not None:
        offset = (page - 1) * per_page
        return query.limit(per_page).offset(offset)
    return query


def get_pagination_values(page, per_page):
    limit = per_page
    offset = (page - 1) * per_page
    return limit, offset
