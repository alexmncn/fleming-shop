import datetime
from sqlalchemy import text
from sqlalchemy.dialects import mysql
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models import Article, Family
from app.utils import query_helpers

new_articles_range = 15 # in days
no_articles_limit = 20


@jwt_required(optional=True)
def all_articles_total():
    jwt = get_jwt()
    
    query = Article.query
    query = query_helpers.apply_articles_auth_filter(query, jwt)
    
    return query.count()


@jwt_required(optional=True)
def all_articles_codebars():
    jwt = get_jwt()
    
    query = db.session.query(Article.codebar)
    query = query_helpers.apply_articles_auth_filter(query, jwt)
    query = query_helpers.apply_articles_ordering(query)
    
    return [codebar[0] for codebar in query.all()]
    

@jwt_required(optional=True)
def all_articles(page, per_page, order_by, direction):
    jwt = get_jwt()
    
    query = Article.query
    query = query_helpers.apply_articles_auth_filter(query, jwt)
    query = query_helpers.apply_articles_ordering(query, order_by, direction)
    query = query_helpers.apply_pagination(query, page, per_page)
    
    return [article.to_dict() if jwt else article.to_dict_reduced() for article in query.all()]


@jwt_required(optional=True)
def search_articles_total(search, filter, context_filter=None, context_value=None):
    jwt = get_jwt()

    if filter == 'detalle':
        base_query = """
        SELECT COUNT(*) as total FROM article
        WHERE MATCH(detalle) AGAINST(:search IN NATURAL LANGUAGE MODE)
        """

        # Auth filter
        if not jwt:
            sql_auth_conditions = query_helpers.get_raw_sql_articles_auth_filter()
            base_query += f" AND {sql_auth_conditions}"
            
        # Context filter
        if context_filter:
            if context_filter == 'featured':
                base_query += f" AND destacado = 1"
            elif context_filter == 'new':
                time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
                base_query += f" AND date_created >= '{time_threshold}'"
            elif context_filter == 'family':
                try:
                    codfam = int(context_value)
                    base_query += f" AND codfam = {codfam}"
                except TypeError:
                    return None

        query = db.session.execute(text(base_query),{'search': search})
        
        return query.scalar()

    elif filter == 'codebar':
        try:
            codebar = int(search)
            query = Article.query.filter_by(codebar=codebar)
            query = query_helpers.apply_articles_auth_filter(query, jwt)
            
            if context_filter:
                if context_filter == 'featured':
                    query = query.filter_by(destacado=1)
                elif context_filter == 'new':
                    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
                    query = query.filter(Article.date_created >= time_threshold)
                elif context_filter == 'family':
                    try:
                        codfam = int(context_value)
                        query = query.filter_by(codfam=codfam)
                    except TypeError:
                        return None
                    
            return query.count()
        except ValueError:
            return None


@jwt_required(optional=True)
def search_articles(search, filter, page, per_page, order_by, direction, context_filter=None, context_value=None):
    jwt = get_jwt()

    if filter == 'detalle':
        base_query = """
        SELECT * FROM article 
        WHERE MATCH(detalle) AGAINST(:search IN NATURAL LANGUAGE MODE)
        """

        # Auth filter
        if not jwt:
            sql_conditions = query_helpers.get_raw_sql_articles_auth_filter()
            base_query += f" AND {sql_conditions}"

        # Context filter
        if context_filter:
            if context_filter == 'featured':
                base_query += f" AND destacado = 1"
            elif context_filter == 'new':
                time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
                base_query += f" AND date_created >= '{time_threshold}'"
            elif context_filter == 'family':
                try:
                    codfam = int(context_value)
                    base_query += f" AND codfam = {codfam}"
                except TypeError:
                    return None
                
        # Ordering
        order_clause = query_helpers.get_raw_sql_articles_ordering(order_by, direction)
        base_query += f" {order_clause}"

        # Pagination
        limit, offset = query_helpers.get_pagination_values(page, per_page)
        base_query += " LIMIT :limit OFFSET :offset"

        # Execute the query with parameters
        query = db.session.execute(text(base_query), {'search': search, 'limit': limit, 'offset': offset}).mappings()
        articles_raw = query.fetchall()

        return [Article(**article).to_dict() if jwt else Article(**article).to_dict_reduced() for article in articles_raw]

    elif filter == 'codebar':
        try:
            codebar = int(search)
            query = Article.query.filter_by(codebar=codebar)
            query = query_helpers.apply_articles_auth_filter(query, jwt)
            
            if context_filter:
                if context_filter == 'featured':
                    query = query.filter_by(destacado=1)
                elif context_filter == 'new':
                    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
                    query = query.filter(Article.date_created >= time_threshold)
                elif context_filter == 'family':
                    try:
                        codfam = int(context_value)
                        query = query.filter_by(codfam=codfam)
                    except TypeError:
                        return None
            
            query = query_helpers.apply_articles_ordering(query, order_by, direction)
            query = query_helpers.apply_pagination(query, page, per_page)

            return [article.to_dict() if jwt else article.to_dict_reduced() for article in query.all()]
        except ValueError:
            return None


