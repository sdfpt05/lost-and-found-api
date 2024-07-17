from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.comment import Comment, db

bp = Blueprint('comment', __name__, url_prefix='/comments')

@bp.route('/<int:item_id>', methods=['POST'])
@login_required
def add_comment(item_id):
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    comment = Comment(user_id=current_user.id, item_id=item_id, content=content)
    db.session.add(comment)
    db.session.commit()
    
    return jsonify(comment.to_dict()), 201

@bp.route('/<int:item_id>', methods=['GET'])
@login_required
def get_comments(item_id):
    comments = Comment.query.filter_by(item_id=item_id).all()
    return jsonify([comment.to_dict() for comment in comments]), 200
