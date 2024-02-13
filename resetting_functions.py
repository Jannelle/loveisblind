from sys import path_importer_cache
from app import *
from app.models.league import *

def reset_db():
    '''Resets the db and repopulates the tables.
    '''
    db.drop_all()
    db.create_all()
    populate_activities()
    populate_participants()
    populate_leagues()
    populate_episode_one_teams()
    db.session.commit()
    
def populate_leagues():
    family_league  = League(name = 'family' , id = 1)
    friends_league = League(name = 'friends', id = 2)

    db.session.add(family_league)
    db.session.add(friends_league)
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


def process_league_data(league_data, league_name, episode):
    for owner_name, team_members in league_data.items():
        league = League.query.filter_by(name=league_name).one()

        # Get owner object or create new one
        # owner = owner.query.filter_by(name=owner_name, league_id=league.id).one()
        # if not owner:
        owner = Owner(name=owner_name, league_id=league.id)
        db.session.add(owner)
        # Get participant IDs
        # print(team_members['Man'])
        # import pdb
        # pdb.set_trace()
        man_id   = Participant.query.filter_by(name=team_members['Man'])        .first().id
        woman_id = Participant.query.filter_by(name=team_members['Woman'])      .first().id
        bear_id  = Participant.query.filter_by(name=team_members['BadNewsBear']).first().id
        
        # Create or update team for the owner
        Team.create_or_update_team(owner.id, episode, man_id, woman_id, bear_id)
        
        # Append the owner to the league
        
        league.owners.append(owner)

def populate_episode_one_teams():
    episode = 1
    
    # Define owner-team mappings for the friends league
    friends_league_data = {
        "UC": {
            "Man"         : "Kenneth",
            "Woman"       : "Danette",
            "BadNewsBear" : "Nolan"
        },
        "Katie": {
            "Man"         : "Drake",
            "Woman"       : "Amy",
            "BadNewsBear" : "Ben"
        },
        "Marc": {
            "Man"         : "Matthew",
            "Woman"       : "Amy C.",
            "BadNewsBear" : "Brittany"
        },
        "Jannelle": {
            "Man"         : "Ariel",
            "Woman"       : "Alejandra",
            "BadNewsBear" : "Trevor"
        },
        "Monica": {
            "Man"         : "Clay",
            "Woman"       : "Sunni",
            "BadNewsBear" : "Ashley"
        }
    }

    # Define owner-team mappings for the family league
    family_league_data = {
        "Jawknee": {
            "Man"         : "Nolan",
            "Woman"       : "Chelsea",
            "BadNewsBear" : "Vince"
        },
        "Jayden": {
            "Man"         : "Jamal",
            "Woman"       : "Amy C.",
            "BadNewsBear" : "Austin"
        },
        "Jeannette": {
            "Man"         : "Jimmy",
            "Woman"       : "Amy",
            "BadNewsBear" : "Sunni"
        },
        "John Jr.": {
            "Man"         : "Kenneth",
            "Woman"       : "Sarah Ann",
            "BadNewsBear" : "Nolan"
        },
        "Michelle": {
            "Man"         : "Vince",
            "Woman"       : "Brittany",
            "BadNewsBear" : "AD"
        },
        "Jannelle": {
            "Man"         : "Johnny",
            "Woman"       : "Jessica",
            "BadNewsBear" : "Danette"
        },
        "Monica": {
            "Man"         : "Deion",
            "Woman"       : "AD",
            "BadNewsBear" : "Alejandra"
        },
        "Marc": {
            "Man"         : "Matthew",
            "Woman"       : "Mackenzie",
            "BadNewsBear" : "Laura"
        },
    }
    
    process_league_data(family_league_data , "family" , episode)
    process_league_data(friends_league_data, "friends", episode)
    db.session.commit()