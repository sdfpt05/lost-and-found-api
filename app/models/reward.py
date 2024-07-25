from app.extensions import db

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date_paid = db.Column(db.Date, nullable=False)
    #date_offered = db.Column(db.Date, nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_username = db.Column(db.String(80), nullable=False)
    payer_username = db.Column(db.String(80), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='rewards_received')
    payer = db.relationship('User', foreign_keys=[payer_id], back_populates='rewards_paid')

    def __init__(self, amount, date_paid, receiver_id, receiver_username, payer_username, payer_id):
        self.amount = amount
        self.date_paid = date_paid
        self.receiver_id = receiver_id
        self.receiver_username = receiver_username
        self.payer_username = payer_username
        self.payer_id = payer_id

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'date_paid': self.date_paid.strftime('%Y-%m-%d'),
            'receiver_id': self.receiver_id,
            'receiver_username': self.receiver_username,
            'payer_username': self.payer_username,
            'payer_id': self.payer_id
        }