@jwt_required(optional=True)
def featured_articles_total():
    jwt = get_jwt()
    
    query = Article.query.filter_by(destacado=1)
    query = query_helpers.apply_articles_auth_filter(query, jwt)
    
    return query.count()


@jwt_required(optional=True)
def featured_articles(page, per_page, order_by, direction):
    jwt = get_jwt()
    
    query = Article.query.filter_by(destacado=1)
    query = query_helpers.apply_articles_auth_filter(query, jwt)
    query = query_helpers.apply_articles_ordering(query, order_by, direction)
    query = query_helpers.apply_pagination(query, page, per_page)
    
    return [article.to_dict() if jwt else article.to_dict_reduced() for article in query.all()]


@jwt_required(optional=True)
def new_articles_total():
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
    jwt = get_jwt()

    query = Article.query.filter(Article.date_created >= time_threshold)
    query = query_helpers.apply_articles_auth_filter(query, jwt)
    articles_count = query.count()

    return articles_count or no_articles_limit


@jwt_required(optional=True)
def new_articles(page, per_page, order_by, direction):
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
    jwt = get_jwt()

    query = Article.query.filter(Article.date_created >= time_threshold)
    query = query_helpers.apply_articles_auth_filter(query, jwt)
    query = query_helpers.apply_articles_ordering(query, order_by, direction)
    query = query_helpers.apply_pagination(query, page, per_page)
    articles = query.all()
    
    if not articles:
        fallback_query = Article.query
        fallback_query = query_helpers.apply_articles_auth_filter(fallback_query, jwt)
        fallback_query = query_helpers.apply_articles_ordering(fallback_query, order_by, direction)
        articles = fallback_query.limit(no_articles_limit).all()

    return [article.to_dict() if jwt else article.to_dict_reduced() for article in articles]
    

@jwt_required(optional=True)
def all_families_total():
    jwt = get_jwt()
    
    query = Family.query
    query = query_helpers.apply_families_auth_filter(query, jwt)
    
    return query.count()    


@jwt_required(optional=True)
def all_families():
    jwt = get_jwt()
    
    query = Family.query
    query = query_helpers.apply_families_auth_filter(query, jwt)
    
    return [family.to_dict() if jwt else family.to_dict_reduced() for family in query.all()]


@jwt_required(optional=True)
def family_articles_total(family_id):
    jwt = get_jwt()
    
    query = Article.query.filter_by(codfam=family_id)
    query = query_helpers.apply_articles_auth_filter(query, jwt)
    
    return query.count()


@jwt_required(optional=True)
def family_articles(family_id, page, per_page, order_by, direction):
    jwt = get_jwt()
    
    query = Article.query.filter_by(codfam=family_id)
    query = query_helpers.apply_articles_auth_filter(query, jwt)
    query = query_helpers.apply_articles_ordering(query, order_by, direction)
    query = query_helpers.apply_pagination(query, page, per_page)
    
    return [article.to_dict() if jwt else article.to_dict_reduced() for article in query.all()]