from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.reward import Reward
from app.extensions import db

bp = Blueprint('reward', __name__, url_prefix='/reward')

@bp.route('/<int:item_id>', methods=['POST'])
@login_required
def offer_reward(item_id):
    reward = Reward(item_id=item_id, payer_id=current_user.id, receiver_id=request.form['receiver_id'], amount=request.form['amount'], date_paid=request.form['date_paid'])
    db.session.add(reward)
    db.session.commit()
    return jsonify({'message': 'Reward offered successfully'}), 201
