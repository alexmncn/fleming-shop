"""Database models"""
import pytz
from datetime import datetime, timedelta
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.mysql import TINYINT, BIGINT

from .extensions import db


class Article(db.Model):
    __tablename__ = "article"
    ref = db.Column(BIGINT, nullable=False)
    detalle = db.Column(db.String(50), nullable=True)
    codfam = db.Column(db.Integer, db.ForeignKey('family.codfam'), index=True, nullable=True)
    pcosto = db.Column(db.Float, nullable=True)
    pvp = db.Column(db.Float, nullable=False)
    codebar = db.Column(BIGINT, primary_key=True, autoincrement=False, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=True)
    factualizacion = db.Column(db.DateTime, nullable=True)
    destacado = db.Column(TINYINT(1), default=0, nullable=True)
    hidden = db.Column(TINYINT(1), default=0, nullable=True)
    
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
            'destacado': bool(self.destacado),
            'hidden': bool(self.hidden)
        }
        
    def to_dict_reduced(self):
        return {
            'ref': self.ref,
            'codebar': self.codebar, 
            'detalle': self.detalle, 
            'codfam': self.codfam,  
            'pvp': self.pvp,
            'stock': self.stock,
            'destacado': bool(self.destacado)
        }
        
    def to_dict_og_keys(self):
        return {
            'CREF': self.ref, 
            'CDETALLE': self.detalle, 
            'CCODFAM': self.codfam, 
            'NCOSTEDIV': self.pcosto, 
            'NPVP': self.pvp, 
            'CCODEBAR': self.codebar, 
            'NSTOCKMIN': self.stock, 
            'DACTUALIZA': self.factualizacion,
            'destacado': bool(self.destacado),
            'hidden': bool(self.hidden)
        }
    

class Family(db.Model):
    __tablename__= "family"
    codfam = db.Column(db.Integer, primary_key=True, nullable=False)
    nomfam = db.Column(db.String(50), nullable=False),
    hidden = db.Column(TINYINT(1), default=0, nullable=True)
    
    def to_dict(self):
        return {
            'codfam': self.codfam, 
            'nomfam': self.nomfam,
            'hidden': self.hidden
        }

    def to_dict_reduced(self):
        return {
            'codfam': self.codfam, 
            'nomfam': self.nomfam
        }
        
        
class User(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Madrid')), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
class OTPCode(db.Model):
    __tablename__ = 'otp_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    expires_at = db.Column(db.DateTime, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)

    def __init__(self, username, otp_code):
        self.username = username
        self.otp_code = otp_code
        self.expires_at = datetime.now() + timedelta(minutes=5)