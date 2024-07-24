from app.extensions import db

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(250), nullable=True)
    lost_reports = db.relationship('LostReport', back_populates='item', lazy=True)  
    found_reports = db.relationship('FoundReport', back_populates='item', lazy=True)
    comments = db.relationship('Comment', back_populates='item')