from flask import Blueprint, Flask, render_template, request, url_for, redirect, jsonify, session, send_file
from config import DEFAULT_LEAGUE_ID
from app.models.league import *
from app.main import bp
from app.main.template_globals import *
import subprocess
import os

@bp.route('/', methods = ('GET', 'POST'))
@set_default_league_id
def index():
    selected_league_id = session.get('selected_league_id')

    all_leagues = League.query.all()
    selected_league = League.query.get(selected_league_id)
    owners = sorted(selected_league.owners, key=calculate_owner_points, reverse=True)
    return render_template('index.html', owners = owners, leagues = all_leagues, selected_league_id=selected_league_id)

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

@bp.route('/all_castmembers_scores.html')
@set_default_league_id
def all_castmembers_scores():
    castmembers = Castmember.query.all()
    return render_template('all_castmembers_scores.html', castmembers = castmembers)

@bp.route('/get_teams', methods=['GET'])
@set_default_league_id
def get_teams():
    selected_league_id = session.get('selected_league_id')
    episode            = int(request.args.get('episode', 0))
    teams              = Team.query.filter_by(episode = episode).join(Owner).filter(Owner.league_id == selected_league_id).all()
    
    if len(teams) > 0:
        return jsonify({'teams': 
                    [
                        {
                            'name'         : team.owner.name,
                            'castmembers' : {
                                'woman' : [member.name for member in team.good_members if member.gender == 'female'],
                                'man'   : [member.name for member in team.good_members if member.gender == 'male'  ],
                                'bear'  : [member.name for member in team.bad_members],
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
        owners    = League.query.filter_by(id = selected_league_id).one().owners

        men   = Castmember.query.filter_by(gender = 'male'  ) # Castmember.query.join(Team, (Team.man_id   == Castmember.id) & (Team.episode == episode))
        women = Castmember.query.filter_by(gender = 'female') # Castmember.query.join(Team, (Team.woman_id == Castmember.id) & (Team.episode == episode))
        bears = Castmember.query # Castmember.query.join(Team, (Team.bear_id  == Castmember.id) & (Team.episode == episode))

        roles_dict = {
            'Men'            : men,
            'Women'          : women,
            'Bad News Bears' : bears,
        }
        
        return render_template('score_episode.html'
                            , leagues = League.query.all()
                            , owners = owners
                            , episode    = episode
                            , roles_dict = roles_dict
                            , activities = activities
                            )
    elif request.method == 'POST':

        # Get the list of owner IDs from the submitted form
        attended_owners_ids = request.form.getlist('owner-checkboxes')

        # Update the database based on the submitted form data
        for owner in Owner.query.all():
            if str(owner.id) in attended_owners_ids:
                # Add the viewing for owners who attended
                owner.viewings.append(Viewing(episode = episode))
            else:
                # Remove the viewing for owners who did not attend
                for viewing in owner.viewings:
                    if viewing.episode == episode:
                        owner.viewings.remove(viewing)

        # Commit the changes to the database
        db.session.commit()

    # Redirect to the GET route for displaying the updated scores
    return redirect(url_for('.score_episode', episode = episode))

@bp.route('/select_teams/<int:episode>')
@set_default_league_id
def select_teams(episode):
    selected_league_id = session.get('selected_league_id')
    
    castmembers = Castmember.query.order_by(Castmember.name).all()
    men         = Castmember.query.filter_by(gender = 'male'  )
    women       = Castmember.query.filter_by(gender = 'female')
    owners      = Owner     .query.filter_by(league_id = selected_league_id).order_by(Owner.name).all()
    
    return render_template('select_teams.html'
                           , leagues = League.query.all()
                           , castmembers = castmembers
                           , men         = men
                           , women       = women
                           , owners      = owners
                           , episode     = episode
                           )

@bp.route('/save_teams', methods=('GET', 'POST'))
@set_default_league_id
def save_teams():

    data               = request.get_json()
    episode            = data.get('episode')
    teams_to_parse     = data.get('teams')
    selected_league_id = session.get('selected_league_id')
    
    for owner_name, team_to_parse in teams_to_parse.items():
        owner = Owner.query.filter_by(name=owner_name, league_id=selected_league_id).one()
        good_member_ids = get_castmember_ids_by_names(team_to_parse['good_members'])
        bad_member_ids  = get_castmember_ids_by_names(team_to_parse['bad_members'])
        
        Team.create_or_update_team(
            owner_id = owner.id,
            episode  = episode,
            good_member_ids = good_member_ids,
            bad_member_ids  = bad_member_ids
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
    owners = selected_league.owners
    # Convert data to a dictionary or list that can be easily converted to JSON
    updated_data = {
        'owners': [
            {
                'name'         : owner.name,
                'id'           : owner.id,
                'total_score'  : calculate_owner_points(owner),
                'teams': [
                    {
                        'id'              : team.id,
                        'episode'         : team.episode,
                        'good_members'    : [castmember.name for castmember in team.good_members],
                        'bad_members'     : [castmember.name for castmember in team.bad_members ],
                        'good_points'     : sum(calculate_castmember_points(castmember, 'good', team.episode) for castmember in team.good_members),
                        'bad_points'      : sum(calculate_castmember_points(castmember, 'bad' , team.episode) for castmember in team.bad_members ),
                        'episode_points'  : calculate_team_points(team),
                        'attended_viewing': team.attended_viewing
                    }
                    for team in owner.teams.all()
                ]
            }
            for owner in owners
        ]
    }

    return updated_data


@bp.route('/add_owner', methods=['POST'])
def add_owner():
    if request.method == 'POST':
        selected_league = League.query.filter_by(name = request.form['league_name']).one().id
        db.session.add(Owner(name = request.form['owner_name']))
        db.session.commit()

        # Redirect to a success page or back to the form page
        return redirect(url_for('.add_or_remove_owners'))
    
@bp.route('/add_or_remove_owners', methods=['GET', 'POST'])
def add_or_remove_owners():
    if request.method == 'POST':
        if 'add_owner' in request.form:
            # Add a new owner
            owner_name = request.form['owner_name']
            league_name = request.form['league_name']
            league_id = League.query.filter_by(name = league_name).one().id
            if owner_name:
                new_owner = Owner(name = owner_name, league_id = league_id)
                db.session.add(new_owner)
                db.session.commit()
        elif 'remove_owner' in request.form:
            # Remove a owner
            owner_id = request.form['owner_id']
            owner = Owner.query.get(owner_id)
            if owner:
                db.session.delete(owner)
                db.session.commit()

    # Fetch the list of owners from the database
    owners = Owner.query.all()
    leagues = League.query.all()
    return render_template('add_or_remove_owners.html', owners=owners, leagues=leagues)


@bp.route('/draft/<int:episode>')
def draft(episode):
    selected_league_id = session.get('selected_league_id')
    
    castmembers = Castmember.query.order_by(Castmember.name).all()
    men         = Castmember.query.filter_by(gender    = 'male'  )
    women       = Castmember.query.filter_by(gender    = 'female')
    owners      = Owner     .query.filter_by(league_id = selected_league_id).order_by(Owner.name).all()
    
    # men = men.all().query.filter_by(name = 'Ariel')   
    return render_template('draft.html'
                           , leagues      = League.query.all()
                           , castmembers = castmembers
                           , men          = men
                           , women        = women
                           , owners      = owners
                           , episode      = episode
                           )

def get_castmember_ids_by_names(names):
    """
    Get the IDs of cast members given their names.

    Args:
        names (list): A list of cast member names.

    Returns:
        list: A list of cast member IDs.
    """
    import pdb
    # pdb.set_trace()
    castmember_ids = [Castmember.query.filter_by(name=name).first().id for name in names]
    return castmember_ids

@bp.route('/get_owners')
@set_default_league_id
def get_owners():
    selected_league_id = session.get('selected_league_id')

    owners = Owner.query.filter_by(league_id = selected_league_id)
    owner_data = [owner.name for owner in owners]
    return jsonify(owners=owner_data)


@bp.route('/save_drafted_team', methods=('GET', 'POST'))
@set_default_league_id
def save_drafted_team():
    data = request.get_json()
    episode = data.get('episode')
    teams_to_parse = data.get('teams')
    selected_league_id = session.get('selected_league_id')
    
    for team_to_parse in teams_to_parse:
        owner_name = team_to_parse['name']
        owner = Owner.query.filter_by(name=owner_name, league_id=selected_league_id).one()
        
        good_member_ids = get_castmember_ids_by_names(team_to_parse['good_members'])
        bad_member_ids  = get_castmember_ids_by_names(team_to_parse['bad_members'])
        
        Team.create_or_update_team(owner_id=owner.id,
                                   episode=episode,
                                   good_member_ids=good_member_ids,
                                   bad_member_ids=bad_member_ids)
    
    db.session.commit()
    updated_data = fetch_updated_data()
    return jsonify(updated_data)


@bp.route('/backup/')
def backup_database():
    backup_file_path = '../database.db'
    return send_file(backup_file_path, as_attachment=True)
