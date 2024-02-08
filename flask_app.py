import json
import os
from sys import activate_stack_trampoline
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), unique=True, nullable=False)
    teams    = db.relationship("Team", backref="owner", lazy="dynamic", uselist=True)
    viewings = db.relationship('Viewing', secondary=viewing_player_association, back_populates='players')

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
        return team_dict

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
    players = sorted(Player.query.all(), key=calculate_player_points, reverse=True)

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
    # return jsonify({team.owner.name : team.__repr__() for team in teams})
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

@app.route('/score_episode/<int:episode>', methods = ('GET', 'POST'))
def score_episode(episode):
    if request.method == 'GET':
        activities = Activity.query.all()
        players    = Player.query.all()

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
    participants = Participant.query.order_by(Participant.name).all()
    men          = Participant.query.filter_by(gender = 'male'  )
    women        = Participant.query.filter_by(gender = 'female')
    players      = Player     .query.order_by(Player.name).all()
    
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

        for participant_item in team_to_parse['participants']:
            name        = participant_item['name']
            origin_list = participant_item['origin_list']
            participant = Participant.query.filter_by(name = name).first()
            if   origin_list == 'menList':
                team.man   = participant
            elif origin_list == 'womenList':
                team.woman = participant
            elif origin_list == 'badNewsBearsList':
                team.bear   = participant
            else:
                print('!!!!!')
                print(origin_list)

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
