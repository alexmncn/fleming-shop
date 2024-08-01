from flask import Blueprint, request, jsonify

from app.services.home_data import all_articles, featured_articles


home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    return '<h1>Hello world</h1>'


@home_bp.route('/articles/all')
def data_():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    articulos = all_articles(page, per_page)
            
    return jsonify(articulos)


@home_bp.route('/articles/featured')
def featured_a():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    articulos = featured_articles(page, per_page)
    
    return jsonify(articulos)