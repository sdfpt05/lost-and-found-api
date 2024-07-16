from app.extensions import db

class FoundReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    date_reported = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)
