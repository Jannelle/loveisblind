from flask import Blueprint
from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from config import DEFAULT_LEAGUE_ID
from app.models.league import *
from app.main import bp
from app.main.template_globals import *


@bp.route('/', methods = ('GET', 'POST'))
@set_default_league_id
def index():
    selected_league_id = session.get('selected_league_id')

    # Render the page with the selected league
    # You can retrieve the league data and pass it to the template
    all_leagues = League.query.all()
    selected_league = League.query.get(selected_league_id)
    # import pdb
    # pdb.set_trace()
    players = sorted(selected_league.players, key=calculate_player_points, reverse=True)
    return render_template('index.html',  players = players, leagues = all_leagues, selected_league_id=selected_league_id)

@bp.route('/select_league/', methods=['POST'])
@set_default_league_id
def select_league():
    league_id = request.form.get('league_id')
    session['selected_league_id'] = league_id
    return 'League ID updated successfully'

@bp.route('/how_to-score.html')
@set_default_league_id
def how_to_score():
    good_activities = Activity.query.filter_by(type = 'good').all()
    bad_activities = Activity.query.filter_by(type = 'bad').all()
    return render_template('how_to_score.html', good_activities = good_activities, bad_activities = bad_activities)

@bp.route('/castmembers.html')
@set_default_league_id
def castmembers():
    participants = Participant.query.all()
    return render_template('castmembers.html', participants = participants)

@bp.route('/get_teams', methods=['GET'])
@set_default_league_id
def get_teams():
    selected_league_id = session.get('selected_league_id')
    episode            = int(request.args.get('episode', 0))
    teams              = Team.query.filter_by(episode = episode).join(Player).filter(Player.league_id == selected_league_id).all()
    
    if len(teams) > 0:
        return jsonify({'teams': 
                        [
                            {
                                'name'         : team.owner.name,
                                'participants' : {
                                    'menList'          : team.man.name,
                                    'womenList'        : team.woman.name,
                                    'badNewsBearsList' : team.bear.name
                                    }
                            }
                            for team in teams
                        ]
                        })
    else:
        return jsonify({"message" : "No teams found for this episode!"})

@bp.route('/score_episode/<int:episode>', methods = ('GET', 'POST'))
@set_default_league_id
def score_episode(episode):
    selected_league_id = session.get('selected_league_id')
    
    if request.method == 'GET':
        activities = Activity.query.all()
        players    = League.query.filter_by(id = selected_league_id).one().players

        men   = Participant.query.filter_by(gender = 'male'  ) # Participant.query.join(Team, (Team.man_id   == Participant.id) & (Team.episode == episode))
        women = Participant.query.filter_by(gender = 'female') # Participant.query.join(Team, (Team.woman_id == Participant.id) & (Team.episode == episode))
        bears = Participant.query.join(Team, (Team.bear_id  == Participant.id)) # Participant.query.join(Team, (Team.bear_id  == Participant.id) & (Team.episode == episode))
        # men   = Participant.query.join(Team, (Team.man_id == Participant.id) & (Team.episode == episode)) \
        #                  .join(Player, Player.id == Team.owner_id) \
        #                  .filter(Player.league_id == selected_league_id)
                                       
        # women = Participant.query.join(Team, (Team.woman_id == Participant.id) & (Team.episode == episode)) \
        #                  .join(Player, Player.id == Team.owner_id) \
        #                  .filter(Player.league_id == selected_league_id)
        # bears = Participant.query.join(Team, (Team.bear_id == Participant.id) & (Team.episode == episode)) \
        #                  .join(Player, Player.id == Team.owner_id) \
        #                  .filter(Player.league_id == selected_league_id)

        roles_dict = {
            'Men'            : men,
            'Women'          : women,
            'Bad News Bears' : bears,
        }
        
        return render_template('score_episode.html'
                            , leagues = League.query.all()
                            , players = players
                            , episode    = episode
                            , roles_dict = roles_dict
                            , activities = activities
                            )
    elif request.method == 'POST':

        # Get the list of player IDs from the submitted form
        attended_players_ids = request.form.getlist('player-checkboxes')

        # Update the database based on the submitted form data
        for player in Player.query.all():
            if str(player.id) in attended_players_ids:
                # Add the viewing for players who attended
                player.viewings.append(Viewing(episode = episode))
            else:
                # Remove the viewing for players who did not attend
                for viewing in player.viewings:
                    if viewing.episode == episode:
                        player.viewings.remove(viewing)

        # Commit the changes to the database
        db.session.commit()

    # Redirect to the GET route for displaying the updated scores
    return redirect(url_for('.score_episode', episode = episode))

@bp.route('/select_teams/<int:episode>')
@set_default_league_id
def select_teams(episode):
    selected_league_id = session.get('selected_league_id')
    
    participants = Participant.query.order_by(Participant.name).all()
    men          = Participant.query.filter_by(gender = 'male'  )
    women        = Participant.query.filter_by(gender = 'female')
    players      = Player     .query.filter_by(league_id = selected_league_id).order_by(Player.name).all()
    
    return render_template('select_teams.html'
                           , leagues = League.query.all()
                           , participants = participants
                           , men          = men
                           , women        = women
                           , players      = players
                           , episode      = episode
                           )

