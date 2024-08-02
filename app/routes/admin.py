from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_required
from werkzeug.exceptions import BadRequest
from app.models.item import Item
from app.models.lost_report import LostReport
from app.models.found_report import FoundReport
from app.models.claim import Claim
from app.models.reward import Reward
from app.extensions import db
from app.utils.image_utils import handle_image_upload
from app.utils.decorators import admin_required
from app.services import item_service, report_service, claim_service, reward_service
from app.forms.item_form import ItemForm
from sqlalchemy.orm import joinedload

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Render the admin dashboard with summary statistics."""
    try:
        stats = {
            'lost_reports': LostReport.query.count(),
            'found_reports': FoundReport.query.count(),
            'claims': Claim.query.count(),
            'rewards': Reward.query.count()
        }
        return render_template('admin_dashboard.html', stats=stats)
    except Exception as e:
        current_app.logger.error(f"Error in admin dashboard: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/items', methods=['GET', 'POST'])
@login_required
@admin_required
def add_item():
    """Add a new item."""
    form = ItemForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                image_url = handle_image_upload(form.image.data)
                item = item_service.create_item(form.name.data, form.description.data, image_url)
                return jsonify({'message': 'Item added successfully', 'item_id': item.id}), 201
            except BadRequest as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                current_app.logger.error(f"Error adding item: {str(e)}")
                return jsonify({'error': 'An unexpected error occurred'}), 500
        else:
            return jsonify({'errors': form.errors}), 400
    
    return render_template('add_item.html', form=form)

@bp.route('/list_items', methods=['GET'])
@login_required
@admin_required
def list_items():
    """List all items with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['ITEMS_PER_PAGE']
        items_query = Item.query.paginate(page=page, per_page=per_page)
        return render_template(
            'list_items.html',
            items=items_query.items,
            pagination=items_query
        )
    except Exception as e:
        current_app.logger.error(f"Error listing items: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def manage_item(item_id):
    """Get, update or delete an item."""
    item = Item.query.get_or_404(item_id)

    if request.method == 'GET':
        return render_template('update_item.html', item=item, form=ItemForm(obj=item))

    elif request.method == 'PUT':
        form = ItemForm()
        if form.validate_on_submit():
            try:
                image_url = handle_image_upload(form.image.data) if form.image.data else None
                updated_item = item_service.update_item(item, form.name.data, form.description.data, image_url)
                return jsonify({'message': 'Item updated successfully', 'item_id': updated_item.id}), 200
            except Exception as e:
                current_app.logger.error(f"Error updating item: {str(e)}")
                return jsonify({'error': 'An unexpected error occurred'}), 500
        else:
            return jsonify({'errors': form.errors}), 400

    elif request.method == 'DELETE':
        try:
            item_service.delete_item(item)
            return jsonify({'message': 'Item deleted successfully'}), 200
        except Exception as e:
            current_app.logger.error(f"Error deleting item: {str(e)}")
            return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/reports/<string:report_type>', methods=['GET'])
@login_required
@admin_required
def view_reports(report_type):
    """View lost or found reports with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['REPORTS_PER_PAGE']

        if report_type == 'lost':
            reports = LostReport.query.paginate(page=page, per_page=per_page)
            template = 'view_lost_reports.html'
        elif report_type == 'found':
            reports = FoundReport.query.paginate(page=page, per_page=per_page)
            template = 'view_found_reports.html'
        else:
            return jsonify({'error': 'Invalid report type'}), 400

        return render_template(template, reports=reports.items, pagination=reports)
    except Exception as e:
        current_app.logger.error(f"Error viewing {report_type} reports: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/claims', methods=['GET'])
@login_required
@admin_required
def view_claims():
    """View all claims with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['CLAIMS_PER_PAGE']
        claims = Claim.query.paginate(page=page, per_page=per_page)
        return render_template('view_claims.html', claims=claims.items, pagination=claims)
    except Exception as e:
        current_app.logger.error(f"Error viewing claims: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/rewards', methods=['GET'])
@login_required
@admin_required
def view_rewards():
    """View all rewards with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['REWARDS_PER_PAGE']
        rewards = Reward.query.paginate(page=page, per_page=per_page)
        return render_template('view_rewards.html', rewards=rewards.items, pagination=rewards)
    except Exception as e:
        current_app.logger.error(f"Error viewing rewards: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/reports/lost/<int:lost_report_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_lost_report(lost_report_id):
    """Approve a lost report."""
    try:
        report = report_service.approve_lost_report(lost_report_id)
        return jsonify({'message': 'Lost report approved successfully', 'report_id': report.id}), 200
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error approving lost report: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/list_recovered_items', methods=['GET'])
@login_required
@admin_required
def list_recovered_items():
    """List all recovered items."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['ITEMS_PER_PAGE']
        recovered_items = Item.query.join(FoundReport).filter(FoundReport.item_id == Item.id).paginate(page=page, per_page=per_page)
        return render_template('list_recovered_items.html', items=recovered_items.items, pagination=recovered_items)
    except Exception as e:
        current_app.logger.error(f"Error listing recovered items: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/list_returned_items', methods=['GET'])
@login_required
@admin_required
def list_returned_items():
    """List all returned items."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['ITEMS_PER_PAGE']
        returned_items = Item.query.filter_by(is_returned=True).paginate(page=page, per_page=per_page)
        return render_template('list_returned_items.html', items=returned_items.items, pagination=returned_items)
    except Exception as e:
        current_app.logger.error(f"Error listing returned items: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
