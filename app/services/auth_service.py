from app.models.user import User
from app.extensions import db

def register_user(username, email, password):
    user = User(username=username, email=email)
    user.password = password
    db.session.add(user)
    db.session.commit()
    return user

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None
