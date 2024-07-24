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
    # Flask-Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')  
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))  
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@gmail.com')  # Replace with your sender email address

