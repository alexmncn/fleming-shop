from app.extensions import db
from app.models import User

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return True  
    return False


def register(username, password):
    # Check if a user with the same username existing_user
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return 409

    # Creates the new user instance and set password
    new_user = User(username=username)
    new_user.set_password(password)

    # Add new user to database
    db.session.add(new_user)
    db.session.commit()
    
    return 200