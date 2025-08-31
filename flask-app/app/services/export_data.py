import csv
import io
import os
from openpyxl import Workbook
from sqlalchemy import select

from app.extensions import db
from app.models import Article
from app.config import UPLOAD_ROUTE


def get_all_articles():
    stmt = select(
        Article.codebar,
        Article.ref,
        Article.codfam,
        Article.detalle,
        Article.pcosto,
        Article.pvp,
        Article.stock,
        Article.factualizacion,
        Article.date_created
    )
    
    articles = db.session.execute(stmt).mappings().all()
    
    formatted_articles = []
    for row in articles:
        row = dict(row)
        if row.get("pcosto") is not None:
            row["pcosto"] = f"{row['pcosto']:.2f}"
        if row.get("pvp") is not None:
            row["pvp"] = f"{row['pvp']:.2f}"
        formatted_articles.append(row)
    return formatted_articles

def articles_csv():
    # Obtener todos los artículos
    articles = get_all_articles()

    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=articles[0].keys())
    writer.writeheader()
    writer.writerows(articles)
    
    return output.getvalue()

def articles_xlsx():
    # Obtener artículos (lista de dicts)
    articles = get_all_articles()

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
    
    return output.read()

def articles_pdf():
    pass