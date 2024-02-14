from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_socketio import SocketIO
socketio = SocketIO()

from flask_caching import Cache
cache = Cache()