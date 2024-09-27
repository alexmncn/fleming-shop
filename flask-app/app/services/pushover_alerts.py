import http.client, urllib
from app.config import PUSHOVER_APP_TOKEN, PUSHOVER_USER_KEY


def send_alert(message, priority):
    if priority == 2:
        retry = 60
        expire = 300
    else:
        retry = None
        expire = None
    
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    
    conn.request('POST', '/1/messages.json',
        urllib.parse.urlencode({
            'token': PUSHOVER_APP_TOKEN,
            'user': PUSHOVER_USER_KEY,
            'message': message,
            'priority': priority,
            'retry': retry,
            'expire': expire,
            'html': 1
        }), 
        { 'Content-type': 'application/x-www-form-urlencoded' })
        
    conn.getresponse()