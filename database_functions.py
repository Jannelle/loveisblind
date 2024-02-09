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
    populate_leagues()
    populate_episode_one_teams()
    db.session.commit()
    

def populate_players():
    '''
    Populate the Player table with initial data.
    '''
    players = [
        Player(name="Katie"   ),
        Player(name="UC"      ),
        Player(name="Jannelle"),
        Player(name="Marc"    ),
        Player(name="Monica"  ),
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

def populate_leagues():
    family_league  = League(name = 'family')
    db.session.add(family_league)
    friends_league = League(name = 'friends')
    db.session.add(friends_league)
    db.session.commit()

def populate_episode_one_teams():
    episode = 1
    
    # Define player-team mappings for the friends league
    friends_league_player_mappings = [
        ("UC",        "Kenneth",   "Danette",    "Nolan"    ),
        ("Katie",     "Drake",     "Amy",        "Ben"      ),
        ("Marc",      "Matthew",   "Amy C.",     "Brittany" ),
        ("Jannelle",  "Ariel",     "Alejandra",  "Trevor"   ),
        ("Monica",    "Clay",      "Sunni",      "Ashley"   )
    ]

    
    # Iterate over player-team mappings for the friends league
    for player_name, man_name, woman_name, bear_name in friends_league_player_mappings:
        # Get player object
        player = Player.query.filter_by(name=player_name).first()
        
        # Get participant IDs
        man_id   = Participant.query.filter_by(name=man_name).first().id
        woman_id = Participant.query.filter_by(name=woman_name).first().id
        bear_id  = Participant.query.filter_by(name=bear_name).first().id
        
        # Create or update team for the player
        Team.create_or_update_team(player.id, episode, man_id, woman_id, bear_id)
        
        # Append the player to the friends league
        friends_league = League.query.filter_by(name='friends').one()
        friends_league.players.append(player)

    # Define player-team mappings for the family league
    family_league_player_mappings = [
        ("Jawknee",   "Nolan",     "Chelsea",   "Vince"     ),
        ("Jayden",    "Jamal",     "Amy C.",    "Austin"    ),
        ("Jeannette", "Jimmy",     "Amy",       "Sunni"     ),
        ("John Jr.",  "Kenneth",   "Sarah Ann", "Nolan"     ),
        ("Michelle",  "Vince",     "Brittany",  "AD"        ),
        ("Jannelle",  "Johnny",    "Jessica",   "Danette"   ),
        ("Monica",    "AD",        "Deion",     "Alejandra" ),
        ("Marc",      "Mackenzie", "Matthew",   "Laura"     ),
    ]
    
    # Iterate over player-team mappings for the family league
    for player_name, man_name, woman_name, bear_name in family_league_player_mappings:
        # Create player object
        new_player = Player(name=player_name)
        db.session.add(new_player)
        
        # Get participant IDs
        man_id = Participant.query.filter_by(name=man_name).first().id
        woman_id = Participant.query.filter_by(name=woman_name).first().id
        bear_id = Participant.query.filter_by(name=bear_name).first().id
        
        # Create or update team for the player
        Team.create_or_update_team(new_player.id, episode, man_id, woman_id, bear_id)
        
        # Append the player to the family league
        family_league = League.query.filter_by(name='family').one()
        family_league.players.append(new_player)

    db.session.commit()