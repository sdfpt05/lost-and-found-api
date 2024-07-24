from flask import Blueprint, request, jsonify, url_for
from flask_login import login_required, current_user
from app.models.lost_report import LostReport
from app.models.found_report import FoundReport
from app.models.item import Item
from app.extensions import db
from werkzeug.utils import secure_filename
from datetime import datetime
import os

bp = Blueprint('report', __name__, url_prefix='/report')

# Helper function to handle image uploads
def handle_image_upload(file, item_id):
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return url_for('static', filename=f'uploads/{filename}')
    return None

@bp.route('/lost', methods=['POST'])
@login_required
def report_lost_item():
    data = request.form
    file = request.files.get('upload_image')  # Get the uploaded file if available

    try:
        date_reported = datetime.strptime(data['date_reported'], '%Y-%m-%d').date()  # Convert to date object
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    item = Item.query.get(data['item_id'])
    if not item:
        return jsonify({'error': 'Item not found.'}), 404

    image_url = handle_image_upload(file, data['item_id']) if file else None

    lost_report = LostReport(
        user_id=current_user.id,
        item_id=data['item_id'],
        item_name=item.name,  # Store the item name
        date_reported=date_reported,
        found_date=data.get('found_date'),
        found_time=data.get('found_time'),
        description=data.get('description'),
        primary_color=data.get('primary_color'),
        upload_image=image_url
    )
    db.session.add(lost_report)
    db.session.commit()
    return jsonify({'message': 'Lost report submitted successfully'}), 201

@bp.route('/found', methods=['POST'])
@login_required
def report_found_item():
    data = request.form
    file = request.files.get('upload_image')  # Get the uploaded file if available

    try:
        date_found = datetime.strptime(data['date_found'], '%Y-%m-%d').date()  # Convert to date object
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    item = Item.query.get(data['item_id'])
    if not item:
        return jsonify({'error': 'Item not found.'}), 404

    image_url = handle_image_upload(file, data['item_id']) if file else None

    found_report = FoundReport(
        user_id=current_user.id,
        item_id=data['item_id'],
        item_name=item.name,  # Store the item name
        date_found=date_found,
        time_found=data.get('time_found'),
        description=data.get('description'),
        primary_color=data.get('primary_color'),
        secondary_color=data.get('secondary_color'),
        upload_image=image_url
    )
    db.session.add(found_report)
    db.session.commit()
    return jsonify({'message': 'Found report submitted successfully'}), 201
