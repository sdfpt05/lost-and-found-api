from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.models.item import Item
from app.models.lost_report import LostReport
from app.models.found_report import FoundReport
from app.models.claim import Claim
from app.models.reward import Reward
from app.extensions import db
from app.utils.decorators import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    items = Item.query.all()
    return render_template('admin_dashboard.html', items=items)

@bp.route('/items', methods=['POST'])
@login_required
@admin_required
def add_item():
    data = request.form
    item = Item(name=data['name'], description=data.get('description'), image_url=data.get('image_url'))
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Item added successfully'}), 201

@bp.route('/items/<int:item_id>', methods=['PUT'])
@login_required
@admin_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.form
    item.name = data['name']
    item.description = data.get('description')
    item.image_url = data.get('image_url')
    db.session.commit()
    return jsonify({'message': 'Item updated successfully'}), 200

@bp.route('/items/<int:item_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted successfully'}), 200

@bp.route('/reports/lost', methods=['GET'])
@login_required
@admin_required
def view_lost_reports():
    lost_reports = LostReport.query.all()
    return jsonify([report.to_dict() for report in lost_reports]), 200

@bp.route('/reports/found', methods=['GET'])
@login_required
@admin_required
def view_found_reports():
    found_reports = FoundReport.query.all()
    return jsonify([report.to_dict() for report in found_reports]), 200

@bp.route('/claims', methods=['GET'])
@login_required
@admin_required
def view_claims():
    claims = Claim.query.all()
    return jsonify([claim.to_dict() for claim in claims]), 200

@bp.route('/rewards', methods=['GET'])
@login_required
@admin_required
def view_rewards():
    rewards = Reward.query.all()
    return jsonify([reward.to_dict() for reward in rewards]), 200

