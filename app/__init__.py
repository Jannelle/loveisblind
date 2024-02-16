from flask import Flask
from .extensions import db, cache
from .main.events import socketio
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Bind the SocketIO server object to the Flask application object.
    socketio.init_app(app)

    # Initialize the SQLAlchemy engine object.
    db.init_app(app)

    cache.init_app(app)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

