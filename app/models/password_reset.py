from app.extensions import db
from datetime import datetime, timedelta
import secrets

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    expiration = db.Column(db.Date, nullable=False)

    user = db.relationship('User', backref=db.backref('reset_tokens', lazy=True))

    def is_expired(self):
        return datetime.utcnow() > self.expiration

    @staticmethod
    def generate_token(user):
        token = secrets.token_urlsafe(16)
        expiration = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
        return PasswordResetToken(user_id=user.id, token=token, expiration=expiration)
