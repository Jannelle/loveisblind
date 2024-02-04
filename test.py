from app import *


katie = Player(name = 'Katie')
mary  = Participant(name = "Mary", gender = "female")
joe   = Participant(name = "Joe", gender = "male")
episode_1_team = Team(episode = 1)
katie.teams.append(episode_1_team)
episode_1_team.woman = mary
episode_1_team.man = joe

