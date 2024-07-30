from app.extensions import db

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(250), nullable=True)
    lost_reports = db.relationship('LostReport', back_populates='item', lazy=True)  
    found_reports = db.relationship('FoundReport', back_populates='item', lazy=True)
    comments = db.relationship('Comment', back_populates='item')
    is_returned = db.Column(db.Boolean, default=False, nullable=False)
    is_claimed = db.Column(db.Boolean, default=False, nullable=False)
    is_recovered = db.Column(db.Boolean, default=False, nullable=False)  
