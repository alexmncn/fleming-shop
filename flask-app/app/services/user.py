import secrets, string, pytz, requests
from datetime import datetime

from app.extensions import db
from app.models import User, OTPCode
from app.services.pushover_alerts import send_alert

from app.config import TURNSTILE_VERIFY_URL, TURNSTILE_SECRET_KEY

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        try:    
            send_alert(f'<b>{username}</b> ha iniciado sesión.', 0) # Send login alert
            # Update last login
            User.query.filter_by(username=username).update(dict(last_login=datetime.now(pytz.timezone('Europe/Madrid'))))
            db.session.commit()
        except:
            pass
        return True  
    return False


def register(username, password, otp_code):
    # Check if a user with the same username existing_user
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return 409
    
    if not otp_code:
        # Generate otp and update status to user
        status = generate_otp(username)
        
        if status is True:
            return 303
        else: 
            return 500
    
    else:
        status, code = verify_otp(username, otp_code)
        
        if status is True:
            try:
                # Creates the new user instance and set password
                new_user = User(username=username)
                new_user.set_password(password)

                # Add new user to database
                db.session.add(new_user)
                db.session.commit()
            except:
                return 500
            
            try:
                send_alert(f'<b>{username}</b> se ha registrado', 1)
            except:
                pass
            return 201
        else:
            return code


def generate_otp(username):
    length=6
    otp_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    
    otp = OTPCode(username=username, otp_code=otp_code)
    
    db.session.add(otp)
    db.session.commit()
    
    otp_alert = f"El usuario <b>{username}</b> intenta registrarse. Código OTP: {otp_code}"
    send_alert(message=otp_alert, priority=-1)

    return True


def verify_otp(username, otp):
    otp_code = OTPCode.query.filter_by(username=username, otp_code=otp, is_valid=True).first()

    if not otp_code:
        return False, 422

    # Verify if OTP has expired
    if datetime.now() > otp_code.expires_at:
        return False, 410

    # Mark code as invalid
    otp_code.is_valid = False
    db.session.commit()

    return True, 200


def verify_turnstile(f_turnstile_response):
    verify_response = requests.post(TURNSTILE_VERIFY_URL, { 'secret': TURNSTILE_SECRET_KEY, 'response': f_turnstile_response })

    verified = verify_response.json().get('success')
    
    return verified