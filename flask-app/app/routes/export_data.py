import os
from openpyxl import Workbook
from flask import Blueprint, Response, request, abort, send_file, current_app
from flask_jwt_extended import jwt_required

from app.services import export_data
from app.config import UPLOAD_ROUTE

export_data_bp = Blueprint('export_data', __name__)


@export_data_bp.route('/data/export/articles')
@jwt_required()
def export_articles():
    format = request.args.get('format')
    
    if format == 'csv':
        articles = export_data.articles_csv()
        response = Response(articles)
        response.mimetype = "text/csv"
        response.headers = {"Content-Disposition": "attachment; filename=articulos.csv"}
    elif format == 'xlsx':
        articles = export_data.articles_xlsx()
        response = Response(articles)
        response.mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response.headers = {"Content-Disposition": "attachment; filename=articulos.xlsx"}
    elif format == 'pdf':
        articles = export_data.articles_pdf()
        response = Response(articles)
        response.mimetype = "application/pdf"
        response.headers = {"Content-Disposition": "attachment; filename=articulos.pdf"}
    elif format == 'dbf':
        data_path = os.path.join(current_app.root_path, UPLOAD_ROUTE)
        files = [f for f in os.listdir(data_path) if f.startswith("articulo") and f.endswith(".dbf")]

        if not files:
            return abort(404, "Archivo de artículos no encontrado")

        file_name = files[0]
        file_path = os.path.join(data_path, file_name)

        return send_file(file_path, as_attachment=True, download_name=file_name, mimetype="application/octet-stream")
    
    return response


@export_data_bp.route('/data/export/families')
@jwt_required()
def export_families():
    format = request.args.get('format')
    
    if format == 'csv':
        families = export_data.families_csv()
        response = Response(families)
        response.mimetype = "text/csv"
        response.headers = {"Content-Disposition": "attachment; filename=familias.csv"}
    elif format == 'xlsx':
        families = export_data.families_xlsx()
        response = Response(families)
        response.mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response.headers = {"Content-Disposition": "attachment; filename=familias.xlsx"}
    elif format == 'pdf':
        families = export_data.families_pdf()
        response = Response(families)
        response.mimetype = "application/pdf"
        response.headers = {"Content-Disposition": "attachment; filename=familias.pdf"}
    elif format == 'dbf':
        data_path = os.path.join(current_app.root_path, UPLOAD_ROUTE)
        files = [f for f in os.listdir(data_path) if f.startswith("familias") and f.endswith(".dbf")]

        if not files:
            return abort(404, "Archivo de familias no encontrado")

        file_name = files[0]
        file_path = os.path.join(data_path, file_name)

        return send_file(file_path, as_attachment=True, download_name=file_name, mimetype="application/octet-stream")

    return response


@export_data_bp.route('/data/export/cierres')
@jwt_required()
def export_cierres():
    format = request.args.get('format')
    
    if format == 'csv':
        return abort(501, "csv export not implemented yet")
    elif format == 'xlsx':
        return abort(501, "xlsx export not implemented yet")
    elif format == 'pdf':
        return abort(501, "PDF export not implemented yet")
    elif format == 'dbf':
        data_path = os.path.join(current_app.root_path, UPLOAD_ROUTE)
        files = [f for f in os.listdir(data_path) if f.startswith("cierre") and f.endswith(".dbf")]

        if not files:
            return abort(404, "Archivo de cierres no encontrado")

        file_name = files[0]
        file_path = os.path.join(data_path, file_name)

        return send_file(file_path, as_attachment=True, download_name=file_name, mimetype="application/octet-stream")
    
    
@export_data_bp.route('/data/export/movimientos')
@jwt_required()
def export_movimientos():
    format = request.args.get('format')
    
    if format == 'csv':
        return abort(501, "csv export not implemented yet")
    elif format == 'xlsx':
        return abort(501, "xlsx export not implemented yet")
    elif format == 'pdf':
        return abort(501, "PDF export not implemented yet")
    elif format == 'dbf':
        data_path = os.path.join(current_app.root_path, UPLOAD_ROUTE)
        files = [f for f in os.listdir(data_path) if f.startswith("movimt") and f.endswith(".dbf")]

        if not files:
            return abort(404, "Archivo de movimientos no encontrado")

        file_name = files[0]
        file_path = os.path.join(data_path, file_name)

        return send_file(file_path, as_attachment=True, download_name=file_name, mimetype="application/octet-stream")
    
    
@export_data_bp.route('/data/export/tickets')
@jwt_required()
def export_tickets():
    format = request.args.get('format')
    
    if format == 'csv':
        return abort(501, "csv export not implemented yet")
    elif format == 'xlsx':
        return abort(501, "xlsx export not implemented yet")
    elif format == 'pdf':
        return abort(501, "PDF export not implemented yet")
    elif format == 'dbf':
        data_path = os.path.join(current_app.root_path, UPLOAD_ROUTE)
        files = [f for f in os.listdir(data_path) if f.startswith("hticketl") and f.endswith(".dbf")]

        if not files:
            return abort(404, "Archivo de tickets no encontrado")

        file_name = files[0]
        file_path = os.path.join(data_path, file_name)

        return send_file(file_path, as_attachment=True, download_name=file_name, mimetype="application/octet-stream")