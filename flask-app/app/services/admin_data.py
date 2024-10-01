from app.extensions import db
from app.models import Article
from app.services.pushover_alerts import send_alert

def feature_article(codebar):
    try:    
        session = db.session
        updated_rows = session.query(Article).filter(Article.codebar==codebar).update({Article.destacado: True})
        
        if updated_rows == 1:
            session.commit()
            session.close()
            
            send_alert(f'Se ha destacado el articulo con <b>codebar: {codebar}</b>', -1)
            return True 
        
        session.close()
        return False
    except Exception as e:
        send_alert(f'Error al destacar el articulo con <b>codebar: {codebar}</b>:\n {e}', 0)
        return e