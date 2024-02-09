from codecs import backslashreplace_errors
import json
import os
from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

DEFAULT_LEAGUE_ID = 1
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db = SQLAlchemy(app)

class League(db.Model):
    __tablename__ = "League"
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), unique=True, nullable=False)
    players = db.relationship('Player', back_populates='league', uselist=True)

    # Define league_slug property
    @property
    def league_slug(self):
        import regex as re
        # Convert name to lowercase and replace spaces with hyphens
        slug = re.sub(r'\s+', '-', self.name.lower())
        # Remove any non-alphanumeric characters except hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        return slug
    
viewing_player_association = db.Table('viewing_player_association',
    db.Column('viewing_id', db.Integer, db.ForeignKey('Viewing.id')),
    db.Column('player_id', db.Integer, db.ForeignKey('Player.id'))
)

class Player(db.Model):
    '''
    The Players of the fantasy game. Each player has a name and a team.

    Columns:
    id (int)   : Primary key
    name (str) : The name of the player

    Relationships:
    teams (Query) : Relationship to Team table
    '''
    __tablename__ = "Player"
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100), unique=False, nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('League.id'))
    teams     = db.relationship("Team", backref="owner", lazy="dynamic", uselist=True)
    viewings  = db.relationship('Viewing', secondary=viewing_player_association, back_populates='players')
    league    = db.relationship("League", lazy=True, back_populates="players")

    def __repr__(self):
        return f"id: {self.id}\nname: {self.name}\nleague_name: {self.league.name}\n\n"

class Viewing(db.Model):
    __tablename__ = 'Viewing'
    id        = db.Column(db.Integer, primary_key=True)
    episode   = db.Column(db.Integer)
    players   = db.relationship('Player', secondary=viewing_player_association, back_populates='viewings')


class Participant_Activity_Association(db.Model):
    '''
    Association table that keeps track of each activity that each participant did.

    Columns:
    id (int)                    : Primary key
    participant_id (int)        : Foreign key referencing Participant.id
    activity_id (int)           : Foreign key referencing Activity.id
    episode (str)               : Episode number for which the activity is associated

    Relationships:
    participant (Participant)   : Reference to the Participant object
    activity (Activity)         : Reference to the Activity object
    '''
    __tablename__  = 'Participant_Activity_Association'
    id             = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('Participant.id'))
    activity_id    = db.Column(db.Integer, db.ForeignKey('Activity.id'))
    episode        = db.Column(db.String(50))

    participant = db.relationship("Participant", back_populates="activity_association")
    activity    = db.relationship("Activity", back_populates="participant_association")


class Participant(db.Model):
    '''
    Participants are the Love is Blind cast members. They earn points by completing certain activities.

    Columns:
    id (int)                    : Primary key
    name (str)                  : The participant's full name
    gender (str)                : Gender of the participant
    activity_association (AppenderQuery)  : Collection of activities the Participant has done
    man_teams (AppenderQuery)    : Collection of teams that have claimed this Participant as a "bad news bear"

    Relationships:
    activity_association (Query): Relationship to Participant_Activity_Association table
    man_teams (Query)           : Relationship to Team table for Man teams
    woman_teams (Query)         : Relationship to Team table for Woman teams
    bear_teams (Query)          : Relationship to Team table for Bad News Bear teams
    '''
    __tablename__ = "Participant"
    id                   = db.Column(db.Integer, primary_key=True)
    name                 = db.Column(db.String(100), unique=True, nullable=False)
    gender               = db.Column(db.String(100), unique=False, nullable=False)
    activity_association = db.relationship('Participant_Activity_Association', lazy='dynamic', back_populates='participant')
    man_teams            = db.relationship("Team", lazy='dynamic', uselist=True, primaryjoin="Team.man_id == Participant.id")
    woman_teams          = db.relationship("Team", lazy='dynamic', uselist=True, primaryjoin="Team.woman_id == Participant.id")
    bear_teams           = db.relationship("Team", lazy='dynamic', uselist=True, primaryjoin="Team.bear_id == Participant.id")

    def get_activities(self, episode):
        '''
        Get a list of activities associated with the participant for a specific episode.

        Args:
        - episode (int): Episode number for which to fetch activities

        Returns:
        - List of Activity objects
        '''
        activity_assocs = self.activity_association.filter_by(episode=episode)
        activities = []
        for activity_assoc in activity_assocs:
            activities.append(activity_assoc.activity)
        return activities


