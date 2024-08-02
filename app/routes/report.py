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
from datetime import date
import os
from flask_babel import Babel, gettext as _

bp = Blueprint('report', __name__, url_prefix='/report')



# Helper function to handle image uploads
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
            flash('Invalid date or time format. Use YYYY-MM-DD and HH:MM:SS.', 'error')
            return redirect(url_for('report.report_lost_item'))

        item = Item.query.get(data['item_id'])
        if not item:
            flash('Item not found.', 'error')
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
            flash('Lost report submitted successfully', 'success')
            
            # Check if a found report exists for the item
            found_report = FoundReport.query.filter_by(item_id=data['item_id']).first()
            if found_report:
                return redirect(url_for('report.list_all_found_reports'))
            
            return redirect(url_for('report.report_lost_item'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving lost report: {e}', 'error')
            return redirect(url_for('report.report_lost_item'))

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
            flash('Invalid date or time format. Use YYYY-MM-DD and HH:MM:SS.', 'error')
            return redirect(url_for('report.report_found_item'))

        item = Item.query.get(data['item_id'])
        if not item:
            flash('Item not found.', 'error')
            return redirect(url_for('report.report_found_item'))

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
            item.is_recovered = True  # Set is_recovered attribute to True
            db.session.add(found_report)
            db.session.commit()
            flash('Found report submitted successfully', 'success')
            return redirect(url_for('report.report_found_item'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving found report: {e}', 'error')
            return redirect(url_for('report.report_found_item'))

    return render_template('found_report.html')


@bp.route('/comments/<int:item_id>', methods=['GET'])
@login_required
def get_comments(item_id):
    comments = Comment.query.filter_by(item_id=item_id).all()
    return jsonify([{
        'user_id': comment.user_id,
        'username': comment.user.username,
        'content': comment.content,
        'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for comment in comments])


@bp.route('/comments/provide/<int:item_id>', methods=['GET', 'POST'])
@login_required
def provide_comment(item_id):
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('Content is required', 'error')
            return redirect(url_for('report.provide_comment', item_id=item_id))

        comment = Comment(user_id=current_user.id, item_id=item_id, content=content)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully', 'success')
        return redirect(url_for('report.provide_comment', item_id=item_id))

    comments = Comment.query.filter_by(item_id=item_id).all()
    return render_template('add_comment.html', item_id=item_id, comments=comments)

@bp.route('/initiate_claim/<int:found_report_id>', methods=['GET', 'POST'])
@login_required
def initiate_claim(found_report_id):
    found_report = FoundReport.query.get_or_404(found_report_id)
    user_lost_report = LostReport.query.filter_by(user_id=current_user.id, item_id=found_report.item_id).first()

    if not user_lost_report:
        flash('You need to submit a lost report of the item before claiming it.', 'error')
        return redirect(url_for('report.report_lost_item'))

    if request.method == 'POST':
        data = request.form
        item = found_report.item
        claim = Claim(
            user_id=current_user.id,
            found_report_id=found_report_id,
            description=data.get('description')
        )
        try:
            item.is_claimed = True
            db.session.add(claim)
            db.session.commit()
            flash('Claim initiated successfully', 'success')
            return redirect(url_for('report.initiate_claim', found_report_id=found_report_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error initiating claim: {e}', 'error')
            return redirect(url_for('report.initiate_claim', found_report_id=found_report_id))

    return render_template('initiate_claim.html', found_report_id=found_report_id)


@bp.route('/offer_reward/<int:found_report_id>', methods=['GET', 'POST'])
@login_required
def offer_reward(found_report_id):
    if request.method == 'POST':
        data = request.form
        try:
            amount = float(data['amount'])
            

            if amount <= 0:
                flash('Reward amount must be positive.', 'error')
                return redirect(url_for('report.offer_reward', found_report_id=found_report_id))

            found_report = FoundReport.query.get(found_report_id)
            if not found_report:
                flash('Found report not found.', 'error')
                return redirect(url_for('report.offer_reward', found_report_id=found_report_id))

            receiver = found_report.user

            reward = Reward(
                amount=amount,
                receiver_id=receiver.id,
                receiver_username=receiver.username,
                payer_username=current_user.username,
                payer_id=current_user.id,
                found_report_id=found_report_id
            )
            db.session.add(reward)
            db.session.commit()
            flash('Reward offered successfully', 'success')
            return redirect(url_for('report.pay_reward', found_report_id=found_report_id))
        except ValueError:
            flash('Invalid data format. Ensure all fields are correct.', 'error')
            return redirect(url_for('report.offer_reward', found_report_id=found_report_id))
        except KeyError as e:
            flash(f'Missing field: {str(e)}', 'error')
            return redirect(url_for('report.offer_reward', found_report_id=found_report_id))

    return render_template('offer_reward.html', found_report_id=found_report_id)

@bp.route('/receive_reward/<int:found_report_id>', methods=['GET', 'POST'])
@login_required
def receive_reward(found_report_id):
    found_report = FoundReport.query.get_or_404(found_report_id)
    
    if request.method == 'POST':
        data = request.form
        try:
            amount = float(data['amount'])
            date_paid = datetime.strptime(data['date_paid'], '%Y-%m-%d').date()
            payer_username = data['payer_username']
            
            if amount <= 0:
                flash('Reward amount must be positive.', 'error')
                return redirect(url_for('report.receive_reward', found_report_id=found_report_id))
            
            payer = User.query.filter_by(username=payer_username).first()
            if not payer:
                flash('Payer not found.', 'error')
                return redirect(url_for('report.receive_reward', found_report_id=found_report_id))

            reward = Reward.query.filter_by(found_report_id=found_report_id).first()
            if not reward:
                flash('No reward offered for this found report.', 'error')
                return redirect(url_for('report.receive_reward', found_report_id=found_report_id))

            # Ensure that the receiver of the reward is the one who submitted the found report
            if found_report.user_id != current_user.id:
                flash('You are not authorized to receive this reward.', 'error')
                return redirect(url_for('report.receive_reward', found_report_id=found_report_id))

            # Ensure that the reward exists and is still valid
            if reward.payer_id != payer.id or reward.amount <= 0:
                flash('Invalid reward or reward has already been processed.', 'error')
                return redirect(url_for('report.receive_reward', found_report_id=found_report_id))

            reward.amount = amount
            reward.date_paid = date_paid
            reward.payer_username = payer_username
            reward.payer_id = payer.id
            db.session.commit()
            flash('Reward received successfully', 'success')
            return redirect(url_for('report.receive_reward', found_report_id=found_report_id))
        except ValueError:
            flash('Invalid data format. Ensure all fields are correct.', 'error')
            return redirect(url_for('report.receive_reward', found_report_id=found_report_id))
        except KeyError as e:
            flash(f'Missing field: {str(e)}', 'error')
            return redirect(url_for('report.receive_reward', found_report_id=found_report_id))

    return render_template('receive_reward.html', found_report_id=found_report_id)


@bp.route('/list_found_reports', methods=['GET'])
@login_required
def list_all_found_reports():
    try:  
        
        page = request.args.get('page', 1, type=int)  
        per_page = 4  
 
        found_reports_paginated = FoundReport.query.paginate(page=page, per_page=per_page)  
          
        return render_template('list_found_reports.html', found_reports=found_reports_paginated)  
    except Exception as e:  
        flash(f'Error: {str(e)}', 'error')  
        return redirect(url_for('user.dashboard'))

@bp.route('/list_lost_reports', methods=['GET'])
@login_required
def list_all_lost_reports():
    try:  
        # Get the page number from the query string; default is 1  
        page = request.args.get('page', 1, type=int)  
        per_page = 2  # Number of reports per page  

        # Query the LostReport and paginate  
        lost_reports_paginated = LostReport.query.paginate(page=page, per_page=per_page)  
        
        # Pass the pagination object to the template  
        return render_template('list_lost_reports.html', lost_reports=lost_reports_paginated)  
    except Exception as e:  
        flash(f'Error: {str(e)}', 'error')  
        return redirect(url_for('user.dashboard')) 

@bp.route('/pay_reward/<int:found_report_id>', methods=['GET', 'POST'])
@login_required
def pay_reward(found_report_id):
    found_report = FoundReport.query.get_or_404(found_report_id)

    reward = Reward.query.filter_by(found_report_id=found_report_id).first()
    if not reward:
        flash('No reward offered for this found report. Please offer a reward first.', 'error')
        return redirect(url_for('report.offer_reward', found_report_id=found_report_id))

    #if reward.date_paid:
       #flash('This reward has already been paid. Please offer a new reward.', 'error')
        #return redirect(url_for('report.offer_reward', found_report_id=found_report_id))

    if request.method == 'POST':
        data = request.form
        try:
            amount = float(data['amount'])
            date_paid = datetime.strptime(data['date_paid'], '%Y-%m-%d').date()

            if amount <= 0:
                flash('Reward amount must be positive.', 'error')
                return redirect(url_for('report.pay_reward', found_report_id=found_report_id))

            #if amount != reward.amount:
                #flash('Entered amount does not match the offered reward amount.', 'error')
                #return redirect(url_for('report.pay_reward', found_report_id=found_report_id))

            reward.date_paid = date_paid
            db.session.commit()
            flash('Reward paid successfully', 'success')
            return redirect(url_for('report.pay_reward', found_report_id=found_report_id))
        except ValueError:
            flash('Invalid data format. Ensure all fields are correct.', 'error')
            return redirect(url_for('report.pay_reward', found_report_id=found_report_id))
        except KeyError as e:
            flash(f'Missing field: {str(e)}', 'error')
            return redirect(url_for('report.pay_reward', found_report_id=found_report_id))

    return render_template('pay_reward.html', found_report=found_report)


@bp.route('/return_item/<int:found_report_id>', methods=['GET', 'POST'])
@login_required
def return_item(found_report_id):
    found_report = FoundReport.query.get_or_404(found_report_id)
    item = found_report.item
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if not user_id:
            flash('User ID is required to return the item.', 'error')
            return redirect(url_for('report.return_item', found_report_id=found_report_id))

        claim = Claim.query.filter_by(found_report_id=found_report_id, user_id=user_id).first()
        if not claim:
            flash('No claim found for this user and found report.', 'error')
            return redirect(url_for('report.return_item', found_report_id=found_report_id))
        
        if found_report.user_id != current_user.id:
            flash('You are not authorized to return this item.', 'error')
            return redirect(url_for('report.list_all_found_reports'))

        if not item.is_claimed:
            flash('Item must be claimed before it can be returned.', 'error')
            return redirect(url_for('report.list_all_found_reports'))

        try:
            item.is_returned = True
            db.session.commit()
            flash('Item returned successfully', 'success')
            return redirect(url_for('report.list_all_found_reports'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error returning item: {e}', 'error')
            return redirect(url_for('report.list_all_found_reports'))

    claims = Claim.query.filter_by(found_report_id=found_report_id).all()
    return render_template('return_item.html', found_report_id=found_report_id, claims=claims)




@bp.route('/my_rewards', methods=['GET'])
@login_required
def view_my_rewards():
    rewards_received = Reward.query.filter_by(receiver_id=current_user.id).all()
    rewards_paid = Reward.query.filter_by(payer_id=current_user.id).all()
    return render_template('view_my_rewards.html', rewards_received=rewards_received, rewards_paid=rewards_paid)

