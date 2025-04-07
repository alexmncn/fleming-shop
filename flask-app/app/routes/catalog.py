from flask import Blueprint, request, jsonify

from app.services import catalog_data

def_per_page = 20

catalog_bp = Blueprint('catalog', __name__)


@catalog_bp.route('/')
def home():
    return '<h1>Hello world</h1>'


@catalog_bp.route('/articles/total', methods=['GET'])
def all_articles_total():
    total = catalog_data.all_articles_total()
    return jsonify(total=total)


@catalog_bp.route('/articles/all/codebars', methods=['GET'])
def all_articles_codebars():
    codebars = catalog_data.all_articles_codebars()
    return jsonify(codebars)


@catalog_bp.route('/articles/all', methods=['GET'])
def all_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', def_per_page, type=int)
    order_by = request.args.get('order_by')
    direction = request.args.get('direction', 'asc')
    
    articles = catalog_data.all_articles(page, per_page, order_by, direction)
    
    if len(articles) == 0:
        return jsonify(error='Not found'), 404
    
    return jsonify(articles)


@catalog_bp.route('/articles/search', methods=['GET'])
def search_articles():
    search = request.args.get('search', None)
    filter = request.args.get('filter', 'detalle')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', def_per_page, type=int)
    
    articles = catalog_data.search_articles(search, filter, page, per_page)
    
    if articles is None:
        return jsonify(error='Error with filter or search value.'), 400
    elif len(articles) == 0:
        return jsonify(error='Not found'), 404
    
    return jsonify(articles)


@catalog_bp.route('/articles/search/total', methods=['GET'])
def search_articles_total():
    search = request.args.get('search', None)
    filter = request.args.get('filter', 'detalle')
    
    total = catalog_data.search_articles_total(search, filter)
    
    if total is None:
        return jsonify(error='Error with filter or search value.'), 400
    
    return jsonify(total=total)


@catalog_bp.route('/articles/featured/total', methods=['GET'])
def featured_articles_total():
    total = catalog_data.featured_articles_total()
    return jsonify(total=total)
    

@catalog_bp.route('/articles/featured', methods=['GET'])
def featured_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', def_per_page, type=int)
    
    articles = catalog_data.featured_articles(page, per_page)
    
    if len(articles) == 0:
        return jsonify(error='Not found'), 404
    
    return jsonify(articles)


@catalog_bp.route('/articles/new/total', methods=['GET'])
def new_articles_total():
    total = catalog_data.new_articles_total()
    return jsonify(total=total)


@catalog_bp.route('/articles/new', methods=['GET'])
def new_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', def_per_page, type=int)
    
    articles = catalog_data.new_articles(page, per_page)
    
    if len(articles) == 0:
        return jsonify(error='Not found'), 404

    return jsonify(articles)


@catalog_bp.route('/articles/families', methods=['GET'])
@catalog_bp.route('/articles/families/<int:family_id>', methods=['GET'])
def families_articles(family_id=None):
    if family_id:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', def_per_page, type=int)
        
        families = catalog_data.family_articles(family_id, page, per_page)
        
        if len(families) == 0:
            return jsonify(error='Not found'), 404
        
        return jsonify(families)
    
    families = catalog_data.all_families()
    
    if len(families) == 0:
            return jsonify(error='Not found'), 404
    
    return jsonify(families)


@catalog_bp.route('/articles/families/<int:family_id>/total', methods=['GET'])
def family_articles_total(family_id=None):
    total = catalog_data.family_articles_total(family_id)
    return jsonify(total=total)