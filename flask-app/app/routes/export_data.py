import os
from openpyxl import Workbook
from flask import Blueprint, Response, request, abort, send_file, current_app
from flask_jwt_extended import jwt_required

from app.services import export_data
from app.config import UPLOAD_ROUTE

export_data_bp = Blueprint('export_data', __name__)


@export_data_bp.route('/data/export/articles')
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
        pass
    elif format == 'dbf':
        data_path = os.path.join(current_app.root_path, UPLOAD_ROUTE)
        files = [f for f in os.listdir(data_path) if f.startswith("articulo") and f.endswith(".dbf")]

        if not files:
            return abort(404, "Archivo de artículos no encontrado")

        file_name = files[0]
        file_path = os.path.join(data_path, file_name)

        return send_file(file_path, as_attachment=True, download_name=file_name, mimetype="application/octet-stream")
    
    return response