@bp.route('/save_teams', methods=('GET', 'POST'))
@set_default_league_id
def save_teams():
    data               = request.get_json()
    episode            = data.get('episode')
    teams_to_parse     = data.get('teams')
    selected_league_id = session.get('selected_league_id')

    for team_to_parse in teams_to_parse:
        player_name = team_to_parse['name']
        player      = Player.query.filter_by(name = player_name, league_id = session.get('selected_league_id')).one()
        for team_member in team_to_parse['participants']:
            name        = team_member['name']
            origin_list = team_member['origin_list']
            participant_id = Participant.query.filter_by(name = name).first().id
            if   origin_list == 'menList':
                man_id   = participant_id
            elif origin_list == 'womenList':
                woman_id = participant_id
            elif origin_list == 'badNewsBearsList':
                bear_id   = participant_id
            else:
                raise ValueError(f"Bad origin_list {origin_list}")
        
        
        Team.create_or_update_team(player_id  = player.id
                                   , episode  = episode
                                   , man_id   = man_id
                                   , woman_id = woman_id
                                   , bear_id  = bear_id
                                   )

    db.session.commit()

    updated_data = fetch_updated_data()
    return jsonify(updated_data)

@bp.route('/fetch_updated_data')
@set_default_league_id
def fetch_updated_data():
    # Query the updated data from the database
    # You may need to adjust this based on your actual data retrieval logic
    selected_league = League.query.get(session.get('selected_league_id'))
    players = selected_league.players
    # Convert data to a dictionary or list that can be easily converted to JSON
    updated_data = {
        'players': [
            {
                'name'        : player.name,
                'id'          : player.id,
                'total_score' : calculate_player_points(player),
                'teams': [
                    {
                        'id'               : team.id,
                        'episode'          : team.episode,
                        'man'              : team.man.name,
                        'woman'            : team.woman.name,
                        'bear'             : team.bear.name,
                        'man_points'       : calculate_participant_points(team.man,   'good', team.episode),
                        'woman_points'     : calculate_participant_points(team.woman, 'good', team.episode),
                        'bear_points'      : calculate_participant_points(team.bear,  'bad' , team.episode),
                        'episode_points'   : calculate_team_points(team),
                        'attended_viewing' : team.attended_viewing,
                        
                    }
                    for team in player.teams.all()
                ]
            }
            for player in players
        ]
    }

    return updated_data


@bp.route('/add_player', methods=['POST'])
def add_player():
    if request.method == 'POST':
        selected_league = League.query.filter_by(name = request.form['league_name']).one().id
        db.session.add(Player(name = request.form['player_name']))
        db.session.commit()

        # Redirect to a success page or back to the form page
        return redirect(url_for('.add_or_remove_players'))
    
@bp.route('/add_or_remove_players', methods=['GET', 'POST'])
def add_or_remove_players():
    if request.method == 'POST':
        if 'add_player' in request.form:
            # Add a new player
            player_name = request.form['player_name']
            league_name = request.form['league_name']
            league_id = League.query.filter_by(name = league_name).one().id
            if player_name:
                new_player = Player(name = player_name, league_id = league_id)
                db.session.add(new_player)
                db.session.commit()
        elif 'remove_player' in request.form:
            # Remove a player
            player_id = request.form['player_id']
            player = Player.query.get(player_id)
            if player:
                db.session.delete(player)
                db.session.commit()

    # Fetch the list of players from the database
    players = Player.query.all()
    leagues = League.query.all()
    return render_template('add_or_remove_players.html', players=players, leagues=leagues)


@bp.route('/draft/<int:episode>')
def draft(episode):
    selected_league_id = session.get('selected_league_id')
    
    participants = Participant.query.order_by(Participant.name).all()
    men          = Participant.query.filter_by(gender = 'male'  )
    women        = Participant.query.filter_by(gender = 'female')
    players      = Player     .query.filter_by(league_id = selected_league_id).order_by(Player.name).all()
    
    # men = men.all().query.filter_by(name = 'Ariel')   
    return render_template('draft.html'
                           , leagues = League.query.all()
                           , participants = participants
                           , men          = men
                           , women        = women
                           , players      = players
                           , episode      = episode
                           )


@bp.route('/test')
def test():
    return render_template('test.html')

@bp.route('/get_players')
@set_default_league_id
def get_players():
    selected_league_id = session.get('selected_league_id')

    players = Player.query.filter_by(league_id = selected_league_id)
    player_data = [player.name for player in players]
    return jsonify(players=player_data)


@bp.route('/save_drafted_team', methods=('GET', 'POST'))
@set_default_league_id
def save_drafted_team():
    data               = request.get_json()
    episode            = data.get('episode')
    teams_to_parse     = data.get('teams')
    selected_league_id = session.get('selected_league_id')

    for team_to_parse in teams_to_parse:
        player_name = team_to_parse['name']
        player      = Player.query.filter_by(name = player_name, league_id = session.get('selected_league_id')).one()
        man_id      = Participant.query.filter_by(name = team_to_parse['man'  ]).first().id
        woman_id    = Participant.query.filter_by(name = team_to_parse['woman']).first().id
        bear_id     = Participant.query.filter_by(name = team_to_parse['bear' ]).first().id
        
        Team.create_or_update_team(player_id  = player.id
                                   , episode  = episode
                                   , man_id   = man_id
                                   , woman_id = woman_id
                                   , bear_id  = bear_id
                                   )

    db.session.commit()

    updated_data = fetch_updated_data()
    print(updated_data)
    return jsonify(updated_data)