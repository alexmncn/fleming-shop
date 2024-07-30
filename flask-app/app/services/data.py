
from app.models import articulo

def data():
    return articulo.query.first()