from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.lost_report import LostReport
from app.models.found_report import FoundReport
from app.extensions import db
from datetime import datetime

bp = Blueprint('report', __name__, url_prefix='/report')

@bp.route('/lost', methods=['POST'])
@login_required
def report_lost_item():
    data = request.form
    try:
        date_reported = datetime.strptime(data['date_reported'], '%Y-%m-%d').date()  # Convert to date object
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    lost_report = LostReport(
        user_id=current_user.id,
        item_id=data['item_id'],
        date_reported=date_reported,
        description=data.get('description')
    )
    db.session.add(lost_report)
    db.session.commit()
    return jsonify({'message': 'Lost report submitted successfully'}), 201

@bp.route('/found', methods=['POST'])
@login_required
def report_found_item():
    data = request.form
    try:
        date_reported = datetime.strptime(data['date_reported'], '%Y-%m-%d').date()  # Convert to date object
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    found_report = FoundReport(
        user_id=current_user.id,
        item_id=data['item_id'],
        date_reported=date_reported,
        description=data.get('description')
    )
    db.session.add(found_report)
    db.session.commit()
    return jsonify({'message': 'Found report submitted successfully'}), 201
