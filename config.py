import os

class Config:
    #SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://dinah5:123456@localhost:5432/lost_and_found_db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///lost_and_found.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'
    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_SECURE = False
    DEBUG = True  # Set to False in production
    BCRYPT_LOG_ROUNDS = 12  # Number of hashing rounds
    # Flask-Login settings
    LOGIN_DISABLED = False  # Set to True to disable login
    

