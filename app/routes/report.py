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
    file = request.files.get('upload_image')  # Get the uploaded file if available

    try:
        date_lost = datetime.strptime(data['date_lost'], '%Y-%m-%d').date()  # Convert to date object
        time_lost = datetime.strptime(data['time_lost'], '%H:%M:%S').time()  #convert to time object
    except ValueError:
        return jsonify({'error': 'Invalid date or time format. Use YYYY-MM-DD and HH:MM:SS.'}), 400

    item = Item.query.get(data['item_id'])
    if not item:
        return jsonify({'error': 'Item not found.'}), 404

    image_url = handle_image_upload(file, data['item_id']) if file else None

    lost_report = LostReport(
        user_id=current_user.id,
        item_id=data['item_id'],
        item_name=item.name,  # Store the item name
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
        item_name=item.name,  # Store the item name
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
