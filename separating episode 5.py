from app import create_app, db
from app.models.league import *
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
        updating_activities()
        