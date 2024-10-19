import datetime
from sqlalchemy import desc, text

from app.extensions import db
from app.models import Article, Family

new_articles_range = 30 # in days

def_article_filter = [Article.hidden == False]
def_family_filter = [Family.hidden == False]

def all_articles_total():
    return Article.query.filter(*def_article_filter).count()


def all_articles(page, per_page):
    offset = (page - 1) * per_page
    
    articles = Article.query.filter(*def_article_filter).limit(per_page).offset(offset).all()
    return [article.to_dict_reduced() for article in articles]


def search_articles(search, page, per_page):
    offset = (page - 1) * per_page
    
    query = db.session.execute(
        text("""
        SELECT * FROM article 
        WHERE MATCH(detalle) AGAINST(:search IN NATURAL LANGUAGE MODE) 
        LIMIT :per_page OFFSET :offset
        """), 
        {'search': search, 'per_page': per_page, 'offset': offset}
    ).mappings()
    
    articles = query.fetchall()
    
 
    return [dict(article) for article in articles]


def search_articles_total(search):
    query = db.session.execute(
        text("""
        SELECT COUNT(*) as total FROM article
        WHERE MATCH(detalle) AGAINST(:search IN NATURAL LANGUAGE MODE)
        """),
        {'search': search}
    )
    total_articles = query.fetchone()[0]
    
    return total_articles


def featured_articles_total():
    return Article.query.filter(*def_article_filter).filter_by(destacado=1).count()


def featured_articles(page, per_page):
    offset = (page - 1) * per_page
    
    articles = Article.query.filter(*def_article_filter).filter_by(destacado=1).limit(per_page).offset(offset)
    return [article.to_dict_reduced() for article in articles]


def new_articles_total():
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
    
    return Article.query.filter(*def_article_filter, Article.factualizacion>=time_threshold).order_by(desc(Article.factualizacion)).count()


def new_articles(page, per_page):
    offset = (page - 1) * per_page
    time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=new_articles_range)
    
    articles = Article.query.filter(*def_article_filter, Article.factualizacion>=time_threshold).order_by(desc(Article.factualizacion)).limit(per_page).offset(offset)
    
    if articles is None:
        articles = Article.query.filter(*def_article_filter).all().order_by(desc(Article.factualizacion)).limit(per_page)
    
    return [article.to_dict_reduced() for article in articles]
    

def all_families():
    families = Family.query.filter(*def_family_filter).all()
    return [family.to_dict_reduced() for family in families]


def family_articles(family_id, page, per_page):
    offset = (page - 1) * per_page
    
    articles = Article.query.filter(*def_article_filter).filter_by(codfam=family_id).limit(per_page).offset(offset)
    return [article.to_dict_reduced() for article in articles]

def family_articles_total(family_id):
    return Article.query.filter(*def_article_filter).filter_by(codfam=family_id).count()