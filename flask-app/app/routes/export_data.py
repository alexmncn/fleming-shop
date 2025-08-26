import csv
import io
from openpyxl import Workbook
from flask import Blueprint, Response
from flask_jwt_extended import jwt_required


from app.services import export_data

export_data_bp = Blueprint('export_data', __name__)


@export_data_bp.route("/data/export/articles.csv")
@jwt_required()
def export_articles_csv():
    # Obtener todos los artículos
    articles = export_data.all_articles()

    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=articles[0].keys())
    writer.writeheader()
    writer.writerows(articles)


    # Devolver CSV como descarga
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=articulos.csv"
    return response


@export_data_bp.route("/data/export/articles.xlsx")
@jwt_required(optional=True)
def export_articles_xlsx():
    # Obtener artículos (lista de dicts)
    articles = export_data.all_articles()

    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Articulos"

    # Encabezados
    headers = list(articles[0].keys()) if articles else []
    ws.append(headers)

    # Filas
    for article in articles:
        row = []
        for key in headers:
            value = article[key]
            row.append(value)
        ws.append(row)

    # Guardar todo en un buffer en memoria
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Devolver archivo como descarga
    return Response(
        output.read(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=articulos.xlsx"}
    )