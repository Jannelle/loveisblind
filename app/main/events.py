import socket
from flask import request, session
from flask_socketio import emit
from app.models.league import *
from app.extensions import socketio, db, cache

@socketio.on("connect")
def handle_connect():
    print("Client connected!")

# Socket for scoring an episode
@socketio.on('activity_updated')
def handle_activity_update(data):
    castmember_id = data.get('castmember_id')
    activity_id   = data.get('activity_id')
    episode       = data.get('episode')
    increment     = data.get('increment')

    castmember = Castmember.query.get(castmember_id)
    activity    = Activity.query.get(activity_id)
    
    if increment:
        castmember.activity_association.append(
            Castmember_Activity_Association(episode = episode, activity = activity)
        )
    else:
        assoc_to_remove = Castmember_Activity_Association.query.filter_by(castmember = castmember
                                                                         , episode     = episode
                                                                         , activity    = activity
                                                                         ).first()
        if assoc_to_remove is not None:
            castmember.activity_association.remove(assoc_to_remove)

    db.session.commit()
    
    # Emit a SocketIO event to notify all clients about the activity update
    emit('update_activity_count', data, broadcast = True)
