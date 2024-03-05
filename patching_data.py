from app import create_app, db
from app.models.league import *

def adding_activities():

    # New Activities
    activities_to_add = [

        Activity(name = "Another castmember said they wish they were with them/chose them", pts = 2, type = "good"),
        Activity(name = "Showed self-improvement or had a self-realization",                pts = 3, type = "good"),
        Activity(name = "Apologized for something they did wrong",                          pts = 1, type = "good"),
        Activity(name = "Defended their partner to others",                                 pts = 2, type = "good"),
        Activity(name = "Rejected flirtations/advancements from non-partner",               pts = 1, type = "good"),
        Activity(name = "Consoled or supported another castmember ",                        pts = 1, type = "good"),

        Activity(name = "Family/friends didn't like their partner",                          pts = 1, type = "bad"),
        Activity(name = "Tried to change/control how partner looks",                         pts = 5, type = "bad"),
        Activity(name = "Did/said something cringe",                                         pts = 1, type = "bad"),
        Activity(name = "Backpedaled on something they said in the pods",                    pts = 3, type = "bad"),
        Activity(name = "Revealed a fundamental relatinship incompatibility",                pts = 5, type = "bad"),
        Activity(name = "Expressed regret about another castmember (1-3 pts)",               pts = 3, type = "bad"),
        Activity(name = "Called their partner another castmember/romantic interest/'s name", pts = 3, type = "bad"),
        Activity(name = "Got caught lying",                                                  pts = 5, type = "bad"),
        Activity(name = "Pressured partner to do something for own self-interest",           pts = 3, type = "bad"),
    ]

    for activity in activities_to_add:
        db.session.add(activity)



    db.session.commit()    

def delete_duplicate_activities():
    from sqlalchemy import select, func


    
    # Use the subquery in the delete statement
    # db.session.query(

    # Commit the changes
    db.session.commit()

def editing_activities():
    print('editing activities')
    # # Fix typo
    # gift = Activity.query.filter_by(name = "Got/received a gift").one()
    # gift.name = "Gave/received a gift"

    # # Change to they find them attractive
    # attracted = Activity.query.filter_by(name = "Another contestant says they’re attracted to them").one()
    # attracted.name = "Another castmember finds them attractive"

    argued = Activity.query.filter_by(name = "Argued with partner").one()
    argued.name = "Fought with/had an argument with partner"

    db.session.commit()


def updating_teams():
    teams_for_episode_4 = Team.query.filter_by(episode=4).all()
    for team in teams_for_episode_4:
        new_team = Team(owner_id = team.owner_id
                        , episode = "5 - pre-engagements"
                        , good_members = team.good_members
                        , bad_members  = team.bad_members)
        db.session.add(new_team)

    teams_for_episode_5 = Team.query.filter_by(episode=5).all()
    for team in teams_for_episode_5:
        new_team = Team(owner_id = team.owner_id
                        , episode = "5 - post-engagements"
                        , good_members = team.good_members
                        , bad_members  = team.bad_members)
        db.session.add(new_team)
        db.session.delete(team)
    db.session.commit()    


def updating_activities():

    # Get all rows where episode is currently "5"
    associations_to_update = Castmember_Activity_Association.query.filter_by(episode=5).all()
    print(len(associations_to_update))

    # Update the episode value for each association
    for association in associations_to_update:
        association.episode = "5 - pre-engagements"

    # Commit the changes to the database
    db.session.commit()    


# Entry point of the script
if __name__ == "__main__":
    # Create the Flask application instance
    app = create_app()

    # Run the script within the Flask application context
    with app.app_context():
        delete_duplicate_activities()


