from sys import path_importer_cache
from app import *
from app.models.league import *

def reset_db():
    '''Resets the db and repopulates the tables.
    '''
    db.drop_all()
    db.create_all()
    populate_activities()
    populate_castmembers()
    populate_leagues()
    populate_episode_one_teams()
    populate_episode_two_teams()
    db.session.commit()
    
def populate_leagues():
    family_league  = League(name = 'family' , id = 1)
    friends_league = League(name = 'friends', id = 2)

    db.session.add(family_league)
    db.session.add(friends_league)
    db.session.commit()

def populate_activities():
    activities = [
        Activity(name = "Miscellaneous 'Awww' moments",                          pts = 1,   type = "good"),
        Activity(name = "Maturely handled a situation with another cast member", pts = 2,   type = "good"),
        Activity(name = "Happy cried",                                           pts = 1,   type = "good"),
        Activity(name = "Did a sweet/romantic gesture for their partner",        pts = 1,   type = "good"),
        Activity(name = "Said “I love you” to date/partner or vice versa",       pts = 3,   type = "good"),
        Activity(name = "Had sex with their partner",                            pts = 2,   type = "good"),
        Activity(name = "Created/performed some type of art",                    pts = 1,   type = "good"),
        Activity(name = "Got their partner’s friends/family’s blessing",         pts = 1,   type = "good"),
        Activity(name = "Post-engagement, had a romantic date",                  pts = 1,   type = "good"),
        Activity(name = "Said “I do” on their wedding day",                      pts = 8,   type = "good"),
        Activity(name = "Partner said “I do” on their wedding day",              pts = 7,   type = "good"),

        # New Activities
        Activity(name = "Another castmember said they wish they were with them/chose them", pts = 2, type = "good"),
        Activity(name = "Showed self-improvement or had a self-realization",                pts = 3, type = "good"),
        Activity(name = "Apologized for something they did wrong",                          pts = 1, type = "good"),
        Activity(name = "Defended their partner to others",                                 pts = 2, type = "good"),
        Activity(name = "Rejected flirtations/advancements from non-partner",               pts = 1, type = "good"),
        Activity(name = "Consoled or supported another castmember ",                        pts = 1, type = "good"),

        # Pods only
        Activity(name = "Got called, someone's #1/only choice/interest",         pts = 1,   type = "good"),
        Activity(name = "Proposed or got proposed to",                           pts = 5,   type = "good"),
        Activity(name = "Got engaged (i.e., the proposal was accepted)",         pts = 5,   type = "good"),        
        Activity(name = "Said they're 'falling for' partner (or vice versa)",    pts = 2,   type = "good"),

        # Fix typo
        Activity(name = "Got/received a gift",                                   pts = 1,   type = "good"),
        # Change to they find them attractive
        Activity(name = "Another contestant says they’re attracted to them",     pts = 0.5, type = "good"),

        Activity(name = "Miscellaneous scandalous thing",                                    pts = 1,  type = "bad"),
        Activity(name = "Sad/angry cried",                                                   pts = 1,  type = "bad"),
        Activity(name = "Argued with partner",                                               pts = 1,  type = "bad"),
        Activity(name = "Yelled at/insulted their partner",                                  pts = 2,  type = "bad"),
        Activity(name = "Can't choose between two (or more) people",                         pts = 1,  type = "bad"),
        Activity(name = "Talked shit about someone else or got talked shit about",           pts = 1,  type = "bad"),
        Activity(name = "Doesn't find partner attractive at reveal (or vice versa)",         pts = 1,  type = "bad"),
        Activity(name = "Walked out during a date without saying bye",                       pts = 1,  type = "bad"),
        Activity(name = "In the pods, dumped or got dumped by someone else",                 pts = 2,  type = "bad"),
        Activity(name = "Got their proposal rejected or rejected a proposal",                pts = 2,  type = "bad"),
        Activity(name = "After being engaged, flirted with someone who isn’t their partner", pts = 2,  type = "bad"),
        Activity(name = "Broke up with partner (post-engagement)",                           pts = 5,  type = "bad"),
        Activity(name = "Cheated on their partner",                                          pts = 5,  type = "bad"),
        Activity(name = "Got dumped on their wedding day",                                   pts = 7,  type = "bad"),
        Activity(name = "Said no on their wedding day",                                      pts = 10, type = "bad"),
    ]

    for activity in activities:
        db.session.add(activity)
    db.session.commit()

