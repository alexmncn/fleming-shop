"""The app module, containing the app factory function."""
from flask import Flask
from flask_cors import CORS

from app.extensions import db, migrate
from app.routes import home, load_data

def create_app(config_object="app.config"):
    # Create application factory. Param config_object, the configuration object to use.
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_blueprints(app)
    register_extensions(app)
    set_CORS(app)
    return app

def register_extensions(app):
    # Initialize the extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    return None

def register_blueprints(app):
    # Register Flask blueprints.
    app.register_blueprint(home.home_bp)
    app.register_blueprint(load_data.load_data_bp)

def set_CORS(app):
    CORS(app, origins=['http://localhost:4200', 'https://3rm85g3k-4200.uks1.devtunnels.ms'])
    return None