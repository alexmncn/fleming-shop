import csv
import io
from openpyxl import Workbook
from sqlalchemy import select
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.extensions import db
from app.models import Article
from app.services import catalog_data


def get_all_articles():
    stmt = select(
        Article.codebar,
        Article.ref,
        Article.codfam,
        Article.detalle,
        Article.pcosto,
        Article.pvp,
        Article.stock,
        Article.factualizacion
    )
    
    articles = db.session.execute(stmt).mappings().all()
    
    formatted_articles = []
    for row in articles:
        row = dict(row)
        if row.get("pcosto") is not None:
            row["pcosto"] = f"{row['pcosto']:.2f}"
        if row.get("pvp") is not None:
            row["pvp"] = f"{row['pvp']:.2f}"
        if row.get("factualizacion") is not None:
            # Formato: YYYY-MM-DD
            row["factualizacion"] = row["factualizacion"].strftime("%d-%m-%Y")
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
    
    return output.getvalue()

def articles_pdf():
    articles = get_all_articles()
    
    output = io.BytesIO()

    if not articles:
        return output

    # Documento en vertical (portrait)
    left_margin = right_margin = top_margin = bottom_margin = 36
    doc = SimpleDocTemplate(
        output,
        pagesize=letter,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin
    )

    # Estilos
    styles = getSampleStyleSheet()
    style_body = styles["BodyText"]
    style_body.fontSize = 8  # cuerpo más pequeño
    style_body.leading = 10
    style_body.alignment = 0  # izquierda

    # Encabezados
    headers = list(articles[0].keys())
    data = [headers]

    # Filas
    for art in articles:
        row = [Paragraph(str(art.get(key, "")), style_body) for key in headers]
        data.append(row)

    # Calcular anchos
    available_width = doc.pagesize[0] - (left_margin + right_margin)

    col_widths = []
    for key in headers:
        if key.lower() in ("detalle", "description", "nombre"):  # campo largo
            col_widths.append(available_width * 0.25)  # 25% del ancho
        elif key.lower() in ("pcosto", "pvp", "codfam", "stock"):
            col_widths.append(available_width * 0.08)  # 8% del ancho
        elif key.lower() in ("ref"):
            col_widths.append(available_width * 0.10)  # 10% del ancho
        else:
            col_widths.append(available_width * 0.12)  # reparto para los demás

    # Normalizar: si la suma no da exacto, escalar
    factor = available_width / sum(col_widths)
    col_widths = [w * factor for w in col_widths]

    # Tabla
    table = Table(data, colWidths=col_widths, repeatRows=1)

    # Estilos
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ])
    
    for i in range(1, len(data)):
        bg_color = colors.white if i % 2 == 0 else colors.aliceblue
        table_style.add('BACKGROUND', (0, i), (-1, i), bg_color)

    table.setStyle(table_style)

    # Construcción
    elements = []
    title = Paragraph("Listado de Artículos", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))
    elements.append(table)

    doc.build(elements)
    output.seek(0)
    return output


def get_all_families():
    families = catalog_data.all_families()

    # Remove 'hidden' field
    for fam in families:
        fam.pop('hidden', None)
    return families

def families_csv():
    families = get_all_families()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=families[0].keys())
    writer.writeheader()
    writer.writerows(families)
    return output.getvalue()

def families_xlsx():
    families = get_all_families()

    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Familias"

    # Encabezados
    headers = list(families[0].keys()) if families else []
    ws.append(headers)

    # Filas
    for family in families:
        row = []
        for key in headers:
            value = family[key]
            row.append(value)
        ws.append(row)

    # Guardar todo en un buffer en memoria
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output.getvalue()

def families_pdf():
    families = get_all_families()

    output = io.BytesIO()

    if not families:
        return output

    # Documento en vertical (portrait)
    left_margin = right_margin = top_margin = bottom_margin = 36
    doc = SimpleDocTemplate(
        output,
        pagesize=letter,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin
    )

    # Estilos
    styles = getSampleStyleSheet()
    style_body = styles["BodyText"]
    style_body.fontSize = 10
    style_body.leading = 12
    style_body.alignment = 0  # izquierda

    # Encabezados
    headers = list(families[0].keys())
    data = [headers]

    # Filas
    for fam in families:
        row = [Paragraph(str(fam.get(key, "")), style_body) for key in headers]
        data.append(row)

    # Tabla
    table = Table(data, repeatRows=1)

    # Estilos
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ])
    
    # Alternar colores de filas
    for i in range(1, len(data)):
        bg_color = colors.white if i % 2 == 0 else colors.aliceblue
        table_style.add('BACKGROUND', (0, i), (-1, i), bg_color)

    table.setStyle(table_style)

    # Construcción
    elements = []
    title = Paragraph("Listado de Familias", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))
    elements.append(table)

    doc.build(elements)
    output.seek(0)
    return output