def populate_castmembers():
    castmembers = [
        Castmember(name = 'AD'       , gender = 'female'),
        Castmember(name = 'Alejandra', gender = 'female'),
        Castmember(name = 'Amber'    , gender = 'female'),
        Castmember(name = 'Amy C'   , gender = 'female'),
        Castmember(name = 'Amy'      , gender = 'female'),
        Castmember(name = 'Ashley'   , gender = 'female'),
        Castmember(name = 'Brittany' , gender = 'female'),
        Castmember(name = 'Chelsea'  , gender = 'female'),
        Castmember(name = 'Danette'  , gender = 'female'),
        Castmember(name = 'Danielle' , gender = 'female'),
        Castmember(name = 'Jessica'  , gender = 'female'),
        Castmember(name = 'Laura'    , gender = 'female'),
        Castmember(name = 'Mackenzie', gender = 'female'),
        Castmember(name = 'Sarah Ann', gender = 'female'),
        Castmember(name = 'Sunni'    , gender = 'female'),

        Castmember(name = 'Ariel'   , gender = 'male'),
        Castmember(name = 'Austin'  , gender = 'male'),
        Castmember(name = 'Ben'     , gender = 'male'),
        Castmember(name = 'Clay'    , gender = 'male'),
        Castmember(name = 'Deion'   , gender = 'male'),
        Castmember(name = 'Drake'   , gender = 'male'),
        Castmember(name = 'Jamal'   , gender = 'male'),
        Castmember(name = 'Jeramey' , gender = 'male'),
        Castmember(name = 'Jimmy'   , gender = 'male'),
        Castmember(name = 'Johnny'  , gender = 'male'),
        Castmember(name = 'Kenneth' , gender = 'male'),
        Castmember(name = 'Matthew' , gender = 'male'),
        Castmember(name = 'Nolan'   , gender = 'male'),
        Castmember(name = 'Trevor'  , gender = 'male'),
        Castmember(name = 'Vince'   , gender = 'male'),
    ]
    
    for castmember in castmembers:
        db.session.add(castmember)
    db.session.commit()


def process_league_data(league_data, league_name, episode):
    
    for owner_name, team_members in league_data.items():
        # import pdb
        # pdb.set_trace()
        
        print(owner_name, team_members)
        league = League.query.filter_by(name=league_name).one()

        owner = Owner.query.filter_by(name=owner_name, league_id=league.id).first()
        if owner is None:
            owner = Owner(name=owner_name, league_id=league.id)
            db.session.add(owner)
        
        # Combine 'Man', 'Woman', and 'BadNewsBear' lists into one list

        # Collect IDs for all members (including 'Man', 'Woman', and 'BadNewsBear')
        good_member_names = team_members['Man'] + team_members['Woman']
        good_members = [
            member.id
            for member in Castmember.query.filter(Castmember.name.in_(good_member_names)).all()
        ]

        
        # Collect IDs for 'BadNewsBear' members
        bad_members = [
            member.id
            for member in Castmember.query.filter(Castmember.name.in_(team_members['BadNewsBear'])).all()
        ]

        # Create or update team for the owner
        Team.create_or_update_team(owner.id, episode, good_members, bad_members)
        # Append the owner to the league
        league.owners.append(owner)


