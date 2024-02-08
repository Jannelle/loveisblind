from sys import path_importer_cache
from flask_app import *


def reset_db():
    '''Resets the db and repopulates the tables.
    '''
    db.drop_all()
    db.create_all()
    populate_players()
    populate_activities()
    populate_participants()
    populate_episode_one_teams()
    db.session.commit()
    

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


def populate_episode_one_teams():

    episode = 1

    #### UC ####
    uc             = Player.query.filter_by(name = 'UC').one()
    uc_team        = Team(episode = episode)
    db.session.add(uc_team)

    uc_team.man    = Participant.query.filter_by(name ='Kenneth').one()
    uc_team.woman  = Participant.query.filter_by(name ='Danette').one()
    uc_team.bear   = Participant.query.filter_by(name ='Nolan'  ).one()
    uc.teams.append(uc_team)

    #### Katie ####
    katie             = Player.query.filter_by(name = 'Katie').one()
    katie_team        = Team(episode = episode)
    db.session.add(katie_team)

    katie_team.man    = Participant.query.filter_by(name = 'Drake').one()
    katie_team.woman  = Participant.query.filter_by(name = 'Amy'  ).one()
    katie_team.bear   = Participant.query.filter_by(name = 'Ben'  ).one()
    katie.teams.append(katie_team)


    #### Marc ####
    marc             = Player.query.filter_by(name = 'Marc').one()
    marc_team        = Team(episode = episode)
    db.session.add(marc_team)

    marc_team.man    = Participant.query.filter_by(name = 'Matthew' ).one()
    marc_team.woman  = Participant.query.filter_by(name = 'Amy C.'  ).one()
    marc_team.bear   = Participant.query.filter_by(name = 'Brittany').one()
    marc.teams.append(marc_team)


    #### Jannelle ####
    jannelle             = Player.query.filter_by(name = 'Jannelle').one()
    jannelle_team        = Team(episode = episode)
    db.session.add(jannelle_team)

    jannelle_team.man    = Participant.query.filter_by(name = 'Ariel'    ).one()
    jannelle_team.woman  = Participant.query.filter_by(name = 'Alejandra').one()
    jannelle_team.bear   = Participant.query.filter_by(name = 'Trevor'   ).one()
    jannelle.teams.append(jannelle_team)


    #### Monica ####
    monica             = Player.query.filter_by(name = 'Monica').one()
    monica_team        = Team(episode = episode)
    db.session.add(monica_team)

    monica_team.man    = Participant.query.filter_by(name = 'Clay'  ).one()
    monica_team.woman  = Participant.query.filter_by(name = 'Sunni' ).one()
    monica_team.bear   = Participant.query.filter_by(name = 'Ashley').one()
    monica.teams.append(monica_team)

    for participant in [uc, katie, marc, jannelle, monica]:
        db.session.add(participant)

    db.session.commit()


populate_episode_one_teams()