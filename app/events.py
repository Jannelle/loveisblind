from flask import request
from flask_socketio import emit
from app.models.league import *
# from app.

from .extensions import socketio, db

@socketio.on("connect")
def handle_connect():
    print("Client connected!")

# Socket for scoring an episode
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


# # Socket for drafting a team
# @socketio.on('activity_updated')
# def save_drafted_team():
#     data               = request.get_json()
#     episode            = data.get('episode')
#     teams_to_parse     = data.get('teams')
#     selected_league_id = session.get('selected_league_id')
    
#     for team_to_parse in teams_to_parse:
#         owner_name = team_to_parse['name']
#         owner      = Owner.query.filter_by(name = owner_name, league_id = session.get('selected_league_id')).one()
#         man_id      = Participant.query.filter_by(name = team_to_parse['man'  ]).first().id
#         woman_id    = Participant.query.filter_by(name = team_to_parse['woman']).first().id
#         bear_id     = Participant.query.filter_by(name = team_to_parse['bear' ]).first().id
        
#         Team.create_or_update_team(owner_id  = owner.id
#                                    , episode  = episode
#                                    , man_id   = man_id
#                                    , woman_id = woman_id
#                                    , bear_id  = bear_id
#                                    )


#     db.session.commit()

#     updated_data = fetch_updated_data()

#     return jsonify(updated_data)