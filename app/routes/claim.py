from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.models.claim import Claim
from app.extensions import db

bp = Blueprint('claim', __name__, url_prefix='/claim')

@bp.route('/initiate_claim', methods=['GET', 'POST'])
@login_required
def initiate_claim():
    if request.method == 'POST':
        data = request.form
        claim = Claim(
            user_id=current_user.id,
            report_id=data['report_id'],
            description=data.get('description')
        )
        db.session.add(claim)
        db.session.commit()
        return jsonify({'message': 'Claim initiated successfully'}), 201

    return render_template('initiate_claim.html')