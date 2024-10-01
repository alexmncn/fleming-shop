from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from app.services import admin_data


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/articles/feature', methods=['POST'])
def feature_article():
    codebar = request.args.get('codebar', None)
    
    if codebar:
        status = admin_data.feature_article(codebar)
        
        if status == True:
            return jsonify(message=f'Article "{codebar}" featured successfully.'), 200
        
        return jsonify(message='Error'), 500
    
    return jsonify(message='No codebar'), 400
    
    