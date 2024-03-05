from flask import Blueprint, Flask, render_template, request, url_for, redirect, jsonify, session, send_file
from config import DEFAULT_LEAGUE_ID
from app.models.league import *
from app.main import bp
from app.main.template_globals import *


@bp.route('/', methods = ('GET', 'POST'))
@set_default_league_id
def index():
    selected_league_id = session.get('selected_league_id')

    selected_league = League.query.get(selected_league_id)
    owners = sorted(selected_league.owners, key=calculate_owner_points, reverse=True)
    return render_template('index.html', owners = owners)

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
    episode            = request.args.get('episode', 0)
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

@bp.route('/score_episode/<episode>', methods = ('GET', 'POST'))
@set_default_league_id
def score_episode(episode):
    from sqlalchemy import func
    selected_league_id = session.get('selected_league_id')
    
    if request.method == 'GET':

        # Assuming you have a list of activity names
        activity_order = [
            "Miscellaneous 'Awww' moments",
            "Maturely handled a situation with another cast member",
            "Happy cried",
            "Did a sweet/romantic gesture for their partner",
            "Said “I love you” to date/partner or vice versa",
            "Had sex with their partner",
            "Gave/received a gift",
            "Created/performed some type of art",
            "Another castmember finds them attractive",
            "Got their partner’s friends/family’s blessing",
            "Post-engagement, had a romantic date",
            "Another castmember said they wish they were with them/chose them",
            "Showed self-improvement or had a self-realization",
            "Apologized for something they did wrong",
            "Defended their partner to others",
            "Rejected flirtations/advancements from non-partner",
            "Consoled or supported another castmember ",
            "Said “I do” on their wedding day",  
            "Partner said “I do” on their wedding day",
            "Got called, someone's #1/only choice/interest",
            "Said they're 'falling for' partner (or vice versa)",
            "Proposed or got proposed to",
            "Got engaged (i.e., the proposal was accepted)",

            "Miscellaneous scandalous thing",
            "Sad/angry cried",
            "Argued with partner",
            "Yelled at/insulted their partner",
            "Talked shit about someone else or got talked shit about",
            "Walked out during a date without saying bye",
            "After being engaged, flirted with someone who isn’t their partner",
            "Broke up with partner (post-engagement)",
            "Cheated on their partner",
            "Family/friends didn't like their partner",
            "Tried to change/control how partner looks",
            "Did/said something cringe",
            "Backpedaled on something they said in the pods",
            "Revealed a fundamental relatinship incompatibility",
            "Expressed regret about another castmember (1-3 pts)",
            "Called their partner another castmember/romantic interest/'s name",
            "Got caught lying",
            "Pressured partner to do something for own self-interest",
            "Got dumped on their wedding day",
            "Said no on their wedding day",            
            "Doesn't find partner attractive at reveal (or vice versa)",            
            "Can't choose between two (or more) people",
            "In the pods, dumped or got dumped by someone else",
            "Got their proposal rejected or rejected a proposal",            
        ]

        # Query activities based on the input list of names and order them accordingl
        activities = sorted(Activity.query.all(), key=lambda x: activity_order.index(x.name))
        owners     = League.query.filter_by(id = selected_league_id).one().owners

        men   = Castmember.query.filter_by(gender = 'male'  ) # Castmember.query.join(Team, (Team.man_id   == Castmember.id) & (Team.episode == episode
        women = Castmember.query.filter_by(gender = 'female') # Castmember.query.join(Team, (Team.woman_id == Castmember.id) & (Team.episode == episode
        bears = Castmember.query # Castmember.query.join(Team, (Team.bear_id  == Castmember.id) & (Team.episode == episode

        roles_dict = {
            'Men'            : men,
            'Women'          : women,
            'Bad News Bears' : bears,
        }
        
        return render_template('score_episode.html'
                            , owners     = owners
                            , episode    = episode
                            , roles_dict = roles_dict
                            , activities = activities
                            )
                               
    elif request.method == 'POST':

        # Get the list of owner IDs from the submitted for
        attended_owners_ids = request.form.getlist('owner-checkboxes')

        # Update the database based on the submitted form dat
        for owner in Owner.query.all():
            if str(owner.id) in attended_owners_ids:
                # Add the viewing for owners who attende
                owner.viewings.append(Viewing(episode = episode))
            else:
                # Remove the viewing for owners who did not atten
                for viewing in owner.viewings:
                    if viewing.episode == episode:
                        owner.viewings.remove(viewing)

        # Commit the changes to the database
        db.session.commit()

    # Redirect to the GET route for displaying the updated scores
    return redirect(url_for('.score_episode', episode = episode))

@bp.route('/select_teams/<episode>')
@set_default_league_id
def select_teams(episode):
    selected_league_id = session.get('selected_league_id')
    
    castmembers = Castmember.query.order_by(Castmember.name).all()
    men         = Castmember.query.filter_by(gender = 'male'  ).all()
    women       = Castmember.query.filter_by(gender = 'female').all()
    print(len(women))
    print(len(women))
    print(len(women))

    owners      = Owner     .query.filter_by(league_id = selected_league_id).order_by(Owner.name).all()
    
    return render_template('select_teams.html'
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

    owners = Owner.query.all()
    return render_template('add_or_remove_owners.html', owners=owners)


@bp.route('/draft/<int:episode>')
def draft(episode):
    selected_league_id = session.get('selected_league_id')
    
    castmembers = Castmember.query.order_by(Castmember.name).all()
    men         = Castmember.query.filter_by(gender    = 'male'  ).all()
    women       = Castmember.query.filter_by(gender    = 'female').all()
    owners      = Owner     .query.filter_by(league_id = selected_league_id).order_by(Owner.name).all()

    castmember_groups = [
        {'castmembers' : men,
         'role'        : 'man',
         'header_text' : 'Men',
        },
        {'castmembers' : women,
         'role'        : 'woman',
         'header_text' : 'Women',
        },
        {'castmembers' : castmembers,
         'role'        : 'bear',
         'header_text' : 'Bad News Bears',
        },
    ]
    
    return render_template('draft.html'
                           , castmembers        = castmembers
                           , castmember_groups  = castmember_groups
                           , owners             = owners
                           , episode            = episode
                           , selected_league_id = selected_league_id
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


@bp.route('/backup/')
def backup_database():
    
    backup_file_path = '../database.db'
    return send_file(backup_file_path, as_attachment=True)
