"""Database models"""
from .extensions import db

# article
class articulo(db.Model):
    __tablename__ = "articulo"
    ref = db.Column(db.Integer, nullable=False)
    detalle = db.Column(db.String(50), nullable=True)
    codfam = db.Column(db.Integer, nullable=True)
    detallefam = db.Column(db.String(50), nullable=True)
    pcosto = db.Column(db.Float, nullable=True)
    pvp = db.Column(db.Float, nullable=False)
    codebar = db.Column(db.Integer, primary_key=True, nullable=False)
    stock = db.Column(db.Integer, nullable=True)
    factualizacion = db.Column(db.DateTime, nullable=True)