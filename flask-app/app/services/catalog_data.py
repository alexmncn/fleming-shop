import datetime
from sqlalchemy import desc, text
from sqlalchemy.dialects import mysql
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from app.extensions import db
from app.models import Article, Family

new_articles_range = 30 # in days

def_article_filter = [Article.hidden == False]
def_family_filter = [Family.hidden == False]


@jwt_required(optional=True)
def all_articles_total():
    jwt = get_jwt()
    if jwt:
        return Article.query.count()
        
    return Article.query.filter(*def_article_filter).count()


@jwt_required(optional=True)
def all_articles(page, per_page):
    offset = (page - 1) * per_page
    
    jwt = get_jwt()
    if jwt:
        articles = Article.query.limit(per_page).offset(offset).all()
        return [article.to_dict() for article in articles]
    
    articles = Article.query.filter(*def_article_filter).limit(per_page).offset(offset).all()
    return [article.to_dict_reduced() for article in articles]


@jwt_required(optional=True)
def search_articles(search, page, per_page):
    offset = (page - 1) * per_page
    
    jwt = get_jwt()
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
        SELECT {', '.join(reduced_columns)} FROM article 
        WHERE MATCH(detalle) AGAINST(:search IN NATURAL LANGUAGE MODE)
        AND {sql_conditions_text}
        LIMIT :per_page OFFSET :offset
        """
    
    query = db.session.execute(
        text(text_query), 
        {'search': search, 'per_page': per_page, 'offset': offset}
    ).mappings()
    
    articles = query.fetchall()
    
 
    return [dict(article) for article in articles]


@jwt_required(optional=True)
def search_articles_total(search):
    jwt = get_jwt()
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
    
    jwt = get_jwt()
    if jwt:
        return Article.query.filter(Article.factualizacion>=time_threshold).order_by(desc(Article.factualizacion)).count()
    
    return Article.query.filter(*def_article_filter, Article.factualizacion>=time_threshold).order_by(desc(Article.factualizacion)).count()


@jwt_required(optional=True)
def new_articles(page, per_page):
    offset = (page - 1) * per_page
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
    
    jwt = get_jwt()
    if jwt:
        articles = Article.query.filter(Article.factualizacion>=time_threshold).order_by(desc(Article.factualizacion)).limit(per_page).offset(offset)
    
        if articles is None:
            articles = Article.query.all().order_by(desc(Article.factualizacion)).limit(per_page)
        
        return [article.to_dict() for article in articles]
            
    articles = Article.query.filter(*def_article_filter, Article.factualizacion>=time_threshold).order_by(desc(Article.factualizacion)).limit(per_page).offset(offset)
    
    if articles is None:
        articles = Article.query.filter(*def_article_filter).all().order_by(desc(Article.factualizacion)).limit(per_page)
    
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