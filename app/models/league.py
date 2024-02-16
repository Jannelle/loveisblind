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
    """

    __tablename__  = 'Castmember_Activity_Association'
    id             = db.Column(db.Integer, primary_key=True)
    castmember_id = db.Column(db.Integer, db.ForeignKey('Castmember.id'))
    activity_id    = db.Column(db.Integer, db.ForeignKey('Activity.id'))
    episode        = db.Column(db.String(50))

    castmember  = db.relationship("Castmember", back_populates="activity_association")
    activity    = db.relationship("Activity", back_populates="castmember_association")


class Castmember(db.Model):
    """
    Represents a castmember (cast member) in the fantasy game.

    Attributes:
        id             (int) : The unique identifier for the castmember.
        name           (str) : The name of the castmember.
        gender         (str) : The gender of the castmember.
        good_teams     (relationship) : Relationship to Team table for teams where the castmember is a "good" member.
        bad_teams      (relationship) : Relationship to Team table for teams where the castmember is a "bad" member.
    """
    __tablename__ = "Castmember"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), unique=True, nullable=False)
    gender        = db.Column(db.String(100), unique=False, nullable=False)
    activity_association = db.relationship("Castmember_Activity_Association", lazy='dynamic', back_populates="castmember")

    good_teams = db.relationship(
        "Team",
        secondary="team_good_members",
        back_populates="good_members"
    )

    bad_teams = db.relationship(
        "Team",
        secondary="team_bad_members",
        back_populates="bad_members"
    )

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

team_good_members = db.Table(
    "team_good_members",
    db.Column("team_id"      , db.Integer, db.ForeignKey("Team.id")      , primary_key=True),
    db.Column("castmember_id", db.Integer, db.ForeignKey("Castmember.id"), primary_key=True)
)

team_bad_members = db.Table(
    "team_bad_members",
    db.Column("team_id"      , db.Integer, db.ForeignKey("Team.id")      , primary_key=True),
    db.Column("castmember_id", db.Integer, db.ForeignKey("Castmember.id"), primary_key=True)
)

class Team(db.Model):
    """
    Represents a team of castmembers in the fantasy game.

    Attributes:
        id            (int) : The unique identifier for the team.
        owner_id      (int) : The id of the owner of the team in the Owner table.
        episode       (int) : The episode number that the team was created for.
        good_members  (relationship) : Relationship to Castmember table for good cast members on the team.
        bad_members   (relationship) : Relationship to Castmember table for bad cast members on the team.
    """
    __tablename__ = "Team"
    id            = db.Column(db.Integer, primary_key=True)
    owner_id      = db.Column(db.Integer, db.ForeignKey("Owner.id"))
    episode       = db.Column(db.Integer)

    good_members = db.relationship(
        "Castmember",
        secondary      = "team_good_members",
        back_populates = "good_teams"
    )

    bad_members = db.relationship(
        "Castmember",
        secondary      = "team_bad_members",
        back_populates = "bad_teams"
    )

    @staticmethod
    def create_or_update_team(owner_id, episode, good_member_ids, bad_member_ids):
        """Create or update a team."""
        existing_team = Team.query.filter_by(owner_id = owner_id, episode = episode).first()
        if existing_team:
            # import pdb
            # pdb.set_trace()
            # print('updating existing team')
            # Update the existing team
            existing_team.good_members = Castmember.query.filter(Castmember.id.in_(good_member_ids)).all()
            existing_team.bad_members  = Castmember.query.filter(Castmember.id.in_(bad_member_ids)).all()
        else:
            # Create a new team
            good_members = Castmember.query.filter(Castmember.id.in_(good_member_ids)).all()
            bad_members = Castmember.query.filter(Castmember.id.in_(bad_member_ids)).all()
            new_team = Team(
                owner_id = owner_id,
                episode  = episode,
                good_members = good_members,
                bad_members = bad_members,
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

    def __repr__(self):
        good_member_names = ", ".join([member.name for member in self.good_members])
        bad_member_names = ", ".join([member.name for member in self.bad_members])
        owner_name = Owner.query.get(self.owner_id).name if self.owner_id else None
        return f"Team(owner_name={owner_name}, episode={self.episode}, good members: {good_member_names}, bad members: {bad_member_names})"


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