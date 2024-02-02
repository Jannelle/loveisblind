from app import *
import pdb
reset_db()
for i in range(1, 6):
    
    p = Player.query.get(i)

    for e in range(0, 3):
        new_team = Team(episode = e + 1)
        db.session.add(new_team)
        # Men start at id 16, which is why I'm adding + 14 for men (it's not exactly right).
        # I did some janky math to try to make sure everyone gets a different man/woman,
        # but I did it wrong. However, I think the overlap here is actaully good because
        # it will help me test when people draft the same man.
        new_team.woman = Participant.query.get((i * 2) + e)
        new_team.man   = Participant.query.get((i * 2) + e + 14)
        new_team.bear  = Participant.query.get(random.randint(1, 30))
        p.teams.append(new_team)
        db.session.commit()