from sys import activate_stack_trampoline
from database_functions import *
from flask import render_template, request, url_for, redirect, jsonify


@app.route('/', methods = ('GET', 'POST'))
def index():
    players = Player.query.all()
    return render_template('index.html', players = players)
    

@app.route('/how_to-score.html')
def how_to_score():
    good_activities = Activity.query.filter_by(type = 'good').all()
    bad_activities = Activity.query.filter_by(type = 'bad').all()
    return render_template('how_to_score.html', good_activities = good_activities, bad_activities = bad_activities)

@app.route('/castmembers.html')
def castmembers():
    participants = Participant.query.all()
    return render_template('castmembers.html', participants = participants)

@app.route('/get_teams', methods=['GET'])
def get_teams():
    episode = int(request.args.get('episode', 0))
    teams = Team.query.filter_by(episode = episode).all()
    if len(teams) > 0:
        return jsonify({'teams': 
                        [
                            {
                                'name'         : team.owner.name,
                                'participants' : [team.man.name, team.woman.name, team.bear.name]
                            }
                            for team in teams
                        ]
                        })
    else:
        return jsonify({'error': 'Episode not found'}), 404

@app.template_global()
def calculate_participant_points(participant, type, episode = None):
        '''Calculates how many points a participant has earned.

        Args:
            participant (Participant) : The participant whose points we are evaluating.
            type (str) ["good", "bad"]: Will be used to filter which activities will give that participant points.
            episode                   : Which episode to calculate points for. If None, will get total.
        '''
        total_pts = 0
        if participant is None:
            return 0
        if episode is None:
            activity_assocs_to_search = participant.activity_association.all()
        else:
            activity_assocs_to_search = participant.activity_association.filter_by(episode = episode)
        for activity_association in activity_assocs_to_search:
            if activity_association.activity.type == type:
                total_pts += activity_association.activity.pts
        return total_pts



# This decorator allows us to use this function in a template
@app.template_global()
def calculate_team_points(team):
    '''Calculates how many points a team has. It does so by looping through each Participant in the team.'''
    
    total_points = 0
    # Doing a separate loop for the man and woman compared to bear since they require different activity types
    for participant in [team.man, team.woman]:
        if participant: # skip if the participant is None (this shouldn't happen in practice, but happens during testing)
            total_points += calculate_participant_points(participant, "good", team.episode)
        
    if team.bear: # skip if team has no Bad News Bear
        total_points += calculate_participant_points(team.bear, "bad", team.episode)

    return total_points

@app.template_global()
def calculate_player_points(player):
    '''Calculates how many points a player has by looping through all of their teams.'''
    total_points = 0
    for team in player.teams.all():
        total_points += calculate_team_points(team)
    return total_points

@app.route('/score_episode/<int:episode>')
def score_episode(episode):
    activities              = Activity.query.all()
    # men   = Participant.query.filter_by(gender = 'male'  ) # Participant.query.join(Team, (Team.man_id   == Participant.id) & (Team.episode == episode))
    # women = Participant.query.filter_by(gender = 'female') # Participant.query.join(Team, (Team.woman_id == Participant.id) & (Team.episode == episode))
    # bears = Participant.query.join(Team, (Team.bear_id  == Participant.id)) # Participant.query.join(Team, (Team.bear_id  == Participant.id) & (Team.episode == episode))
    men   = Participant.query.join(Team, (Team.man_id   == Participant.id) & (Team.episode == episode))
    women = Participant.query.join(Team, (Team.woman_id == Participant.id) & (Team.episode == episode))
    bears = Participant.query.join(Team, (Team.bear_id  == Participant.id) & (Team.episode == episode))

    roles_dict = {
        'Men'            : men,
        'Women'          : women,
        'Bad News Bears' : bears,
    }
    
    return render_template('score_episode.html'
                           , episode    = episode
                           , roles_dict = roles_dict
                           , activities = activities
                           )

@app.route('/select_teams/<int:episode>')
def select_teams(episode):
    participants = Participant.query.all()
    men          = Participant.query.filter_by(gender = 'male'  )
    women        = Participant.query.filter_by(gender = 'female')
    players      = Player     .query.all()
    
    return render_template('select_teams.html'
                           , participants = participants
                           , men          = men
                           , women        = women
                           , players      = players
                           , episode      = episode
                           )


@app.route('/save_teams', methods = ('GET', 'POST'))
def save_teams():

    data = request.get_json()
    episode = data.get('episode')
    teams_to_parse = data.get('teams')

    Team.query.filter_by(episode = episode).delete()

    for team_to_parse in teams_to_parse:
        player = Player.query.filter_by(name = team_to_parse['name']).first()
        team   = Team(episode = episode)
        player.teams.append(team)

        for participant_str in team_to_parse['participants']:
            participant_name = participant_str.split(' - ')[0]
            participant_role = participant_str.split(' - ')[1]
            participant = Participant.query.filter_by(name = participant_name).first()
            if   participant_role == 'men':
                team.man   = participant
            elif participant_role == 'women':
                team.woman = participant
            elif participant_role == 'badNewsBears':
                team.bear   = participant
            else:
                print('!!!!!')
                print(participant_role)

        db.session.commit()

    updated_data = fetch_updated_data()
    return jsonify(updated_data)

@app.route('/fetch_updated_data')
def fetch_updated_data():
    # Query the updated data from the database
    # You may need to adjust this based on your actual data retrieval logic
    players = Player.query.all()
    # ... (any other data you need)

    # Convert data to a dictionary or list that can be easily converted to JSON
    updated_data = {
        'players': [
            {
                'name'        : player.name,
                'id'          : player.id,
                'total_score' : calculate_player_points(player),
                'teams': [
                    {
                        'id'           : team.id,
                        'episode'      : team.episode,
                        'man'          : team.man.name,
                        'woman'        : team.woman.name,
                        'bear'         : team.bear.name,
                        'man_points'   : calculate_participant_points(team.man,   'good', team.episode),
                        'woman_points' : calculate_participant_points(team.woman, 'good', team.episode),
                        'bear_points'  : calculate_participant_points(team.bear,  'bad' , team.episode),
                        
                    }
                    for team in player.teams.all()
                ]
            }
            for player in players
        ]
    }

    return updated_data

@app.route('/increment_activity', methods=['POST'])
def increment_activity():
    data = request.get_json()

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
    return jsonify({"message": "Updated activities"})


@app.template_global()
def get_activity_count(participant_id, activity_id):
    return len(Participant_Activity_Association.query.filter_by(participant_id = participant_id, activity_id = activity_id).all())
