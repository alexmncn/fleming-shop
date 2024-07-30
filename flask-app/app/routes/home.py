from flask import Blueprint, jsonify

from app.services.data import data


home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    return '<h1>Hello world</h1>'

@home_bp.route('/data')
def data_():
    articulo = data()
    return jsonify(ref=articulo.ref, detalle=articulo.detalle, codfam=articulo.codfam, detallefam=articulo.detallefam, pcosto=articulo.pcosto, pvp=articulo.pvp, codebar=articulo.codebar, stock=articulo.stock, factualizacion=articulo.factualizacion)