from app.extensions import db
from sqlalchemy import ForeignKey


class League(db.Model):
    """
    Represents a league in the fantasy game.

    Attributes:
        id   (int) : The unique identifier for the league.
        name (str) : The name of the league.
        owners (relationship): Relationship to Owner table.
    """    
    __tablename__ = "League"
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), unique=True, nullable=False)
    owners = db.relationship('Owner', back_populates='league', uselist=True)

    # Define league_slug property
    @property
    def league_slug(self):
        import regex as re
        # Convert name to lowercase and replace spaces with hyphens
        slug = re.sub(r'\s+', '-', self.name.lower())
        # Remove any non-alphanumeric characters except hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        return slug
    
viewing_owner_association = db.Table('viewing_owner_association',
    db.Column('viewing_id', db.Integer, db.ForeignKey('Viewing.id')),
    db.Column('owner_id', db.Integer, db.ForeignKey('Owner.id'))
)

class Owner(db.Model):
    """
    Represents a team owner in the fantasy game.

    Attributes:
        id         (int) : The unique identifier for the owner.
        name       (str) : The name of the owner.
        league_id  (int) : The foreign key referencing the League table.
        teams      (relationship) : Relationship to Team table.
        viewings   (relationship) : Relationship to Viewing table through viewing_owner_association table.
        league     (relationship) : Relationship to League table.
    """
    __tablename__ = "Owner"
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100), unique=False, nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('League.id'), nullable=False)
    teams     = db.relationship("Team", backref="owner", lazy="dynamic", uselist=True)
    viewings  = db.relationship('Viewing', secondary=viewing_owner_association, back_populates='owners')
    league    = db.relationship("League", lazy=True, back_populates="owners")

    def __repr__(self):
        return f"id: {self.id}\nname: {self.name}\nleague_name: {self.league.name}\n\n"

class Viewing(db.Model):
    """
    Represents a viewing event in the fantasy game.

    Attributes:
        id      (int) : The unique identifier for the viewing event.
        episode (int) : The episode number associated with the viewing event.
        owners (relationship): Relationship to Owner table through viewing_owner_association table.
    """    
    __tablename__ = 'Viewing'
    id        = db.Column(db.Integer, primary_key=True)
    episode   = db.Column(db.Integer)
    owners   = db.relationship('Owner', secondary=viewing_owner_association, back_populates='viewings')


class Castmember_Activity_Association(db.Model):
    """
    Represents a castmember (cast member) in the fantasy game.

    Attributes:
        id                   (int) : The unique identifier for the castmember.
        name                 (str) : The name of the castmember.
        gender               (str) : The gender of the castmember.
        activity_association (relationship) : Relationship to Castmember_Activity_Association table.
        man_teams            (relationship) : Relationship to Team table for teams where the castmember is a Man.
        woman_teams          (relationship) : Relationship to Team table for teams where the castmember is a Woman.
        bear_teams           (relationship) : Relationship to Team table for teams where the castmember is a Bad News Bear.
    """

    __tablename__  = 'Castmember_Activity_Association'
    id             = db.Column(db.Integer, primary_key=True)
    castmember_id = db.Column(db.Integer, db.ForeignKey('Castmember.id'))
    activity_id    = db.Column(db.Integer, db.ForeignKey('Activity.id'))
    episode        = db.Column(db.String(50))

    castmember = db.relationship("Castmember", back_populates="activity_association")
    activity    = db.relationship("Activity", back_populates="castmember_association")


class Castmember(db.Model):
    """
    Represents a castmember (cast member) in the fantasy game.

    Attributes:
        id                   (int) : The unique identifier for the castmember.
        name                 (str) : The name of the castmember.
        gender               (str) : The gender of the castmember.
        activity_association (relationship) : Relationship to Castmember_Activity_Association table.
        man_teams            (relationship) : Relationship to Team table for teams where the castmember is a Man.
        woman_teams          (relationship) : Relationship to Team table for teams where the castmember is a Woman.
        bear_teams           (relationship) : Relationship to Team table for teams where the castmember is a Bad News Bear.
    """
    __tablename__ = "Castmember"
    id                   = db.Column(db.Integer, primary_key=True)
    name                 = db.Column(db.String(100), unique=True, nullable=False)
    gender               = db.Column(db.String(100), unique=False, nullable=False)
    activity_association = db.relationship('Castmember_Activity_Association', lazy='dynamic', back_populates='castmember')
    man_teams            = db.relationship("Team", lazy='dynamic', uselist=True, primaryjoin="Team.man_id == Castmember.id")
    woman_teams          = db.relationship("Team", lazy='dynamic', uselist=True, primaryjoin="Team.woman_id == Castmember.id")
    bear_teams           = db.relationship("Team", lazy='dynamic', uselist=True, primaryjoin="Team.bear_id == Castmember.id")

    def get_activities(self, episode):
        """
        Get a list of activities associated with the castmember for a specific episode.

        Args:
            episode (int): The episode number for which to fetch activities.

        Returns:
            List of Activity objects.
        """
        activity_assocs = self.activity_association.filter_by(episode=episode)
        activities = []
        for activity_assoc in activity_assocs:
            activities.append(activity_assoc.activity)
        return activities


