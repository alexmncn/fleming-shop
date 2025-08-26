from sqlalchemy import select

from app.extensions import db
from app.models import Article


def all_articles():
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