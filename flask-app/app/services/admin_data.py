
from app.extensions import db
from app.models import Article


def feature_article(codebar):
    session = db.session
    n_updates = session.query(Article).filter(Article.codebar==codebar).update({Article.destacado: True})
    
    if n_updates == 1:
        session.commit()
        return True
    
    session.close()
    return False