from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.claim import Claim
from app.extensions import db

bp = Blueprint('claim', __name__, url_prefix='/claim')

@bp.route('/<int:item_id>', methods=['POST'])
@login_required
def claim_item(item_id):
    claim = Claim(
        user_id=current_user.id,
        item_id=item_id,
        date_claimed=request.form['date_claimed'],
        description=request.form.get('description')
    )
    db.session.add(claim)
    db.session.commit()
    return jsonify({'message': 'Claim submitted successfully'}), 201
