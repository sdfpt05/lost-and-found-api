from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.models.comment import Comment, db

bp = Blueprint('comment', __name__, url_prefix='/comments')

@bp.route('/<int:item_id>', methods=['GET'])
@login_required
def get_comments(item_id):
    comments = Comment.query.filter_by(item_id=item_id).all()
    return jsonify([comment.to_dict() for comment in comments]), 200



@bp.route('/provide/<int:item_id>', methods=['GET', 'POST'])
@login_required
def provide_comment(item_id):
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        comment = Comment(user_id=current_user.id, item_id=item_id, content=content)
        db.session.add(comment)
        db.session.commit()
        return jsonify({'message': 'Comment added successfully'}), 201

    return render_template('add_comment.html', item_id=item_id)
