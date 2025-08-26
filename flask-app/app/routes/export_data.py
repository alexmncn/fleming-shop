import csv
import io
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