class Team(db.Model):
    """
    Represents a team of castmembers in the fantasy game.

    Attributes:
        id        (int) : The unique identifier for the team.
        owner_id  (int) : The id of the owner of the team in the Owner table.
        episode   (int) : The episode number that the team was created for.
        man_id    (int) : The foreign key referencing Castmember.id for the Man on the team.
        woman_id  (int) : The foreign key referencing Castmember.id for the Woman on the team.
        bear_id   (int) : The foreign key referencing Castmember.id for the Bad News Bear on the team.
        man       (relationship) : Reference to the Castmember object for the Man on the team.
        woman     (relationship) : Reference to the Castmember object for the Woman on the team.
        bear      (relationship) : Reference to the Castmember object for the Bad News Bear on the team.
    """
    __tablename__ = "Team"
    id       = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("Owner.id"))
    episode  = db.Column(db.Integer)

    man_id   = db.Column(db.Integer, db.ForeignKey('Castmember.id'))
    woman_id = db.Column(db.Integer, db.ForeignKey('Castmember.id'))
    bear_id  = db.Column(db.Integer, db.ForeignKey('Castmember.id'))

    man   = db.relationship("Castmember",
                          primaryjoin    = "Team.man_id == Castmember.id",
                          back_populates = 'man_teams',
                          lazy           = True,
                          uselist        = False
                          )
    woman = db.relationship("Castmember",
                            primaryjoin    = "Team.woman_id == Castmember.id",
                            back_populates = 'woman_teams',
                            lazy           = True,
                            uselist        = False
                            )
    bear  = db.relationship("Castmember",
                           primaryjoin    = "Team.bear_id == Castmember.id",
                           back_populates = 'bear_teams',
                           lazy           = True,
                           uselist        = False
                           )
    

    @staticmethod
    def get_team_for_owner_and_episode(owner_id, episode):
        """Get the team for a owner and episode."""
        return Team.query.filter_by(owner_id=owner_id, episode=episode).first()

    @staticmethod
    def create_or_update_team(owner_id, episode, man_id, woman_id, bear_id):
        """Create or update a team."""
        existing_team = Team.get_team_for_owner_and_episode(owner_id, episode)
        if existing_team:
            # Update the existing team
            existing_team.man_id   = man_id
            existing_team.woman_id = woman_id
            existing_team.bear_id  = bear_id
        else:
            # Create a new team
            new_team = Team(
                owner_id = owner_id,
                episode  = episode,
                man_id   = man_id,
                woman_id = woman_id,
                bear_id  = bear_id
            )
            db.session.add(new_team)

        db.session.commit()

    @property
    def attended_viewing(self):
        """Check if the team's owner attended the viewing."""
        return any(viewing.episode == self.episode for viewing in self.owner.viewings)
    
    def __repr__(self):
        team_dict = {'owner' : self.owner.name}
        if self.man:
            team_dict['man'] = self.man.name
        if self.woman:
            team_dict['woman'] = self.woman.name
        if self.bear:
            team_dict['bear'] = self.bear.name
        return str(team_dict)
    

class Activity(db.Model):
    """
    Represents an activity in the fantasy game.

    Attributes:
        id   (int) : The unique identifier for the activity.
        name (str) : The description of the activity.
        pts  (int) : The points associated with the activity.
        type (str) : The type of activity ("good" or "bad").
        castmember_association (relationship): Relationship to Castmember_Activity_Association table.
    """
    __tablename__ = "Activity"
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    pts  = db.Column(db.Integer, unique=False, nullable=False)
    type = db.Column(db.String(100), unique=False, nullable=False)
    castmember_association = db.relationship('Castmember_Activity_Association', back_populates='activity')