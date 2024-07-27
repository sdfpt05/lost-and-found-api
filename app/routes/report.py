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

@bp.route('/lost', methods=['GET', 'POST'])
@login_required
def report_lost_item():
    if request.method == 'POST':
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
            item_name=data.get('item_name'),
            date_lost=date_lost,
            time_lost=time_lost,
            place_lost=data['place_lost'],
            contact=data.get('contact'),
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

    return render_template('lost_report.html')

@bp.route('/found', methods=['GET', 'POST'])
@login_required
def report_found_item():
    if request.method == 'POST':
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
            item_name=data.get('item_name'),
            date_found=date_found,
            time_found=time_found,
            place_found=data['place_found'],
            contact=data.get('contact'),
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

    return render_template('found_report.html')

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

@bp.route('/initiate_claim/<int:found_report_id>', methods=['GET', 'POST'])
@login_required
def initiate_claim(found_report_id):
    if request.method == 'POST':
        data = request.form
        claim = Claim(
            user_id=current_user.id,
            found_report_id=found_report_id,  # Update this line
            description=data.get('description')
        )
        db.session.add(claim)
        db.session.commit()
        return jsonify({'message': 'Claim initiated successfully'}), 201

    return render_template('initiate_claim.html', found_report_id=found_report_id)


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

@bp.route('/list_found_reports', methods=['GET'])
@login_required
def list_all_found_reports():
    found_reports = FoundReport.query.all()
    return render_template('list_found_reports.html', found_reports=found_reports)

@bp.route('/list_lost_reports', methods=['GET'])
@login_required
def list_all_lost_reports():
    lost_reports = LostReport.query.all()
    return render_template('list_lost_reports.html', lost_reports=lost_reports)

@bp.route('/pay_reward', methods=['GET', 'POST'])
@login_required
def pay_reward():
    if request.method == 'POST':
        data = request.form
        try:
            amount = float(data['amount'])
            date_paid = datetime.strptime(data['date_paid'], '%Y-%m-%d').date()
            receiver_username = data['receiver_username']
            
            if amount <= 0:
                return jsonify({'error': 'Reward amount must be positive.'}), 400
            
            receiver = User.query.filter_by(username=receiver_username).first()
            if not receiver:
                return jsonify({'error': 'Receiver not found.'}), 404
            
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
            return jsonify({'message': 'Reward paid successfully'}), 201

        except ValueError:
            return jsonify({'error': 'Invalid data format. Ensure all fields are correct.'}), 400
        except KeyError as e:
            return jsonify({'error': f'Missing field: {str(e)}'}), 400

    return render_template('pay_reward.html')

@bp.route('/my_rewards', methods=['GET'])
@login_required
def view_my_rewards():
    rewards_received = Reward.query.filter_by(receiver_id=current_user.id).all()
    rewards_paid = Reward.query.filter_by(payer_id=current_user.id).all()
    return render_template('view_my_rewards.html', rewards_received=rewards_received, rewards_paid=rewards_paid)
