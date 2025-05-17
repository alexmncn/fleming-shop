from datetime import datetime

from app.extensions import db
from app.models import Article, Family, DailySales, Ticket, TicketItem
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
                message = f'Se ha ocultado el articulo con <b>codebar: {codebar}</b>'
            else:
                message = f'Se ha eliminado de ocultos el articulo con <b>codebar: {codebar}</b>'
            
            send_alert(message, -1)
            return True 
        
        session.close()
        return False
    except Exception as e:
        if hidden is True:
            send_alert(f'Error al ocultar el articulo con <b>codebar: {codebar}</b>:\n {e}', 0)
        else:
            send_alert(f'Error al eliminar de ocultos el articulo con <b>codebar: {codebar}</b>:\n {e}', 0)
            
        return e
    
def hide_family(codfam, hidden):
    try:    
        session = db.session
        updated_rows = session.query(Family).filter(Family.codfam==codfam).update({Family.hidden: hidden})
        
        if updated_rows == 1:
            session.commit()
            session.close()
            
            if hidden is True:
                message = f'Se ha ocultado la familia con <b>codigo: {codfam}</b>'
            else:
                message = f'Se ha eliminado de ocultos la familia con <b>codigo: {codfam}</b>'
            
            send_alert(message, -1)
            return True 
        
        session.close()
        return False
    except Exception as e:
        if hidden is True:
            send_alert(f'Error al ocultar la familia con <b>codigo: {codfam}</b>:\n {e}', 0)
        else:
            send_alert(f'Error al eliminar de ocultos la familia con <b>codigo: {codfam}</b>:\n {e}', 0)
        return e
    
def hide_family_articles(codfam, hidden):
    try:    
        session = db.session
        updated_rows = session.query(Article).filter(Article.codfam==codfam).update({Article.hidden: hidden})
        
        if updated_rows >= 1:
            session.commit()
            session.close()
            
            if hidden is True:
                message = f'Se han ocultado {updated_rows} articulos de la familia con <b>codigo: {codfam}</b>'
            else:
                message = f'Se han eliminado de ocultos {updated_rows} articulos de la familia con <b>codigo: {codfam}</b>'
            
            send_alert(message, -1)
            return True 
        
        session.close()
        return False
    except Exception as e:
        if hidden is True:
            send_alert(f'Error al ocultar los articulos de la familia con <b>codigo: {codfam}</b>:\n {e}', 0)
        else:
            send_alert(f'Error al eliminar de ocultos los articulos de la familia con <b>codigo: {codfam}</b>:\n {e}', 0)
        return e
    
     
def all_daily_sales():
    return [ds.to_dict() for ds in DailySales.query.all()]

def all_daily_sales_dates():
   return [ds.date.strftime('%d-%m-%Y') for ds in DailySales.query.with_entities(DailySales.date).distinct().all()]
 
def day_sales(date_str):
    try:
        date = datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        return []
    
    return [ds.to_dict() for ds in DailySales.query.filter(DailySales.date==date).all()]

def all_tickets_of_day(date_str):
    try:
        date = datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        return []
    
    return [ticket.to_dict() for ticket in Ticket.query.filter(Ticket.closed_at==date).all()]
    
def all_items_of_ticket(ticket_number):
    return [ticket_item.to_dict() for ticket_item in TicketItem.query.filter(TicketItem.ticket_number==ticket_number).all()]