def populate_episode_one_teams():
    # Define owner-team mappings for the friends league
    friends_league_data = {
        "UC": {
            "Man": ["Kenneth"],
            "Woman": ["Danette"],
            "BadNewsBear": ["Nolan"]
        },
        "Katie": {
            "Man": ["Drake"],
            "Woman": ["Amy"],
            "BadNewsBear": ["Ben"]
        },
        "Marc": {
            "Man": ["Matthew"],
            "Woman": ["Amy C"],
            "BadNewsBear": ["Brittany"]
        },
        "Jannelle": {
            "Man": ["Ariel"],
            "Woman": ["Alejandra"],
            "BadNewsBear": ["Trevor"]
        },
        "Monica": {
            "Man": ["Clay"],
            "Woman": ["Sunni"],
            "BadNewsBear": ["Ashley"]
        }
    }

    # Define owner-team mappings for the family league
    family_league_data_ep1 = {
        "Jawknee": {
            "Man": ["Nolan"],
            "Woman": ["Chelsea"],
            "BadNewsBear": ["Vince"]
        },
        "Jayden": {
            "Man": ["Jamal"],
            "Woman": ["Amy C"],
            "BadNewsBear": ["Austin"]
        },
        "Jeannette": {
            "Man": ["Jimmy"],
            "Woman": ["Amy"],
            "BadNewsBear": ["Sunni"]
        },
        "John Jr.": {
            "Man": ["Kenneth"],
            "Woman": ["Sarah Ann"],
            "BadNewsBear": ["Nolan"]
        },
        "Michelle": {
            "Man": ["Vince"],
            "Woman": ["Brittany"],
            "BadNewsBear": ["AD"]
        },
        "Jannelle": {
            "Man": ["Johnny"],
            "Woman": ["Jessica"],
            "BadNewsBear": ["Danette"]
        },
        "Monica": {
            "Man": ["Deion"],
            "Woman": ["AD"],
            "BadNewsBear": ["Alejandra"]
        },
        "Marc": {
            "Man": ["Matthew"],
            "Woman": ["Mackenzie"],
            "BadNewsBear": ["Laura"]
        }
    }
    
    family_league_data_ep2 = {
        "Marc": {
            "Man": ["Clay", "Jimmy"],
            "Woman": ["Sunni"],
            "BadNewsBear": ["Matthew"]
        },
        "Jawknee": {
            "Man": ["Nolan", "Trevor"],
            "Woman": ["Chelsea"],
            "BadNewsBear": ["Amber"]
        },
        "Jayden": {
            "Man": ["Jamal", "Drake"],
            "Woman": ["Amy C"],
            "BadNewsBear": ["Austin"]
        },
        "Michelle": {
            "Man": ["Vince", "Austin"],
            "Woman": ["Brittany"],
            "BadNewsBear": ["AD"]
        },
        "Jannelle": {
            "Man": ["Matthew"],
            "Woman": ["Jessica"],
            "BadNewsBear": ["Jimmy", "Clay"]
        },
        "Monica": {
            "Man": ["Jimmy"],
            "Woman": ["AD", "Mackenzie"],
            "BadNewsBear": ["Clay"]
        },
        "Jeannette": {
            "Man": ["Kenneth", "Ariel"],
            "Woman": ["Amy"],
            "BadNewsBear": ["Laura"]
        },
        "John Jr.": {
            "Man": ["Trevor", "Kenneth"],
            "Woman": ["Sarah Ann"],
            "BadNewsBear": ["Nolan"]
        }
    }
    Team.query.filter_by(episode = 1).delete()
    process_league_data(family_league_data_ep1 , "family" , 1)
    process_league_data(friends_league_data, "friends", 1)
    db.session.commit()

def populate_episode_two_teams():
    
    family_league_data_ep2 = {
        "Marc": {
            "Man": ["Clay", "Jimmy"],
            "Woman": ["Sunni"],
            "BadNewsBear": ["Matthew"]
        },
        "Jawknee": {
            "Man": ["Nolan", "Trevor"],
            "Woman": ["Chelsea"],
            "BadNewsBear": ["Amber"]
        },
        "Jayden": {
            "Man": ["Jamal", "Drake"],
            "Woman": ["Amy C"],
            "BadNewsBear": ["Austin"]
        },
        "Michelle": {
            "Man": ["Vince", "Austin"],
            "Woman": ["Brittany"],
            "BadNewsBear": ["AD"]
        },
        "Jannelle": {
            "Man": ["Matthew"],
            "Woman": ["Jessica"],
            "BadNewsBear": ["Jimmy", "Clay"]
        },
        "Monica": {
            "Man": ["Jimmy"],
            "Woman": ["AD", "Mackenzie"],
            "BadNewsBear": ["Clay"]
        },
        "Jeannette": {
            "Man": ["Kenneth", "Ariel"],
            "Woman": ["Amy"],
            "BadNewsBear": ["Laura"]
        },
        "John Jr.": {
            "Man": ["Trevor", "Kenneth"],
            "Woman": ["Sarah Ann"],
            "BadNewsBear": ["Nolan"]
        }
    }
    
    db.session.commit()
    process_league_data(family_league_data_ep2 , "family" , 2)
    db.session.commit()    