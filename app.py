import os
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import null

from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']  = \
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

episode = 1

# Association table that keeps track of each activity that each participant did
class Participant_Activity_Association(db.Model):
    __tablename__  = 'Participant_Activity_Association'
    id             = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('Participant.id'))
    activity_id    = db.Column(db.Integer, db.ForeignKey('Activity.id')   )
    episode        = db.Column(db.String(50))

    participant = db.relationship("Participant", back_populates = "activity_association")
    activity    = db.relationship("Activity"   , back_populates = "participant_association")



# Association table that keeps track of each team that have that participant as their Bad News Bear
bnb_team_association_table = db.Table(
    'bnb_team_association',
    db.metadata,
    db.Column('bnb_id',  db.Integer, db.ForeignKey('Participant.id')),
    db.Column('team_id', db.Integer, db.ForeignKey('Team.id'))
)

class Participant(db.Model):
    ''' Participants are the Love is Blind cast members. They earn points by completing certain activities.

    Columns:
    id (int)                    : Primary key
    name (str)                  : The participant's full name
    type (str) ["Man", "Woman", "BNB"]:
        This determines which activities will give them points.
        "Man" and "Woman" get points for "good" activities; "BNB" gets points for "bad" activities.
    activity_association (AppenderQuery)  : Collection of activites the Participant has done
    bnb_team (AppenderQuery)    : Collection of teams that have clamed this Participant as a "bad news bear"
    '''
    __tablename__         = "Participant"
    id                    = db.Column(db.Integer, primary_key = True)
    name                  = db.Column(db.String(100), unique = True, nullable = False)
    type                  = db.Column(db.String(100))
    activity_association  = db.relationship('Participant_Activity_Association', lazy = 'dynamic', back_populates = 'participant')
    bnb_team              = db.relationship("Team", secondary = bnb_team_association_table, lazy = 'dynamic', uselist = True)
    
    # JZ note: I don't really know what this means but it helps me create subtypes of Participant
    __mapper_args__ = {
        'polymorphic_identity': 'participants',
        'with_polymorphic': '*',
        "polymorphic_on": type
    }

class Man(Participant):
    ''' Male participants of Love is Blind and the team they belong to. This class is a subtype of Participant.
    '''
    __tablename__ = "Man"
    id        = db.Column(db.Integer, db.ForeignKey("Participant.id"), primary_key = True)
    team_id   = db.Column(db.Integer, db.ForeignKey("Team.id"), nullable = True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'man',
        'with_polymorphic': '*'
    }


class Woman(Participant):
    ''' Female participants of Love is Blind and the team they belong to. This class is a subtype of Participant.
    '''
    __tablename__ = "Woman"
    id        = db.Column(db.Integer, db.ForeignKey("Participant.id"), primary_key = True)
    team_id   = db.Column(db.Integer, db.ForeignKey("Team.id"), nullable = True)

    __mapper_args__ = {
        'polymorphic_identity': 'woman',
        'with_polymorphic': '*'
    }

class Activity(db.Model):
    ''' Activities that earn points.

    Columns:
    id (int)   : Primary key
    name (str) : The text description of the activity
    pts (int)  : How many points that activity is worth
    activity_type (str) ["good", "bad"] : 
        The type of activity it is. Bad News Bears will only get points for "bad" activities; others will get
        points for "good" activities.
    participants (AppenderQuery) : Collection of participants that have done the activity
    '''
    __tablename__ = "Activity"
    id            = db.Column(db.Integer, primary_key = True)
    name          = db.Column(db.String(100), unique = False, nullable = False)
    pts           = db.Column(db.Integer,     unique = False, nullable = False)
    activity_type = db.Column(db.String(100), unique = False, nullable = False)
    participant_association  = db.relationship('Participant_Activity_Association', back_populates = 'activity')


class Player(db.Model):
    '''The Players of the fantasy game. Each player has a name and a team.
    '''
    __tablename__ = "Player"
    id        = db.Column(db.Integer, primary_key = True)
    name      = db.Column(db.String(100), unique = True, nullable = False)
    teams     = db.relationship("Team",
                                backref = "owner",
                                lazy    = True,
                                uselist = True)
    def __repr__(self):
        return f'<Player {self.name}>'

