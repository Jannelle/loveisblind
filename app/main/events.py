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

# If page got refreshed but there's cached data,
# update the data with the cached data
@socketio.on('get_cached_data')
def get_cached_data(episode):
    # If user selected a different episode, reset cache
    cached_episode = cache.get('episode')
    if cached_episode and (cached_episode != episode):
        emit('episode_conflict', { 'cached_episode' : cached_episode, 'episode' : episode})
        cache.clear()
    else:
        cache.set('episode', episode)

    if cache.get('current_owner'):
        emit('update_turn_data',
            {
                'owner'         : cache.get('current_owner'),
                'current_round' : cache.get('current_round'),
                'draft_order'   : cache.get('draft_order'),
            }
        )
    if cache.get('teams'):
        teams = cache.get('teams')
        for owner, members in teams.items():
            for role, castmember in members.items():
                if castmember:
                    emit('drafted_castmember',
                        {
                            'owner'              : owner,
                            'drafted_castmember' : castmember,
                            'role'               : role, 
                        }
                    )
                

def reset_team_data():
    owners = [owner.name for owner in Owner.query.filter_by(league_id = session.get('selected_league_id')).all()]
    cache.set('owners', owners)
    teams = { owner : {
                        'man'   : None,
                        'woman' : None,
                        'bear'  : None,
                      }
            for owner in owners
            }
    cache.set('teams', teams)


def reset_turn_data():
    cache.set('current_round', 0 )
    cache.set('current_index', 0 )
    cache.set('current_owner', '')
    cache.set('draft_selections', [])


def roll_draft_order():
    import random
    draft_order = cache.get('owners')
    random.shuffle(draft_order)
    cache.set('draft_order', draft_order)    
    cache.set('current_owner', cache.get('draft_order')[cache.get('current_index')])
    

# Socket for starting the draft
@socketio.on('start_draft')
def start_draft():
    if cache.get('current_round'):
        current_round = cache.get('current_round')
    else:
        current_round = 0

    if current_round == 0:
        reset_draft()
        roll_draft_order()

        current_round += 1
        cache.set('current_round', current_round)
        emit('update_turn_data', 
            {
                'owner'         : cache.get('current_owner'),
                'draft_order'   : cache.get('draft_order'),
                'current_round' : current_round,
            }
            , broadcast = True)
    else:
        emit('reset_draft', None, broadcast = True)
        
@socketio.on('reset_confirmed')
def reset_draft():
    reset_team_data()
    reset_turn_data()
    

@socketio.on('validate_then_draft_castmember')
def validate_castmember(data):
    castmember = data.get('castmember')
    role       = data.get('role')
    image_id   = data.get('imageID')

    team = cache.get('teams')[cache.get('current_owner')]

    # # As of 2/16, validation has been turned off as 
    # # we're still deciding on team requirements
    # # This makes sure people don't
    #  draft multiple members of the same role
    # if team[role] is not None:
    #     other_castmember_in_role = team[role]
    #     emit('invalid_draft', 
    #          {
    #              'castmember'       : castmember,
    #              'role'             : role,
    #              'other_castmember' : other_castmember_in_role,
    #          }
    #     , broadcast = True)
    # else:
    draft_castmember(castmember, role, image_id)
    go_to_next_turn()


def draft_castmember(castmember, role, image_id):
    teams = cache.get('teams'        )
    owner = cache.get('current_owner')
    role  = role
    
    # Updating the teams dictionary to reflect the newly drafted member
    teams[owner][role] = castmember
    cache.set('teams', teams)

    # Updating the list of draft selections. This keeps track for easy undoing
    draft_selections = cache.get('draft_selections')
    draft_selections.append({owner : [castmember, role, image_id]})
    
    cache.set('draft_selections', draft_selections)
    emit('drafted_castmember',
         {
            'image_id'           : image_id,
            'drafted_castmember' : castmember,
            'owner'              : owner,
            'role'               : role, 
         }
    , broadcast = True)

def go_to_next_turn():
    # Increment current index to go to the next team owner.
    # If at the end of the list, reverse the list
    # and start from the beginning of the reversed list (snake draft)
    # and increment the round
    current_index = cache.get('current_index')
    current_round = cache.get('current_round')
    draft_order   = cache.get('draft_order')

    current_index += 1
    if current_index == len(draft_order):
        draft_order.reverse()
        current_index = 0
        current_round += 1
    
    # if current_round > 3:
    #     emit('end_draft', None, broadcast = True)

    cache.set( 'current_index' , current_index              )
    cache.set( 'current_round' , current_round              )
    cache.set( 'draft_order'   , draft_order                )
    cache.set( 'current_owner' , draft_order[current_index] )

    emit('update_turn_data',
        {
            'owner'         : cache.get('current_owner'),
            'current_round' : current_round,
            'draft_order'   : draft_order,
        }
    , broadcast = True)

@socketio.on('undo_last_draft_selection')
def undo_last_draft_selection():
    current_index = cache.get('current_index')
    current_round = cache.get('current_round')
    draft_order   = cache.get('draft_order')
    teams         = cache.get('teams')
    
    draft_selections = cache.get('draft_selections')
    last_draft_selection = draft_selections.pop()
    
    owner_to_undo                 = list(last_draft_selection.keys())[0]
    castmember_to_remove          = last_draft_selection[owner_to_undo][0]
    castmember_to_remove_role     = last_draft_selection[owner_to_undo][1]
    castmember_to_unhide_id       = last_draft_selection[owner_to_undo][2]
    
    # Remove the most recently drafted castmember from the Teams record
    teams[owner_to_undo][castmember_to_remove_role] = None
    current_index -= 1
    #  If a new round was just started before hitting undo, we need to undo the steps of
    # starting a new round
    if (current_index < 0):
        current_round -= 1
        draft_order.reverse()
        current_index = len(draft_order) - 1

    cache.set('draft_selections' , draft_selections )
    cache.set('current_index'    , current_index    )
    cache.set('current_round'    , current_round    )
    cache.set('draft_order'      , draft_order      )
    cache.set('teams'            , teams            )
    cache.set('current_owner'    , draft_order[current_index])

    # Update the front end
    socketio.emit('draft_data_reversed',
                  {
                      'owner'         : owner_to_undo,
                      'castmember'    : castmember_to_remove,
                      'current_owner' : draft_order[current_index],
                      'current_round' : current_round,
                      'draft_order'   : draft_order,
                      'option_to_unhide_id' : castmember_to_unhide_id,
                      'option_to_remove_id' : castmember_to_unhide_id + 'list_option',
                  })        
    if len(draft_selections) == 0:
        socketio.emit('disable_undo')
    
    