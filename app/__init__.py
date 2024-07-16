from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate, bcrypt, login_manager
from .models import user, item, lost_report, found_report, claim, reward

def create_app():
    app = Flask(__name__)
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

def register_blueprints(app):
    from .routes import auth, admin, user, item, report, claim, reward
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(item.bp)
    app.register_blueprint(report.bp)
    app.register_blueprint(claim.bp)
    app.register_blueprint(reward.bp)

def configure_cors(app):
    CORS(app, supports_credentials=True)
