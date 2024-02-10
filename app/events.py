from flask import request
from flask_socketio import emit
from app.models.league import *

from .extensions import socketio, db

@socketio.on("connect")
def handle_connect():
    print("Client connected!")


@socketio.on('activity_updated')
def handle_activity_update(data):
    participant_id = data.get('participant_id')
    activity_id    = data.get('activity_id')
    episode        = data.get('episode')
    increment      = data.get('increment')

    participant = Participant.query.get(participant_id)
    activity    = Activity.query.get(activity_id)
    
    if increment:
        participant.activity_association.append(
            Participant_Activity_Association(episode = episode, activity = activity)
        )
    else:
        assoc_to_remove = Participant_Activity_Association.query.filter_by(participant = participant
                                                                         , episode   = episode
                                                                         , activity  = activity
                                                                         ).first()
        if assoc_to_remove is not None:
            participant.activity_association.remove(assoc_to_remove)

    db.session.commit()
    
    # Emit a SocketIO event to notify all clients about the activity update
    emit('update_activity_count', data, broadcast=True)