import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEFAULT_LEAGUE_ID = 1

class Config:
    SECRET_KEY = "fjesalikfj339!!!vcknjdlkse"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False