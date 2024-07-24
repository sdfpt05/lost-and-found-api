from app.extensions import db
from sqlalchemy.sql import func

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('found_report.id'), nullable=False)
    claim_reason = db.Column(db.String(255), nullable=False)
    date_claimed = db.Column(db.Date, server_default=func.current_date(), nullable=False)
    time_claimed = db.Column(db.Time, server_default=func.current_time(), nullable=False)

    # Relationships
    claim_user = db.relationship('User', back_populates='claims')
    found_item = db.relationship('FoundReport', back_populates='claims')

    def __init__(self, user_id, found_item_id, claim_reason):
        self.user_id = user_id
        self.found_item_id = found_item_id
        self.claim_reason = claim_reason
        # `date_claimed` and `time_claimed` are automatically set to the current date and time
