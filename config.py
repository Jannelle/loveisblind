import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEFAULT_LEAGUE_ID = 1

class Config:
    SECRET_KEY =os.environ.get('SECRET_KEY')
    print(SECRET_KEY)
    print(SECRET_KEY)
    print(SECRET_KEY)
    print(SECRET_KEY)
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False