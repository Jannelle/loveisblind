from app.main import bp
from functools import wraps
from flask import session
from config import DEFAULT_LEAGUE_ID

def set_default_league_id(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the selected league ID is in session
        selected_league_id = session.get('selected_league_id')
        if selected_league_id is None:
            # If no league is selected, set the default league ID
            session['selected_league_id'] = DEFAULT_LEAGUE_ID
        return f(*args, **kwargs)
    return decorated_function

@set_default_league_id
def calculate_team_points(team):
    '''Calculates how many points a team has. It does so by looping through each Participant in the team.'''
    
    total_points = 0
    
    # Adding points if owner attended the viewing
    if team.attended_viewing:
        total_points += 10

    # Doing a separate loop for the man and woman compared to bear since they require different activity types
    for participant in [team.man, team.woman]:
        if participant: # skip if the participant is None (this shouldn't happen in practice, but happens during testing)
            total_points += calculate_participant_points(participant, "good", team.episode)
        
    if team.bear: # skip if team has no Bad News Bear
        total_points += calculate_participant_points(team.bear, "bad", team.episode)

    return total_points


@bp.app_template_global()
def calculate_owner_points(owner):
    '''Calculates how many points a owner has by looping through all of their teams.'''
    total_points = 0
    for team in owner.teams.all():
        total_points += calculate_team_points(team)
    return total_points

@bp.app_template_global()
@set_default_league_id
def get_activity_count(participant_id, activity_id):
    return len(Participant_Activity_Association.query.filter_by(participant_id = participant_id, activity_id = activity_id).all())


@bp.app_template_global()
@set_default_league_id
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