class Team(db.Model):
    '''
    The Team of participants that own points for the players. Each team can have one Man, one Woman, and one Bad News Bear.

    Columns:
    id (int)            : Primary key
    owner_id (int)      : The id of the owner of the team in the Player table
    episode (int)       : The episode number that the team was created for
    man_id (int)        : Foreign key referencing Participant.id for the Man on the team
    woman_id (int)      : Foreign key referencing Participant.id for the Woman on the team
    bear_id (int)       : Foreign key referencing Participant.id for the Bad News Bear on the team

    Relationships:
    owner (Player)      : Reference to the Player object
    man (Participant)   : Reference to the Participant object for the Man on the team
    woman (Participant) : Reference to the Participant object for the Woman on the team
    bear (Participant)  : Reference to the Participant object for the Bad News Bear on the team
    '''
    __tablename__ = "Team"
    id       = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("Player.id"))
    episode  = db.Column(db.Integer)

    man_id   = db.Column(db.Integer, db.ForeignKey('Participant.id'))
    woman_id = db.Column(db.Integer, db.ForeignKey('Participant.id'))
    bear_id  = db.Column(db.Integer, db.ForeignKey('Participant.id'))

    man   = db.relationship("Participant",
                          primaryjoin="Team.man_id == Participant.id",
                          back_populates='man_teams',
                          lazy=True,
                          uselist=False
                          )
    woman = db.relationship("Participant",
                            primaryjoin="Team.woman_id == Participant.id",
                            back_populates='woman_teams',
                            lazy=True,
                            uselist=False
                            )
    bear  = db.relationship("Participant",
                           primaryjoin="Team.bear_id == Participant.id",
                           back_populates='bear_teams',
                           lazy=True,
                           uselist=False
                           )
    

    @staticmethod
    def get_team_for_player_and_episode(player_id, episode):
        return Team.query.filter_by(owner_id=player_id, episode=episode).first()

    @staticmethod
    def create_or_update_team(player_id, episode, man_id, woman_id, bear_id):
        existing_team = Team.get_team_for_player_and_episode(player_id, episode)
        if existing_team:
            # Update the existing team
            existing_team.man_id   = man_id
            existing_team.woman_id = woman_id
            existing_team.bear_id  = bear_id
            
        else:
            # Create a new team
            new_team = Team(
                owner_id=player_id,
                episode=episode,
                man_id=man_id,
                woman_id=woman_id,
                bear_id=bear_id
            )
            db.session.add(new_team)

        db.session.commit()

    @property
    def attended_viewing(self):
        return any(viewing.episode == self.episode for viewing in self.owner.viewings)
    
    def __repr__(self):
        team_dict = {'owner' : self.owner.name}
        if self.man:
            team_dict['man'] = self.man.name
        if self.woman:
            team_dict['woman'] = self.woman.name
        if self.bear:
            team_dict['bear'] = self.bear.name
        return str(team_dict)
    

class Activity(db.Model):
    '''
    Activities that earn points.

    Columns:
    id (int)   : Primary key
    name (str) : The text description of the activity
    pts (int)  : How many points that activity is worth
    type (str) ["good", "bad"] : The type of activity it is. Bad News Bears will only get points for "bad" activities; others will get points for "good" activities.

    Relationships:
    participant_association (Query) : Relationship to Participant_Activity_Association table
    '''
    __tablename__ = "Activity"
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    pts  = db.Column(db.Integer, unique=False, nullable=False)
    type = db.Column(db.String(100), unique=False, nullable=False)
    participant_association = db.relationship('Participant_Activity_Association', back_populates='activity')


@app.route('/', methods = ('GET', 'POST'))
def index():
    # Check if the selected league ID is in session
    if session.get('selected_league_id') is None:
        selected_league_id = DEFAULT_LEAGUE_ID
    
    # Render the page with the selected league
    # You can retrieve the league data and pass it to the template
    all_leagues = League.query.all()
    selected_league = League.query.get(selected_league_id)
    players = sorted(selected_league.players, key=calculate_player_points, reverse=True)
    return render_template('index.html',  players = players, leagues = all_leagues, selected_league_id=selected_league_id)
    
@app.route('/select_league/', methods=['POST'])
def select_league():
    league_id = request.form.get('league_id')
    session['selected_league_id'] = league_id
    return 'League ID updated successfully'

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


@app.route('/score_episode/<int:episode>', methods = ('GET', 'POST'))
def score_episode(episode):
    selected_league_id = session.get('selected_league_id')
    
    if request.method == 'GET':
        activities = Activity.query.all()
        players    = League.query.filter_by(id = selected_league_id).one().players

        # men   = Participant.query.filter_by(gender = 'male'  ) # Participant.query.join(Team, (Team.man_id   == Participant.id) & (Team.episode == episode))
        # women = Participant.query.filter_by(gender = 'female') # Participant.query.join(Team, (Team.woman_id == Participant.id) & (Team.episode == episode))
        # bears = Participant.query.join(Team, (Team.bear_id  == Participant.id)) # Participant.query.join(Team, (Team.bear_id  == Participant.id) & (Team.episode == episode))
        men   = Participant.query.join(Team, (Team.man_id == Participant.id) & (Team.episode == episode)) \
                         .join(Player, Player.id == Team.owner_id) \
                         .filter(Player.league_id == selected_league_id)
                                       
        women = Participant.query.join(Team, (Team.woman_id == Participant.id) & (Team.episode == episode)) \
                         .join(Player, Player.id == Team.owner_id) \
                         .filter(Player.league_id == selected_league_id)
        bears = Participant.query.join(Team, (Team.bear_id == Participant.id) & (Team.episode == episode)) \
                         .join(Player, Player.id == Team.owner_id) \
                         .filter(Player.league_id == selected_league_id)

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
    return redirect(url_for('score_episode', episode = episode))

@app.route('/select_teams/<int:episode>')
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

@app.route('/save_teams', methods=('GET', 'POST'))
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


@app.route('/fetch_updated_data')
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
    
    # Adding points if Player attended the viewing
    if team.attended_viewing:
        total_points += 10

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

@app.route('/add_player', methods=['POST'])
def add_player():
    if request.method == 'POST':
        selected_league = League.query.filter_by(name = request.form['league_name']).one().id
        db.session.add(Player(name = request.form['player_name']))
        db.session.commit()

        # Redirect to a success page or back to the form page
        return redirect(url_for('add_or_remove_players'))
    
@app.route('/add_or_remove_players', methods=['GET', 'POST'])
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