from app.extensions import db
from app.models import Article
from app.services.pushover_alerts import send_alert

def feature_article(codebar, featured):
    try:    
        session = db.session
        updated_rows = session.query(Article).filter(Article.codebar==codebar).update({Article.destacado: featured})
        
        if updated_rows == 1:
            session.commit()
            session.close()
            
            if featured is True:
                message = f'Se ha destacado el articulo con <b>codebar: {codebar}</b>'
            else:
                message = f'Se ha eliminado de destacados el articulo con <b>codebar: {codebar}</b>'
            
            send_alert(message, -1)
            return True 
        
        session.close()
        return False
    except Exception as e:
        send_alert(f'Error al destacar el articulo con <b>codebar: {codebar}</b>:\n {e}', 0)
        return e
    
    
def hide_article(codebar, hidden):
    try:    
        session = db.session
        updated_rows = session.query(Article).filter(Article.codebar==codebar).update({Article.hidden: hidden})
        
        if updated_rows == 1:
            session.commit()
            session.close()
            
            if hidden is True:
                message = f'Se ha destacado el articulo con <b>codebar: {codebar}</b>'
            else:
                message = f'Se ha eliminado de destacados el articulo con <b>codebar: {codebar}</b>'
            
            send_alert(message, -1)
            return True 
        
        session.close()
        return False
    except Exception as e:
        send_alert(f'Error al destacar el articulo con <b>codebar: {codebar}</b>:\n {e}', 0)
        return e