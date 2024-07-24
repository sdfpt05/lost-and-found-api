from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.models.reward import Reward
from app.extensions import db
from datetime import datetime

bp = Blueprint('reward', __name__, url_prefix='/reward')

@bp.route('/offer', methods=['GET', 'POST'])
@login_required
def offer_reward():
    if request.method == 'POST':
        data = request.json
        try:
            amount = float(data['amount'])
            date_paid = datetime.strptime(data['date_paid'], '%Y-%m-%d').date()
            receiver_id = int(data['receiver_id'])

            if amount <= 0:
                return jsonify({'error': 'Reward amount must be positive.'}), 400

            reward = Reward(
                amount=amount,
                date_paid=date_paid,
                receiver_id=receiver_id,
                payer_id=current_user.id
            )
            db.session.add(reward)
            db.session.commit()
            return jsonify({'message': 'Reward offered successfully'}), 201

        except ValueError:
            return jsonify({'error': 'Invalid data format. Ensure all fields are correct.'}), 400
        except KeyError as e:
            return jsonify({'error': f'Missing field: {str(e)}'}), 400

    # Render HTML template for offering a reward
    return render_template('offer_reward.html')

@bp.route('/receive', methods=['GET', 'POST'])
@login_required
def receive_reward():
    if request.method == 'POST':
        data = request.json
        try:
            amount = float(data['amount'])
            date_paid = datetime.strptime(data['date_paid'], '%Y-%m-%d').date()
            payer_id = int(data['payer_id'])

            if amount <= 0:
                return jsonify({'error': 'Reward amount must be positive.'}), 400

            reward = Reward(
                amount=amount,
                date_paid=date_paid,
                receiver_id=current_user.id,
                payer_id=payer_id
            )
            db.session.add(reward)
            db.session.commit()
            return jsonify({'message': 'Reward received successfully'}), 201

        except ValueError:
            return jsonify({'error': 'Invalid data format. Ensure all fields are correct.'}), 400
        except KeyError as e:
            return jsonify({'error': f'Missing field: {str(e)}'}), 400

    # Render HTML template for receiving a reward
    return render_template('receive_reward.html')

@bp.route('/my_rewards', methods=['GET'])
@login_required
def view_my_rewards():
    rewards_received = Reward.query.filter_by(receiver_id=current_user.id).all()
    rewards_paid = Reward.query.filter_by(payer_id=current_user.id).all()
    return render_template('view_my_rewards.html', rewards_received=rewards_received, rewards_paid=rewards_paid)
