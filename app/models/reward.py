from app.extensions import db

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date_given = db.Column(db.Date, nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='rewards_received')
    payer = db.relationship('User', foreign_keys=[payer_id], back_populates='rewards_paid')

