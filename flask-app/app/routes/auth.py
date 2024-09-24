from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from datetime import datetime, timedelta
import pytz


from app.extensions import jwt
from app.services.user import authenticate, register

auth_bp = Blueprint('auth', __name__)

blacklist = set()


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in blacklist


@auth_bp.route('/login', methods=['POST'])
def login():
    # User login
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user_authenticated = authenticate(username, password)
    
    if user_authenticated:
        expires_delta = timedelta(hours=1)
        expires_date = datetime.now(pytz.timezone('Europe/Madrid')) + expires_delta
        access_token = create_access_token(identity={'username': username}, expires_delta=expires_delta)
        return jsonify(token=access_token, expires_at=expires_date.isoformat(), username=username), 200
    
    return jsonify(message='Invalid credentials'), 401


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Logout.
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify(message='Logged out successfully'), 200


@auth_bp.route('/auth')
@jwt_required()
def auth():
    user = get_jwt_identity()
    return jsonify(user), 200


@auth_bp.route('/register', methods=['POST'])
def register_():
    # Register new user.
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    otp_code = data.get('otp', None)
    
    status = register(username, password, otp_code)
    
    if status == 201:
        return jsonify(message='Registered successfully'), 201
    elif status == 303:
        return jsonify(message='Verify OTP code to complete the register'), 303
    elif status == 422:
        return jsonify(message='Invalid OTP code'), 422
    elif status == 410:
        return jsonify(message='OTP code has expired'), 410
    elif status == 409:
        return jsonify(message='This user already exists'), 409
    elif status == 500:
        return jsonify(message='Internal Error'), 500