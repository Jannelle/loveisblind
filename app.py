from curses import pair_content
import os
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, null

from sqlalchemy.sql import func
import pandas as pd

import random
import pdb

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

episode = 1

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
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), unique=True, nullable=False)
    teams = db.relationship("Team", backref="owner", lazy="dynamic", uselist=True)

    def __repr__(self):
        return f'<Player {self.name}>'

def populate_players():
    '''
    Populate the Player table with initial data.
    '''
    players = [
        Player(name="Katie"),
        Player(name="UC"),
        Player(name="Jannelle"),
        Player(name="Marc"),
        Player(name="Monica"),
    ]

    for player in players:
        db.session.add(player)
    db.session.commit()


def populate_activities():
    activities = [
        Activity(name = "Said “I do” on their wedding day",                      pts = 8,   type = "good"),
        Activity(name = "Partner said “I do” on their wedding day",              pts = 7,   type = "good"),
        Activity(name = "Proposed or got proposed to",                           pts = 5,   type = "good"),
        Activity(name = "Got engaged (i.e., the proposal was accepted)",         pts = 5,   type = "good"),
        Activity(name = "Maturely resolved a conflict with another cast member", pts = 2,   type = "good"),
        Activity(name = "Did a sweet/romantic gesture for their partner",        pts = 1,   type = "good"),
        Activity(name = "Had a romantic, drama-free data",                       pts = 1,   type = "good"),
        Activity(name = "Happy cried",                                           pts = 1,   type = "good"),
        Activity(name = "Got called someone’s #1 choice",                        pts = 1,   type = "good"),
        Activity(name = "Said “I love you” to date/partner or vice versa",       pts = 1,   type = "good"),
        Activity(name = "Had sex with their partner",                            pts = 1,   type = "good"),
        Activity(name = "Got their partner’s friends/family’s blessing",         pts = 1,   type = "good"),
        Activity(name = "Got/received a gift",                                   pts = 1,   type = "good"),
        Activity(name = "Another contestant says they’re attracted to them",     pts = 0.5, type = "good"),

        Activity(name = "Says no on their wedding day",                                     pts = 10, type = "bad"),
        Activity(name = "Gets dumped on their wedding day",                                 pts = 7,  type = "bad"),
        Activity(name = "Cheats on their partner",                                          pts = 5,  type = "bad"),
        Activity(name = "Breaks up with partner (post engagement)",                         pts = 5,  type = "bad"),
        Activity(name = "In the pods, gets dumped by or dumps someone else",                pts = 2,  type = "bad"),
        Activity(name = "Gets their proposal rejected or rejects a proposal",               pts = 2,  type = "bad"),
        Activity(name = "Talks shit about someone else or gets talked shit about",          pts = 1,  type = "bad"),
        Activity(name = "After being engaged, flirts with someone who isn’t their partner", pts = 1,  type = "bad"),
        Activity(name = "Can't choose between two (or more) people",                        pts = 1,  type = "bad"),
        Activity(name = "Sad/angry cries",                                                  pts = 1,  type = "bad"),
        Activity(name = "Gets upset and walks out during a date without saying bye",        pts = 1,  type = "bad"),
        Activity(name = "Yells at/insults their partner",                                   pts = 1,  type = "bad"),
    ]

    for activity in activities:
        db.session.add(activity)
    db.session.commit()

def populate_participants():
    participants = [
        Participant(name = 'AD'       , gender = 'female'),
        Participant(name = 'Alejandra', gender = 'female'),
        Participant(name = 'Amber'    , gender = 'female'),
        Participant(name = 'Amy C.'   , gender = 'female'),
        Participant(name = 'Amy'      , gender = 'female'),
        Participant(name = 'Ashley'   , gender = 'female'),
        Participant(name = 'Brittany' , gender = 'female'),
        Participant(name = 'Chelsea'  , gender = 'female'),
        Participant(name = 'Danette'  , gender = 'female'),
        Participant(name = 'Danielle' , gender = 'female'),
        Participant(name = 'Jessica'  , gender = 'female'),
        Participant(name = 'Laura'    , gender = 'female'),
        Participant(name = 'Mackenzie', gender = 'female'),
        Participant(name = 'Sarah Ann', gender = 'female'),
        Participant(name = 'Sunni'    , gender = 'female'),

        Participant(name = 'Ariel'   , gender = 'male'),
        Participant(name = 'Austin'  , gender = 'male'),
        Participant(name = 'Ben'     , gender = 'male'),
        Participant(name = 'Clay'    , gender = 'male'),
        Participant(name = 'Deion'   , gender = 'male'),
        Participant(name = 'Drake'   , gender = 'male'),
        Participant(name = 'Jamal'   , gender = 'male'),
        Participant(name = 'Jeramey' , gender = 'male'),
        Participant(name = 'Jimmy'   , gender = 'male'),
        Participant(name = 'Johnny'  , gender = 'male'),
        Participant(name = 'Kenneth' , gender = 'male'),
        Participant(name = 'Matthew' , gender = 'male'),
        Participant(name = 'Nolan'   , gender = 'male'),
        Participant(name = 'Trevor'  , gender = 'male'),
        Participant(name = 'Vince'   , gender = 'male'),
    ]
    
    for participant in participants:
        db.session.add(participant)
    db.session.commit()

def print_all_players():
    '''Prints each player's name. Mostly for debugging.'''
    [print(p.name) for p in Player.query.all()]

def __repr__(self):
    return f'<Player {self.name}>'    
    
# ...
@app.route('/', methods = ('GET', 'POST'))
def index():
    players = Player.query.all()
    return render_template('index.html', players = players)
    

@app.route('/reset_db/', methods = ('GET', 'POST'))
def reset_db():
    '''Resets the db and repopulates the tables.
    '''
    db.drop_all()
    db.create_all()
    populate_players()
    populate_activities()
    populate_participants()
    fake_data()
    db.session.commit()
    
    return jsonify({"message": "Database reset successfully!"})

def fake_data():
    for i in range(1, 6):
        
        p = Player.query.get(i)

        for e in range(0, 3):
            new_team = Team(episode = e + 1)
            db.session.add(new_team)
            # Men start at id 16, which is why I'm adding + 14 for men (it's not exactly right).
            # I did some janky math to try to make sure everyone gets a different man/woman,
            # but I did it wrong. However, I think the overlap here is actaully good because
            # it will help me test when people draft the same man.
            new_team.woman = Participant.query.get((i * 2) + e)
            new_team.man   = Participant.query.get((i * 2) + e + 14)
            new_team.bear  = Participant.query.get(random.randint(1, 30))
            p.teams.append(new_team)
            db.session.commit()

@app.route('/castmembers.html')
def castmembers():
    participants = Participant.query.all()
    return render_template('castmembers.html', participants = participants)

@app.route('/create/', methods = ('GET', 'POST'))
def create():
    # if request.method == 'POST':
    #     name       = request.form['name']
    #     player = Player(name      = name,
    #                      )
    #     db.session.add(player)
    #     db.session.commit()

    #     return redirect(url_for('index'))

    return render_template('create.html')

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

def read_db():
    for player in Player.query.all():
        print("===" + player.name + "===")
        print(player.teams)
        for team in player.teams:
            print(team.episode)
            for participant in [team.man, team.woman, team.bear]:
                if participant:
                    print(participant.name)


