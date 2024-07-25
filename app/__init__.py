import os
import secrets
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from .extensions import db, migrate, bcrypt, login_manager, mail
from .models import user, item, lost_report, found_report, claim, reward, comment, password_reset
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    load_dotenv()
    
    # Setup secret key from environment variable or generate one if not set
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))
    
    app.config.from_object('config.Config')
    app.config.from_pyfile('config.py', silent=True)

    register_extensions(app)
    register_blueprints(app)
    configure_cors(app)

    return app

def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return user.User.query.get(int(user_id))

def register_blueprints(app):
    from .routes import auth, admin, user, item, comment, main, report, upload, password_reset
    app.register_blueprint(auth.bp,  url_prefix='/auth')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(user.bp)
    app.register_blueprint(item.bp)
    app.register_blueprint(report.bp)
    app.register_blueprint(comment.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(password_reset.bp)


def configure_cors(app):
    CORS(app, supports_credentials=True)

