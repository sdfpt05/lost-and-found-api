from app.extensions import db, bcrypt
from flask_login import UserMixin

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    company_type = db.Column(db.String(50), nullable=False)
    location_address = db.Column(db.String(250), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    users = db.relationship('User', back_populates='admin') 

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
