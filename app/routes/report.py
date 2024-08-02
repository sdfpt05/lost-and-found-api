from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash, current_app
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
import os
from flask_babel import gettext as _

bp = Blueprint('report', __name__, url_prefix='/report')

# Move this to a separate utility file
def handle_image_upload(file, item_id):
    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
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
            current_app.logger.error(f"Error saving file: {e}")
            return None
    else:
        current_app.logger.warning("Invalid file or file type not allowed.")
        return None

# Helper function to parse date and time
def parse_datetime(date_str, time_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time = datetime.strptime(time_str, '%H:%M:%S').time()
        return date, time
    except ValueError:
        return None, None

@bp.route('/lost', methods=['GET', 'POST'])
@login_required
def report_lost_item():
    if request.method == 'POST':
        data = request.form
        file = request.files.get('upload_image')

        date_lost, time_lost = parse_datetime(data['date_lost'], data['time_lost'])
        if not date_lost or not time_lost:
            flash(_('Invalid date or time format. Use YYYY-MM-DD and HH:MM:SS.'), 'error')
            return redirect(url_for('report.report_lost_item'))

        item = Item.query.get(data['item_id'])
        if not item:
            flash(_('Item not found.'), 'error')
            return redirect(url_for('report.report_lost_item'))

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
            flash(_('Lost report submitted successfully'), 'success')
            
            found_report = FoundReport.query.filter_by(item_id=data['item_id']).first()
            if found_report:
                return redirect(url_for('report.list_all_found_reports'))
            
            return redirect(url_for('report.report_lost_item'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving lost report: {e}")
            flash(_('Error saving lost report. Please try again.'), 'error')
            return redirect(url_for('report.report_lost_item'))

    return render_template('lost_report.html')

# Similar improvements for other routes...

@bp.route('/list_found_reports', methods=['GET'])
@login_required
def list_all_found_reports():
    try:  
        page = request.args.get('page', 1, type=int)  
        per_page = current_app.config['REPORTS_PER_PAGE']
 
        found_reports_paginated = FoundReport.query.paginate(page=page, per_page=per_page)  
          
        return render_template('list_found_reports.html', found_reports=found_reports_paginated)  
    except Exception as e:  
        current_app.logger.error(f"Error listing found reports: {e}")
        flash(_('Error retrieving found reports. Please try again.'), 'error')  
        return redirect(url_for('user.dashboard'))

# Similar improvements for other routes...

@bp.route('/return_item/<int:found_report_id>', methods=['GET', 'POST'])
@login_required
def return_item(found_report_id):
    found_report = FoundReport.query.get_or_404(found_report_id)
    item = found_report.item
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if not user_id:
            flash(_('User ID is required to return the item.'), 'error')
            return redirect(url_for('report.return_item', found_report_id=found_report_id))

        claim = Claim.query.filter_by(found_report_id=found_report_id, user_id=user_id).first()
        if not claim:
            flash(_('No claim found for this user and found report.'), 'error')
            return redirect(url_for('report.return_item', found_report_id=found_report_id))
        
        if found_report.user_id != current_user.id:
            flash(_('You are not authorized to return this item.'), 'error')
            return redirect(url_for('report.list_all_found_reports'))

        if not item.is_claimed:
            flash(_('Item must be claimed before it can be returned.'), 'error')
            return redirect(url_for('report.list_all_found_reports'))

        try:
            item.is_returned = True
            db.session.commit()
            flash(_('Item returned successfully'), 'success')
            return redirect(url_for('report.list_all_found_reports'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error returning item: {e}")
            flash(_('Error returning item. Please try again.'), 'error')
            return redirect(url_for('report.list_all_found_reports'))

    claims = Claim.query.filter_by(found_report_id=found_report_id).all()
    return render_template('return_item.html', found_report_id=found_report_id, claims=claims)

@bp.route('/my_rewards', methods=['GET'])
@login_required
def view_my_rewards():
    rewards_received = Reward.query.filter_by(receiver_id=current_user.id).all()
    rewards_paid = Reward.query.filter_by(payer_id=current_user.id).all()
    return render_template('view_my_rewards.html', rewards_received=rewards_received, rewards_paid=rewards_paid)

