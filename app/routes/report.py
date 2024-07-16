from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.lost_report import LostReport
from app.models.found_report import FoundReport
from app.extensions import db

bp = Blueprint('report', __name__, url_prefix='/report')

@bp.route('/lost', methods=['POST'])
@login_required
def report_lost_item():
    data = request.form
    lost_report = LostReport(user_id=current_user.id, item_id=data['item_id'], date_reported=data['date_reported'], description=data.get('description'))
    db.session.add(lost_report)
    db.session.commit()
    return jsonify({'message': 'Lost report submitted successfully'}), 201

@bp.route('/found', methods=['POST'])
@login_required
def report_found_item():
    data = request.form
    found_report = FoundReport(user_id=current_user.id, item_id=data['item_id'], date_reported=data['date_reported'], description=data.get('description'))
    db.session.add(found_report)
    db.session.commit()
    return jsonify({'message': 'Found report submitted successfully'}), 201
