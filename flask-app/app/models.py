"""Database models"""
import pytz
import uuid
from datetime import datetime, timedelta
from flask import url_for
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, Text, Float, DateTime, Date, Time, ForeignKey, Index
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.mysql import TINYINT

from .extensions import db


class Article(db.Model):
    __tablename__ = "article"
    __table_args__ = (
        Index('detalle_index', 'detalle', mysql_prefix='FULLTEXT'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci'
        }
    )
    
    ref = Column(String(50), nullable=False)
    detalle = Column(String(100), nullable=True)
    codfam = Column(Integer, ForeignKey('family.codfam'), index=True, nullable=True)
    pcosto = Column(Float, nullable=True)
    pvp = Column(Float, nullable=False)
    codebar = Column(String(50), primary_key=True, autoincrement=False, nullable=False)
    stock = Column(Integer, default=0, nullable=True)
    factualizacion = Column(DateTime, nullable=True)
    date_created = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Madrid')), nullable=True)
    destacado = Column(TINYINT(1), default=0, nullable=True)
    hidden = Column(TINYINT(1), default=0, nullable=True)
    
    @property
    def has_image(self):
        return db.session.query(ArticleImage.query.filter_by(article_codebar=self.codebar).exists()).scalar()

    @property
    def image_url(self):
        img = ArticleImage.query.filter_by(article_codebar=self.codebar, is_main=True).first()
        if img:
            return url_for('images.get_article_image', image_id=img.id, _external=True, _scheme="https")
        return None

    @property
    def image_urls(self):
        return [
            url_for('images.get_article_image', image_id=img.id, _external=True, _scheme="https")
            for img in ArticleImage.query.filter_by(article_codebar=self.codebar).all()
        ]
    
    def to_dict(self, include_images=False):
        data = {
            'ref': self.ref, 
            'detalle': self.detalle, 
            'codfam': self.codfam, 
            'pcosto': self.pcosto, 
            'pvp': self.pvp, 
            'codebar': self.codebar, 
            'stock': self.stock, 
            'factualizacion': self.factualizacion,
            'date_created': self.date_created,
            'destacado': bool(self.destacado),
            'hidden': bool(self.hidden),
            'has_image': self.has_image,
            'image_url': self.image_url
        }
        if include_images:
            data['image_urls'] = self.image_urls
        return data
        
    def to_dict_reduced(self, include_images=False):
        data = {
            'ref': self.ref,
            'codebar': self.codebar, 
            'detalle': self.detalle, 
            'codfam': self.codfam,  
            'pvp': self.pvp,
            'stock': self.stock,
            'destacado': bool(self.destacado),
            'has_image': self.has_image,
            'image_url': self.image_url
        }
        if include_images:
            data['image_urls'] = self.image_urls
        return data
        
class ArticleImage(db.Model):
    __tablename__ = "article_images"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    id = Column(String(100), primary_key=True)
    article_codebar = Column(db.String(50), nullable=False, index=True)
    filename = Column(String(100), nullable=False)
    is_main = Column(TINYINT(1), default=0, nullable=True)
    
    @property
    def url(self):
        return url_for('images.get_article_image', image_id=self.id, _external=True, _scheme="https")
    
    def to_dict(self):
        return {
            'id': self.id,
            'article_codebar': self.article_codebar,
            'filename': self.filename,
            'is_main': bool(self.is_main),
            'url': self.url
        }

class Family(db.Model):
    __tablename__= "family"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    codfam = Column(Integer, primary_key=True, nullable=False)
    nomfam = Column(String(50), nullable=False)
    hidden = Column(TINYINT(1), default=0, nullable=True)
    
    def to_dict(self):
        return {
            'codfam': self.codfam,
            'nomfam': self.nomfam,
            'hidden': bool(self.hidden)
        }

    def to_dict_reduced(self):
        return {
            'codfam': self.codfam,
            'nomfam': self.nomfam
        }

        
class Article_import(db.Model):
    __tablename__="article_imports"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, db.ForeignKey('users.id'), index=True, nullable=True)
    status = Column(TINYINT(1), default=1, nullable=True)
    info = Column(Text, nullable=True)
    new_rows = Column(Integer, default=0)
    updated_rows = Column(Integer, default=0)
    deleted_rows = Column(Integer, default=0)
    duplicated_rows = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    corrected = Column(Integer, default=0)
    elapsed_time = Column(Float, nullable=True)
    date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Madrid')), nullable=False)
    
    logs = relationship('Article_import_log', back_populates='import_record')
    
class Article_import_log(db.Model):
    __tablename__="article_import_logs"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    import_id = Column(String(36), ForeignKey('article_imports.id'), nullable=False)
    type = Column(Integer, nullable=False)
    ref = Column(String(50), nullable=True)
    codebar = Column(String(50), nullable=True)
    detalle = Column(String(100), nullable=True)
    info = Column(Text, nullable=True)
    
    import_record = relationship('Article_import', back_populates='logs')
        
        
class DailySales(db.Model):
    __tablename__ = 'daily_sales'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    date = Column(Date, primary_key=True)
    counter = Column(Integer, primary_key=True)
    time = Column(Time, nullable=True)
    first_ticket = Column(Integer, nullable=False)
    last_ticket = Column(Integer, nullable=False)
    total_sold = Column(Float, nullable=False)
    previous_balance = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False)

    tickets = relationship("Ticket", back_populates="daily_summary")
    
    def to_dict(self):
        return {
            'date': self.date.strftime('%d-%m-%Y'),
            'counter': self.counter,
            'time': self.time.strftime('%H:%M'),
            'first_ticket': self.first_ticket,
            'last_ticket': self.last_ticket,
            'total_sold': self.total_sold,
            'previous_balance': self.previous_balance,
            'current_balance': self.current_balance
        }

class Ticket(db.Model):
    __tablename__ = 'tickets'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    number = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    closed_at = Column(Date, ForeignKey('daily_sales.date'), nullable=True)

    daily_summary = relationship("DailySales", back_populates="tickets")
    items = relationship("TicketItem", back_populates="ticket")
    
    def to_dict(self):
        return {
            'number': self.number,
            'date': self.date.strftime('%d-%m-%Y'),
            'amount': self.amount,
            'closed_at': self.closed_at.strftime('%d-%m-%Y')
        }

class TicketItem(db.Model):
    __tablename__ = 'ticket_items'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_number = Column(Integer, ForeignKey('tickets.number'), nullable=False)
    ref = Column(String(50), nullable=True, index=True)
    codebar = Column(String(50), nullable=True, index=True)
    detalle = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    ticket = relationship("Ticket", back_populates="items")

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_number': self.ticket_number,
            'ref': self.ref,
            'codebar': self.codebar,
            'detalle': self.detalle,
            'quantity': self.quantity,
            'unit_price': self.unit_price
        }

        
class User(UserMixin,db.Model):
    __tablename__ = "users"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    last_login = Column(DateTime, nullable=True)
    date_created = Column(DateTime, default=datetime.now(pytz.timezone('Europe/Madrid')), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
class OTPCode(db.Model):
    __tablename__ = 'otp_codes'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }
    
    id = Column(db.Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    otp_code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    expires_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True)

    def __init__(self, username, otp_code):
        self.username = username
        self.otp_code = otp_code
        self.expires_at = datetime.now() + timedelta(minutes=5)