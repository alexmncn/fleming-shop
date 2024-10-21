"""The app module, containing the app factory function."""
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from app.extensions import db, migrate, jwt
from app.routes import catalog, load_data, auth, admin

def create_app(config_object="app.config"):
    # Create application factory. Param config_object, the configuration object to use.
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_blueprints(app)
    register_extensions(app)
    set_CORS(app)
    set_proxyFix(app)
    return app

def register_extensions(app):
    # Initialize the extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

def register_blueprints(app):
    # Register Flask blueprints.
    app.register_blueprint(catalog.catalog_bp)
    app.register_blueprint(load_data.load_data_bp)
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(admin.admin_bp)

def set_CORS(app):
    # Set CORS allowed domains
    CORS(app, origins=['http://localhost:4200', 'https://4scw20tt-4200.uks1.devtunnels.ms', 'https://tiendafleming.es'])

def set_proxyFix(app):
    # Set proxy middleware to get the host original data 
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
    
