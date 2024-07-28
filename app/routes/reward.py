from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.models.reward import Reward
from app.extensions import db
from datetime import datetime

bp = Blueprint('reward', __name__, url_prefix='/reward')



@bp.route('/my_rewards', methods=['GET'])
@login_required
def view_my_rewards():
    rewards_received = Reward.query.filter_by(receiver_id=current_user.id).all()
    rewards_paid = Reward.query.filter_by(payer_id=current_user.id).all()
    return render_template('view_my_rewards.html', rewards_received=rewards_received, rewards_paid=rewards_paid)
