from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.item import Item
from app.models.lost_report import LostReport
from app.models.found_report import FoundReport
from app.models.claim import Claim
from app.models.reward import Reward
from app.extensions import db
from app.utils.image_utils import handle_image_upload
from app.utils.decorators import admin_required
import os

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    try:
        lost_reports = LostReport.query.all()
        found_reports = FoundReport.query.all()
        claims = Claim.query.all()
        rewards = Reward.query.all()
        return render_template('admin_dashboard.html', lost_reports=lost_reports, found_reports=found_reports, claims=claims, rewards=rewards)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@bp.route('/items', methods=['GET', 'POST'])
@login_required
@admin_required
def add_item():
    if request.method == 'POST':
        try:
            data = request.form
            item_name = data['name']
            
            # Check if an item with the same name already exists
            existing_item = Item.query.filter_by(name=item_name).first()
            if existing_item:
                flash('Item with this name already exists', 'error')
                return redirect(url_for('admin.add_item'))
            
            image_url = handle_image_upload(request.files.get('image'), None) 
            item = Item(name=item_name, description=data.get('description'), image_url=image_url)
            db.session.add(item)
            db.session.commit()
            
            flash('Item added successfully', 'success')
            return redirect(url_for('admin.list_items'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('admin.add_item'))
    
    return render_template('add_item.html')


@bp.route('/list_items', methods=['GET'])  
@login_required  
@admin_required  
def list_items():  
    try:  
        # Get the current page number from the query parameters, default to 1  
        page = request.args.get('page', 1, type=int)  
        
        # Number of items to display per page  
        items_per_page = 5  
        
        # Query for items, paginating results  
        items_query = Item.query.paginate(page=page, per_page=items_per_page)  
        
        # Pass items, current page, and total pages to the template  
        return render_template(  
            'list_items.html',  
            items=items_query.items,  
            current_page=items_query.page,  
            total_pages=items_query.pages  
        )  
    except Exception as e:  
        flash(f'Error: {str(e)}', 'error')  
        return redirect(url_for('admin.dashboard')) 

@bp.route('/items/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            data = request.form
            image_url = handle_image_upload(request.files.get('image'), item_id)  
            item.name = data['name']
            item.description = data.get('description')
            if image_url:
                item.image_url = image_url
            db.session.commit()
            flash('Item updated successfully', 'success')
            return redirect(url_for('admin.list_items'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('admin.update_item', item_id=item_id))
    
    return render_template('update_item.html', item=item)


@bp.route('/items/<int:item_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_item(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully', 'success')
        return jsonify({'message': 'Item deleted successfully'}), 200
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return jsonify({'error': str(e)}), 500


@bp.route('/reports/lost', methods=['GET'])  
@login_required  
@admin_required  
def view_lost_reports():  
    try:  
        # Get the page number from the query string; default is 1  
        page = request.args.get('page', 1, type=int)  
        per_page = 2  # Number of reports per page  

        # Query the LostReport and paginate  
        lost_reports_paginated = LostReport.query.paginate(page=page, per_page=per_page)  
        
        # Pass the pagination object to the template  
        return render_template('view_lost_reports.html', lost_reports=lost_reports_paginated)  
    except Exception as e:  
        flash(f'Error: {str(e)}', 'error')  
        return redirect(url_for('admin.dashboard')) 


@bp.route('/reports/found', methods=['GET'])
@login_required
@admin_required
def view_found_reports():
    try:
        found_reports = FoundReport.query.all()
        return render_template('view_found_reports.html', found_reports=found_reports)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@bp.route('/claims', methods=['GET'])
@login_required
@admin_required
def view_claims():
    try:
        claims = Claim.query.all()
        return render_template('view_claims.html', claims=claims)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@bp.route('/rewards', methods=['GET'])
@login_required
@admin_required
def view_rewards():
    try:
        rewards = Reward.query.all()
        return render_template('view_rewards.html', rewards=rewards)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@bp.route('/reports/lost/<int:lost_report_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_lost_report(lost_report_id):
    try:
        report = LostReport.query.get_or_404(lost_report_id)
        if report.approved:
            flash('Lost report already approved', 'error')
            return redirect(url_for('admin.view_lost_reports'))
        
        report.approved = True
        db.session.commit()
        flash('Lost report approved successfully', 'success')
        return redirect(url_for('admin.view_lost_reports'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.view_lost_reports'))

@bp.route('/list_recovered_items', methods=['GET'])
@login_required
@admin_required
def list_recovered_items():
    try:
        recovered_items = Item.query.join(FoundReport).filter(FoundReport.item_id == Item.id).all()
        return render_template('list_recovered_items.html', items=recovered_items)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@bp.route('/list_returned_items', methods=['GET'])
@login_required
@admin_required
def list_returned_items():
    try:
        returned_items = Item.query.filter_by(is_returned=True).all()
        return render_template('list_returned_items.html', items=returned_items)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))
