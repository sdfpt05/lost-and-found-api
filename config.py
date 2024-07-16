import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://dinah5:123456@localhost/lost_and_found')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_SECURE = False
    # Instance-specific configurations (if any)
