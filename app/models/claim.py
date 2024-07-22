from app.extensions import db
from datetime import datetime

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('found_report.id'), nullable=False)
    claim_reason = db.Column(db.String(255), nullable=False)
    date_initiated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    claim_user = db.relationship('User', backref='claims')
    found_item = db.relationship('FoundReport', backref='claims')

    def __init__(self, user_id, found_item_id, claim_reason):
        self.user_id = user_id
        self.found_item_id = found_item_id
        self.claim_reason = claim_reason

