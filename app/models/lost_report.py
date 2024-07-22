from app.extensions import db

class LostReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    date_reported = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=True)