import os

class Config:
    #SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://dinah_5:946Vp9ukptGKnMUiOOg3SVsNOHxPMPjD@dpg-cqilr6mehbks73c0996g-a.oregon-postgres.render.com/lost_and_found_x71k')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///lost_and_found.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'
    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_SECURE = False
    DEBUG = False  # Set to False in production
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

    # Uploads folder configuration
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit for file uploads