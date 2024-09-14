from flask import Blueprint, request, jsonify

from app.services import home_data


home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    return '<h1>Hello world</h1>'


@home_bp.route('/articles/total')
def all_articles_total():
    total = home_data.all_articles_total()
    return jsonify(total=total)


@home_bp.route('/articles/all')
def all_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    articles = home_data.all_articles(page, per_page)
    
    if len(articles) == 0:
        return jsonify(error='Not found'), 404
    
    return jsonify(articles)


@home_bp.route('/articles/search')
def search_articles():
    search = request.args.get('search', None)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    articles = home_data.search_articles(search, page, per_page)
    
    if len(articles) == 0:
        return jsonify(error='Not found'), 404
    
    return jsonify(articles)


@home_bp.route('/articles/search/total')
def search_articles_total():
    search = request.args.get('search', None)
    
    total = home_data.search_articles_total(search)
    
    return jsonify(total=total)

@home_bp.route('/articles/featured/total')
def featured_articles_total():
    total = home_data.featured_articles_total()
    return jsonify(total=total)
    

@home_bp.route('/articles/featured')
def featured_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    articles = home_data.featured_articles(page, per_page)
    
    if len(articles) == 0:
        return jsonify(error='Not found'), 404
    
    return jsonify(articles)


@home_bp.route('/articles/new/total')
def new_articles_total():
    total = home_data.new_articles_total()
    return jsonify(total=total)


@home_bp.route('/articles/new')
def new_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    articles = home_data.new_articles(page, per_page)
    
    if len(articles) == 0:
        return jsonify(error='Not found'), 404

    return jsonify(articles)

@home_bp.route('/articles/families')
@home_bp.route('/articles/families/<int:family_id>')
def families_articles(family_id=None):
    if family_id:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        families = home_data.family_articles(family_id, page, per_page)
        
        if len(families) == 0:
            return jsonify(error='Not found'), 404
        
        return jsonify(families)
    
    families = home_data.all_families()
    
    if len(families) == 0:
            return jsonify(error='Not found'), 404
    
    return jsonify(families)


@home_bp.route('/articles/families/<int:family_id>/total')
def family_articles_total(family_id=None):
    total = home_data.family_articles_total(family_id)
    return jsonify(total=total)