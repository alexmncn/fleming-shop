"""Database models"""
from sqlalchemy.dialects.mysql import TINYINT, BIGINT

from .extensions import db

# article
class article(db.Model):
    __tablename__ = "article"
    ref = db.Column(BIGINT, nullable=False)
    detalle = db.Column(db.String(50), nullable=True)
    codfam = db.Column(db.Integer, db.ForeignKey('family.codfam'), index=True, nullable=True)
    pcosto = db.Column(db.Float, nullable=True)
    pvp = db.Column(db.Float, nullable=False)
    codebar = db.Column(BIGINT, primary_key=True, autoincrement=False, nullable=False)
    stock = db.Column(db.Integer, nullable=True)
    factualizacion = db.Column(db.DateTime, nullable=True)
    destacado = db.Column(TINYINT(1), default=0, nullable=True)
    
    def to_dict(self):
        return {
            'ref': self.ref, 
            'detalle': self.detalle, 
            'codfam': self.codfam, 
            'pcosto': self.pcosto, 
            'pvp': self.pvp, 
            'codebar': self.codebar, 
            'stock': self.stock, 
            'factualizacion': self.factualizacion,
            'destacado': bool(self.destacado)
        }
    

class family(db.Model):
    __tablename__= "family"
    codfam = db.Column(db.Integer, primary_key=True, nullable=False)
    nomfam = db.Column(db.String(50), nullable=False)
    