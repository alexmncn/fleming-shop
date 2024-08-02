from flask import Blueprint, request, jsonify

from app.services.home_data import all_articles, featured_articles, all_families, family_articles


home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    return '<h1>Hello world</h1>'


@home_bp.route('/articles/all')
def all_articles_():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    articulos = all_articles(page, per_page)
            
    return jsonify(articulos)


@home_bp.route('/articles/featured')
def featured_articles_():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    articulos = featured_articles(page, per_page)
    
    return jsonify(articulos)


@home_bp.route('/articles/families')
@home_bp.route('/articles/families/<int:family_id>')
def articles_families_(family_id=None):
    if family_id:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        return jsonify(family_articles(family_id, page, per_page))
    
    return jsonify(all_families())