class Team(db.Model):
    '''The Team of participants that own points for the players. Each team can have one Man, one Woman, and one Bad News Bear.

    Columns:
    id (int)            : Primary key
    owner_id (int)      : The id of the owner of the team in the Player table
    episode (int)       : The episode number that the team was created for
    man (Participant)   : The male participant on the team. Comes from the Man table. Has a one-to-one relationship.
    woman (Participant) : The female participant on the team. Comes from the Woman table. Has a one-to-one relationship.
    bnb (Participant)   : The participant on the team that gets points for doing "bad" activities. Each team can have one bear, but each bear can be a part of multiple teams.
    '''
    __tablename__ = "Team"
    id         = db.Column(db.Integer, primary_key = True)
    owner_id   = db.Column(db.Integer, db.ForeignKey("Player.id"))
    episode    = db.Column(db.Integer)
    man        = db.relationship("Man",
                                backref = "team",
                                lazy    = True,
                                uselist = False)
    woman      = db.relationship("Woman",
                                backref = "team",
                                lazy    = True,
                                uselist = False)
    bnb        = db.relationship("Participant",
                                 secondary = bnb_team_association_table,
                                 lazy = True,
                                 uselist = False,
                                 overlaps = "bnb_team"
                                 )
    
def reset_db():
    '''Resets the db and repopulates the tables.
    '''
    db.drop_all()
    db.create_all()
    populate_players()
    populate_activities()
    populate_participants()
    db.session.commit()

def populate_players():
    players = [
        Player(name = "Katie"),
        Player(name = "UC"),
        Player(name = "Jannelle"),
        Player(name = "Marc"),
        Player(name = "Monica"),
    ]

    for player in players:
        db.session.add(player)
    db.session.commit()

def populate_activities():
    activities = [
        Activity(name = "Partner said “I do” on their wedding day",              pts = 7,   activity_type = "good"),
        Activity(name = "Said “I do” on their wedding day",                      pts = 8,   activity_type = "good"),
        Activity(name = "Proposed or got proposed to",                           pts = 5,   activity_type = "good"),
        Activity(name = "Got engaged (i.e., the proposal was accepted)",         pts = 5,   activity_type = "good"),
        Activity(name = "Maturely resolved a conflict with another cast member", pts = 2,   activity_type = "good"),
        Activity(name = "Did a sweet/romantic gesture for their partner",        pts = 1,   activity_type = "good"),
        Activity(name = "Had a romantic, drama-free data",                       pts = 1,   activity_type = "good"),
        Activity(name = "Happy cried",                                           pts = 1,   activity_type = "good"),
        Activity(name = "Got called someone’s #1 choice",                        pts = 1,   activity_type = "good"),
        Activity(name = "Said “I love you” to date/partner or vice versa",       pts = 1,   activity_type = "good"),
        Activity(name = "Had sex with their partner",                            pts = 1,   activity_type = "good"),
        Activity(name = "Got their partner’s friends/family’s blessing",         pts = 1,   activity_type = "good"),
        Activity(name = "Got/received a gift",                                   pts = 1,   activity_type = "good"),
        Activity(name = "Another contestant says they’re attracted to them",     pts = 0.5, activity_type = "good"),

        Activity(name = "Says no on their wedding day",                                     pts = 10, activity_type = "bad"),
        Activity(name = "Gets dumped on their wedding day",                                 pts = 7,  activity_type = "bad"),
        Activity(name = "Cheats on their partner",                                          pts = 5,  activity_type = "bad"),
        Activity(name = "Breaks up with partner (post engagement)",                         pts = 5,  activity_type = "bad"),
        Activity(name = "In the pods, gets dumped by or dumps someone else",                pts = 2,  activity_type = "bad"),
        Activity(name = "Gets their proposal rejected or rejects a proposal",               pts = 2,  activity_type = "bad"),
        Activity(name = "Talks shit about someone else or gets talked shit about",          pts = 1,  activity_type = "bad"),
        Activity(name = "After being engaged, flirts with someone who isn’t their partner", pts = 1,  activity_type = "bad"),
        Activity(name = "Can't choose between two (or more) people",                        pts = 1,  activity_type = "bad"),
        Activity(name = "Sad/angry cries",                                                  pts = 1,  activity_type = "bad"),
        Activity(name = "Gets upset and walks out during a date without saying bye",        pts = 1,  activity_type = "bad"),
        Activity(name = "Yells at/insults their partner",                                   pts = 1,  activity_type = "bad"),
    ]

    for activity in activities:
        db.session.add(activity)
    db.session.commit()

