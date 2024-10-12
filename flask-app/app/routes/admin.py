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