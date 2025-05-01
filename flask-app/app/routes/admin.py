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
@jwt_required()
def hide_family():
    codfam = request.args.get('codfam', None, int)
    hidden = request.args.get('hidden', 'true') in ['True','true', '1', 'yes', 'y']
    recursive = request.args.get('recursive', 'true') in ['True','true', '1', 'yes', 'y']
    
    if codfam:
        status = admin_data.hide_family(codfam, hidden)
        
        if status == True:
            if hidden == True:
                message = f'Family with code `{codfam}` successfully hidden.'
            else:
                message = f'Family with code `{codfam}` removed from hidden.'
                
            if recursive == True:
                # Llamada interna a la función que oculta los artículos
                articles_status = admin_data.hide_family_articles(codfam, hidden)
                
                if articles_status == True:
                    message += f' Articles from family `{codfam}` successfully hidden.' if hidden else f' Articles from family `{codfam}` removed from hidden.'
                else:
                    return jsonify(error=f'Failed to hide articles for family with code `{codfam}`.'), 500
                
            return jsonify(message=message), 200
        
        elif status == False:
            return jsonify(error=f'No family with code `{codfam}` in database.'), 404

        return jsonify(error='Internal error.'), 500
        
    return jsonify(error='No codebar in request.'), 400

@admin_bp.route('/family/articles/hide', methods=['POST'])
@jwt_required()
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


@admin_bp.route('/sales/daily_sales', methods=['GET'])
#@jwt_required()
def daily_sales():
    return admin_data.all_daily_sales()

@admin_bp.route('/sales/daily_sales/dates', methods=['GET'])
#@jwt_required()
def daily_sales_dates():
    return admin_data.all_daily_sales_dates()

@admin_bp.route('/sales/day_sales', methods=['GET'])
#@jwt_required()
def daily_sales_():
    date = request.args.get('date', None, str)
    if date:
        return admin_data.day_sales(date)
    
    return jsonify(error='No date in request.'), 400

@admin_bp.route('/sales/day_sales/tickets', methods=['GET'])
#@jwt_required()
def day_sales_tickets():
    date = request.args.get('date', None, str)
    if date:
        return admin_data.all_tickets_of_day(date)
    
    return jsonify(error='No date in request.'), 400

@admin_bp.route('/sales/day_sales/ticket/items', methods=['GET'])
#@jwt_required()
def ticket_items():
    ticket_number = request.args.get('ticket_number', None, int)
    if ticket_number:
        return admin_data.all_items_of_ticket(ticket_number)

    return jsonify(error='Invalid ticket number in request.'), 400