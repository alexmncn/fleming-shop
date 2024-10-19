from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services import admin_data


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/articles/feature', methods=['POST'])
@jwt_required()
def feature_article():
    codebar = request.args.get('codebar', None, int)
    featured = request.args.get('featured', 'true') in ['True','true', '1', 'yes', 'y']

    if codebar:
        status = admin_data.feature_article(codebar, featured)
        
        if status == True:
            if featured == True:
                message=f'Article with codebar `{codebar}` featured successfully.'
            else:
                message = f'Article with codebar `{codebar}` removed from featured successfully.'
            return jsonify(message=message), 200
        
        elif status == False:
            return jsonify(error=f'No articles with codebar `{codebar}` in database.'), 404
        
        return jsonify(error='Internal error.'), 500
    
    return jsonify(error='No codebar in request.'), 400


@admin_bp.route('/articles/hide', methods=['POST'])
@jwt_required()
def hide_article():
    codebar = request.args.get('codebar', None, int)
    hidden = request.args.get('hidden', 'true') in ['True','true', '1', 'yes', 'y']
    
    if codebar:
        status = admin_data.hide_article(codebar, hidden)
        
        if status == True:
            if hidden == True:
                message = f'Article with codebar `{codebar}` successfully hidden.'
            else:
                message = f'Article with codebar `{codebar}` removed from hidden.'
            return jsonify(message=message), 200
        
        elif status == False:
            return jsonify(error=f'No articles with codebar `{codebar}` in database.'), 404

        return jsonify(error='Internal error.'), 500
        
    return jsonify(error='No codebar in request.'), 400


@admin_bp.route('/families/hide', methods=['POST'])

def hide_family():
    codfam = request.args.get('codfam', None, int)
    hidden = request.args.get('hidden', 'true') in ['True','true', '1', 'yes', 'y']
    
    if codfam:
        status = admin_data.hide_family(codfam, hidden)
        
        if status == True:
            if hidden == True:
                message = f'Family with code `{codfam}` successfully hidden.'
            else:
                message = f'Family with code `{codfam}` removed from hidden.'
            return jsonify(message=message), 200
        
        elif status == False:
            return jsonify(error=f'No family with code `{codfam}` in database.'), 404

        return jsonify(error='Internal error.'), 500
        
    return jsonify(error='No codebar in request.'), 400


@admin_bp.route('/family/articles/hide', methods=['POST'])

def hide_family_articles():
    codfam = request.args.get('codfam', None, int)
    hidden = request.args.get('hidden', 'true') in ['True','true', '1', 'yes', 'y']
    
    if codfam:
        status = admin_data.hide_family_articles(codfam, hidden)
        
        if status == True:
            if hidden == True:
                message = f'Articles from family with code `{codfam}` successfully hidden.'
            else:
                message = f'Articles from family with code `{codfam}` removed from hidden.'
            return jsonify(message=message), 200
        
        elif status == False:
            return jsonify(error=f'No family with code `{codfam}` in database.'), 404

        return jsonify(error='Internal error.'), 500
        
    return jsonify(error='No codebar in request.'), 400