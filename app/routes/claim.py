from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.claim import Claim
from app.extensions import db

bp = Blueprint('claim', __name__, url_prefix='/claim')

@bp.route('/initiate', methods=['POST'])
@login_required
def initiate_claim():
    data = request.form
    claim = Claim(user_id=current_user.id, found_item_id=data['found_item_id'], claim_reason=data['claim_reason'])
    db.session.add(claim)
    db.session.commit()
    return jsonify({'message': 'Claim initiated successfully'}), 201
