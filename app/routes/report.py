from flask import Blueprint, request, jsonify, render_template, url_for
from flask_login import login_required, current_user
from app.models.lost_report import LostReport
from app.models.found_report import FoundReport
from app.models.item import Item
from app.models.comment import Comment
from app.models.claim import Claim
from app.extensions import db
from werkzeug.utils import secure_filename
from datetime import datetime
from app.models.reward import Reward
from app.models.user import User
from datetime import date

import os

bp = Blueprint('report', __name__, url_prefix='/report')

# Helper function to handle image uploads
def handle_image_upload(file, item_id):
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            file.save(file_path)
            return url_for('static', filename=f'uploads/{filename}')
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    else:
        print("Invalid file or file type not allowed.")
        return None

@bp.route('/lost', methods=['POST'])
@login_required
def report_lost_item():
    data = request.form
    file = request.files.get('upload_image')

    try:
        date_lost = datetime.strptime(data['date_lost'], '%Y-%m-%d').date()
        time_lost = datetime.strptime(data['time_lost'], '%H:%M:%S').time()
    except ValueError:
        return jsonify({'error': 'Invalid date or time format. Use YYYY-MM-DD and HH:MM:SS.'}), 400

    item = Item.query.get(data['item_id'])
    if not item:
        return jsonify({'error': 'Item not found.'}), 404

    image_url = handle_image_upload(file, data['item_id']) if file else None

    lost_report = LostReport(
        user_id=current_user.id,
        item_id=data['item_id'],
        item_name=item.name,
        date_lost=date_lost,
        time_lost=time_lost,
        description=data.get('description'),
        primary_color=data.get('primary_color'),
        secondary_color=data.get('secondary_color'),
        upload_image=image_url
    )
    try:
        db.session.add(lost_report)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error saving lost report: {e}'}), 500

    return jsonify({'message': 'Lost report submitted successfully'}), 201

@bp.route('/found', methods=['POST'])
@login_required
def report_found_item():
    data = request.form
    file = request.files.get('upload_image')

    try:
        date_found = datetime.strptime(data['date_found'], '%Y-%m-%d').date()
        time_found = datetime.strptime(data['time_found'], '%H:%M:%S').time()
    except ValueError:
        return jsonify({'error': 'Invalid date or time format. Use YYYY-MM-DD and HH:MM:SS.'}), 400

    item = Item.query.get(data['item_id'])
    if not item:
        return jsonify({'error': 'Item not found.'}), 404

    image_url = handle_image_upload(file, data['item_id']) if file else None

    found_report = FoundReport(
        user_id=current_user.id,
        item_id=data['item_id'],
        item_name=item.name,
        date_found=date_found,
        time_found=time_found,
        description=data.get('description'),
        primary_color=data.get('primary_color'),
        secondary_color=data.get('secondary_color'),
        upload_image=image_url
    )
    try:
        db.session.add(found_report)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error saving found report: {e}'}), 500

    return jsonify({'message': 'Found report submitted successfully'}), 201

@bp.route('/comments/<int:item_id>', methods=['GET'])
@login_required
def get_comments(item_id):
    comments = Comment.query.filter_by(item_id=item_id).all()
    return jsonify([comment.to_dict() for comment in comments]), 200

@bp.route('/comments/provide/<int:item_id>', methods=['GET', 'POST'])
@login_required
def provide_comment(item_id):
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            return jsonify({'error': 'Content is required'}), 400

        comment = Comment(user_id=current_user.id, item_id=item_id, content=content)
        db.session.add(comment)
        db.session.commit()
        return jsonify({'message': 'Comment added successfully'}), 201

    return render_template('add_comment.html', item_id=item_id)

@bp.route('/initiate_claim', methods=['GET', 'POST'])
@login_required
def initiate_claim():
    if request.method == 'POST':
        data = request.form
        claim = Claim(
            user_id=current_user.id,
            report_id=data['report_id'],
            description=data.get('description')
        )
        db.session.add(claim)
        db.session.commit()
        return jsonify({'message': 'Claim initiated successfully'}), 201

    return render_template('initiate_claim.html')

@bp.route('/offer_reward/<int:found_report_id>', methods=['GET', 'POST'])
@login_required
def offer_reward(found_report_id):
    if request.method == 'POST':
        data = request.form
        try:
            amount = float(data['amount'])
            date_paid = datetime.strptime(data['date_paid'], '%Y-%m-%d').date()

            if amount <= 0:
                return jsonify({'error': 'Reward amount must be positive.'}), 400

            found_report = FoundReport.query.get(found_report_id)
            if not found_report:
                return jsonify({'error': 'Found report not found.'}), 404

            receiver = found_report.user

            reward = Reward(
                amount=amount,
                date_paid=date_paid,
                receiver_id=receiver.id,
                receiver_username=receiver.username,
                payer_username=current_user.username,
                payer_id=current_user.id
            )
            db.session.add(reward)
            db.session.commit()
            return jsonify({'message': 'Reward offered successfully'}), 201

        except ValueError:
            return jsonify({'error': 'Invalid data format. Ensure all fields are correct.'}), 400
        except KeyError as e:
            return jsonify({'error': f'Missing field: {str(e)}'}), 400

    return render_template('offer_reward.html', found_report_id=found_report_id)

@bp.route('/receive_reward', methods=['GET', 'POST'])
@login_required
def receive_reward():
    if request.method == 'POST':
        data = request.form
        try:
            amount = float(data['amount'])
            date_paid = datetime.strptime(data['date_paid'], '%Y-%m-%d').date()
            payer_username = data['payer_username']
            
            if amount <= 0:
                return jsonify({'error': 'Reward amount must be positive.'}), 400
            
            payer = User.query.filter_by(username=payer_username).first()
            if not payer:
                return jsonify({'error': 'Payer not found.'}), 404
            
            reward = Reward(
                amount=amount,
                date_paid=date_paid,
                receiver_id=current_user.id,
                receiver_username=current_user.username,
                payer_username=payer_username,
                payer_id=payer.id
            )
            db.session.add(reward)
            db.session.commit()
            return jsonify({'message': 'Reward received successfully'}), 201

        except ValueError:
            return jsonify({'error': 'Invalid data format. Ensure all fields are correct.'}), 400
        except KeyError as e:
            return jsonify({'error': f'Missing field: {str(e)}'}), 400

    return render_template('receive_reward.html')

@bp.route('/rewards_offered', methods=['GET'])
@login_required
def rewards_offered():
    rewards = Reward.query.filter_by(payer_username=current_user.username).all()
    return render_template('rewards_offered.html', rewards=rewards)

@bp.route('/rewards_received', methods=['GET'])
@login_required
def rewards_received():
    rewards = Reward.query.filter_by(receiver_username=current_user.username).all()
    return render_template('rewards_received.html', rewards=rewards)



@bp.route('/pay_reward/<int:reward_id>', methods=['POST'])
@login_required
def pay_reward(reward_id):
    reward = Reward.query.get(reward_id)
    
    if not reward:
        return jsonify({'error': 'Reward not found'}), 404
    
    if reward.payer_id != current_user.id:
        return jsonify({'error': 'Unauthorized to pay this reward'}), 403
    
    if reward.date_paid:
        return jsonify({'error': 'Reward already paid'}), 400

    reward.date_paid = date.today()
    
    try:
        db.session.commit()
        return jsonify({'message': 'Reward paid successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error paying reward: {e}'}), 500