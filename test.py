from app import *
reset_db()
katie = Player.query.filter_by(name = "Katie").one()
team1 = Team()
mary = Woman(name="Mary")
team1.woman = mary

mary.activity_association.append(Participant_Activity_Association(episode = 1, activity = Activity.query.all()[0]))
mary.activity_association.append(Participant_Activity_Association(episode = 1, activity = Activity.query.all()[0]))
mary.activity_association.append(Participant_Activity_Association(episode = 2, activity = Activity.query.all()[2]))
mary.activity_association.append(Participant_Activity_Association(episode = 2, activity = Activity.query.all()[20]))

db.session.add(mary)
joe = Man(name="Joe")
db.session.add(joe)
joe.activity_association.append(Participant_Activity_Association(episode = 1, activity = Activity.query.all()[1]))
joe.activity_association.append(Participant_Activity_Association(episode = 1, activity = Activity.query.all()[0]))
joe.activity_association.append(Participant_Activity_Association(episode = 1, activity = Activity.query.all()[0]))
db.session.commit()

katie.teams.append(team1)
p = team1.woman
y = p.activity_association
print(calculate_participant_points(p, "good", 1))