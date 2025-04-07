import datetime
from sqlalchemy import desc, text
from sqlalchemy.dialects import mysql
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models import Article, Family
from app.utils import query_helpers

new_articles_range = 15 # in days
no_articles_limit = 20

def_article_filter = [Article.hidden == False]
def_family_filter = [Family.hidden == False]


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
def search_articles(search, filter, page, per_page):
    offset = (page - 1) * per_page
    articles = None
    jwt = get_jwt()
    
    if filter == 'detalle':
        if jwt:
            text_query = """
            SELECT * FROM article 
            WHERE MATCH(detalle) AGAINST(:search IN NATURAL LANGUAGE MODE) 
            LIMIT :per_page OFFSET :offset
            """
        else:
            sql_conditions = [str(condition.compile(dialect=mysql.dialect())) for condition in def_article_filter]
            sql_conditions_text = ' AND '.join(sql_conditions)
            
            reduced_columns = ['ref', 'codebar', 'detalle', 'codfam', 'pvp', 'stock', 'destacado']
            
            text_query = f"""
            SELECT * FROM article 
            WHERE MATCH(detalle) AGAINST(:search IN NATURAL LANGUAGE MODE)
            AND {sql_conditions_text}
            LIMIT :per_page OFFSET :offset
            """
        
        query = db.session.execute(
            text(text_query), 
            {'search': search, 'per_page': per_page, 'offset': offset}
        ).mappings()
        
        articles_raw = query.fetchall()
        
        if jwt:
            return [Article(**article).to_dict() for article in articles_raw]
        
        return [Article(**article).to_dict_reduced() for article in articles_raw]
            
    elif filter == 'codebar':
        try:
            codebar = int(search)
            if jwt:
                articles = Article.query.filter_by(codebar=codebar).limit(per_page).offset(offset)
                return [article.to_dict() for article in articles]
            else:
                articles = Article.query.filter(*def_article_filter).filter_by(codebar=codebar).limit(per_page).offset(offset)
                return [article.to_dict_reduced() for article in articles]
        except ValueError:
            return None


@jwt_required(optional=True)
def search_articles_total(search, filter):
    total_articles = None
    jwt = get_jwt()
    
    if filter == 'detalle':
        if jwt:
            text_query = """
            SELECT COUNT(*) as total FROM article
            WHERE MATCH(detalle) AGAINST(:search IN NATURAL LANGUAGE MODE)
            """
        else:
            sql_conditions = [str(condition.compile(dialect=mysql.dialect())) for condition in def_article_filter]
            sql_conditions_text = ' AND '.join(sql_conditions)
            
            text_query = f"""
            SELECT COUNT(*) as total FROM article
            WHERE MATCH(detalle) AGAINST(:search IN NATURAL LANGUAGE MODE)
            AND {sql_conditions_text}
            """
        
        query = db.session.execute(
            text(text_query),
            {'search': search}
        )
        total_articles = query.fetchone()[0]
        
    elif filter == 'codebar':
        try:
            codebar = int(search)
            if jwt:
                total_articles = Article.query.filter_by(codebar=codebar).count()
            else:
                total_articles = Article.query.filter(*def_article_filter).filter_by(codebar=codebar).count()
        except ValueError:
            return None
        
    return total_articles


@jwt_required(optional=True)
def featured_articles_total():
    jwt = get_jwt()
    if jwt:
        return Article.query.filter_by(destacado=1).count()
        
    return Article.query.filter(*def_article_filter).filter_by(destacado=1).count()


@jwt_required(optional=True)
def featured_articles(page, per_page):
    offset = (page - 1) * per_page
    
    jwt = get_jwt()
    if jwt:
        articles = Article.query.filter_by(destacado=1).limit(per_page).offset(offset)
        return [article.to_dict() for article in articles]
    
    articles = Article.query.filter(*def_article_filter).filter_by(destacado=1).limit(per_page).offset(offset)
    return [article.to_dict_reduced() for article in articles]


@jwt_required(optional=True)
def new_articles_total():
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
    no_articles_limit = 20
    
    jwt = get_jwt()
    if jwt:
        articles_count = Article.query.filter(Article.date_created>=time_threshold).order_by(desc(Article.date_created)).count()
        
        if articles_count is None:
            return no_articles_limit
        
    articles_count = Article.query.filter(*def_article_filter, Article.date_created>=time_threshold).order_by(desc(Article.date_created)).count()
    
    if articles_count is None:
        return no_articles_limit

    return articles_count    
    

@jwt_required(optional=True)
def new_articles(page, per_page):
    offset = (page - 1) * per_page
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
    no_articles_limit = 20
    
    jwt = get_jwt()
    if jwt:
        articles = Article.query.filter(Article.date_created>=time_threshold).order_by(desc(Article.date_created), Article.codebar).limit(per_page).offset(offset)
    
        if articles is None:
            articles = Article.query.all().order_by(desc(Article.date_created), Article.codebar).limit(no_articles_limit)
        
        return [article.to_dict() for article in articles]
            
    articles = Article.query.filter(*def_article_filter, Article.date_created>=time_threshold).order_by(desc(Article.date_created), Article.codebar).limit(per_page).offset(offset)
    
    if articles is None:
        articles = Article.query.filter(*def_article_filter).all().order_by(desc(Article.date_created), Article.codebar).limit(no_articles_limit)
    
    return [article.to_dict_reduced() for article in articles]
    

@jwt_required(optional=True)
def all_families():
    jwt = get_jwt()
    
    if jwt:
        families = Family.query.all()
        return [family.to_dict() for family in families]
        
    families = Family.query.filter(*def_family_filter).all()
    return [family.to_dict_reduced() for family in families]


@jwt_required(optional=True)
def family_articles_total(family_id):
    jwt = get_jwt()
    if jwt:
        return Article.query.filter_by(codfam=family_id).count()
        
    return Article.query.filter(*def_article_filter).filter_by(codfam=family_id).count()


@jwt_required(optional=True)
def family_articles(family_id, page, per_page):
    offset = (page - 1) * per_page
    
    jwt = get_jwt()
    if jwt:
        articles = Article.query.filter_by(codfam=family_id).limit(per_page).offset(offset)
        return [article.to_dict() for article in articles]
    
    articles = Article.query.filter(*def_article_filter).filter_by(codfam=family_id).limit(per_page).offset(offset)
    return [article.to_dict_reduced() for article in articles]