def populate_participants():
    participants = [
        Woman(name = 'Brittany')  ,
        Woman(name = 'Alejandra') ,
        Woman(name = 'AD')        ,
        Woman(name = 'Mackenzie') ,
        Woman(name = 'AmyC')      ,
        Woman(name = 'SarahAnn')  ,
        Woman(name = 'Danette')   ,
        Woman(name = 'Sunni')     ,
        Woman(name = 'Laura')     ,
        Woman(name = 'Jessica')   ,
        Woman(name = 'Danielle')  ,
        Woman(name = 'Chelsea')   ,
        Woman(name = 'Amy')       ,
        Woman(name = 'Amber')     ,
        Woman(name = 'Ashley')    ,

        Man(name = 'Matthew')     ,
        Man(name = 'Kenneth')     ,
        Man(name = 'Austin')      ,
        Man(name = 'Jamal')       ,
        Man(name = 'Jimmy')       ,
        Man(name = 'Vince')       ,
        Man(name = 'Clay')        ,
        Man(name = 'Nolan')       ,
        Man(name = 'Trevor')      ,
        Man(name = 'Drake')       ,
        Man(name = 'Ariel')       ,
        Man(name = 'Jeramey')     ,
        Man(name = 'Deion')       ,
        Man(name = 'Ben')         ,
        Man(name = 'Johnny')      ,
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
@app.route('/')
def index():
    players = Player.query.all()
    return render_template('index.html', players = players)
    
@app.route('/<int:player_id>/')
def player(player_id):
    player = Player.query.get_or_404(player_id)
    return render_template('player.html', player = player)

@app.route('/participant_points.html')
def participant_points():
    participants = Participant.query.all()
    return render_template('participant_points.html', participants = participants)

@app.route('/create/', methods = ('GET', 'POST'))
def create():
    if request.method == 'POST':
        name       = request.form['name']
        player = Player(name      = name,
                         )
        db.session.add(player)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html')

@app.template_global()
def calculate_participant_points(participant, activity_type, episode = None):
        '''Calculates how many points a participant has earned.

        Args:
            participant (Participant) : The participant whose points we are evaluating.
            activity_type (str) ["good", "bad"]: Will be used to filter which activities will give that participant points.
        '''
        total_pts = 0
        if episode is not None:
            activity_assocs_to_search = participant.activity_association.filter_by(episode = episode)
        else:
            activity_assocs_to_search = participant.activity_association
        for activity_association in activity_assocs_to_search:
            if activity_association.activity.activity_type == activity_type:
                total_pts += activity_association.activity.pts

        return total_pts

# This decorator allows us to use this function in a template
@app.template_global()
def calculate_team_points(team):
    '''Calculates how many points a team has. It does so by looping through each Participant in the team.'''
    
    total_points = 0
    # Doing a separate loop for the man and woman compared to BNB since they require different activity types
    for participant in [team.man, team.woman]:
        if participant: # skip if the participant is None (this shouldn't happen in practice, but happens during testing)
            total_points += calculate_participant_points(participant, "good", team.episode)
        
    if team.bnb: # skip if team has no Bad News Bear
        total_points += calculate_participant_points(team.bnb, "bad", team.episode)

    return total_points

@app.route('/select_teams/<int:episode>')
def select_teams(episode):
    participants = Participant.query.all()
    men          = Man        .query.all()
    women        = Woman      .query.all()

    for i in range(0, 5):
        db.session.add(Team(episode = episode, owner = Player.query.all()[i]))
    
    teams = Team.query.all()
    
    return render_template('select_teams.html'
                           , participants = participants
                           , men          = men
                           , women        = women
                           , teams        = teams
                           , episode      = episode
                           )


@app.route('/save_teams', methods = ('GET', 'POST'))
def save_teams():
    data = request.get_json()
    episode = data.get('episode')
    teams_to_parse = data.get('teams')
    print('parsing')
    print(teams_to_parse)

    for team_to_parse in teams_to_parse:
        if len(team_to_parse) == 0:
            continue
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
                team.bnb   = participant
            else:
                print('!!!!!')
                print(participant_role)
        db.session.add(player)
        db.session.commit()


    return jsonify({"message": "Team lists saved successfully"})

def read_db():
    for player in Player.query.all():
        print("===" + player.name + "===")
        print(player.teams)
        for team in player.teams:
            print(team.episode)
            for participant in [team.man, team.woman, team.bnb]:
                if participant:
                    print(participant.name)
                