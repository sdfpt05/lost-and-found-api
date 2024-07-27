from app.extensions import db
from app.models.item import Item
from datetime import datetime

class LostReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    item_name = db.Column(db.String(150), nullable=True)
    place_lost = db.Column(db.String(150), nullable=False)
    date_lost = db.Column(db.Date, nullable=False)  
    time_lost = db.Column(db.Time, nullable=False) 
    contact = db.Column(db.String(255), nullable=True)  
    description = db.Column(db.String(255), nullable=True)
    primary_color = db.Column(db.String(50), nullable=True)
    secondary_color = db.Column(db.String(50), nullable=True)
    upload_image = db.Column(db.String(250), nullable=True)
    approved = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship('User', back_populates='lost_reports')
    item = db.relationship('Item', back_populates='lost_reports')

    @staticmethod
    def get_item_by_id(item_id):
        return Item.query.get(item_id)

    @staticmethod
    def get_item_by_name(name):
        return Item.query.filter_by(name=name).first()
