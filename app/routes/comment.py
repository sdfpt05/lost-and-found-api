from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from app.models.comment import Comment, db
from app.models.item import Item  # Assuming you have an Item model
from flask_babel import gettext as _

bp = Blueprint('comment', __name__, url_prefix='/comments')

@bp.route('/<int:item_id>', methods=['GET'])
@login_required
def get_comments(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        comments = Comment.query.filter_by(item_id=item_id).order_by(Comment.timestamp.desc()).all()
        return jsonify([comment.to_dict() for comment in comments]), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving comments for item {item_id}: {str(e)}")
        return jsonify({'error': _('An error occurred while retrieving comments')}), 500

@bp.route('/provide/<int:item_id>', methods=['GET', 'POST'])
@login_required
def provide_comment(item_id):
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        content = request.form.get('content')
        if not content or len(content.strip()) == 0:
            return jsonify({'error': _('Comment content is required')}), 400
        
        if len(content) > current_app.config['MAX_COMMENT_LENGTH']:
            return jsonify({'error': _('Comment exceeds maximum allowed length')}), 400
        
        try:
            comment = Comment(user_id=current_user.id, item_id=item_id, content=content)
            db.session.add(comment)
            db.session.commit()
            return jsonify({'message': _('Comment added successfully'), 'comment': comment.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error while adding comment: {str(e)}")
            return jsonify({'error': _('An error occurred while saving the comment')}), 500
        except Exception as e:
            current_app.logger.error(f"Unexpected error while adding comment: {str(e)}")
            return jsonify({'error': _('An unexpected error occurred')}), 500

    comments = Comment.query.filter_by(item_id=item_id).order_by(Comment.timestamp.desc()).all()
    return render_template('add_comment.html', item=item, comments=comments)

@bp.route('/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': _('You are not authorized to delete this comment')}), 403
    
    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': _('Comment deleted successfully')}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Database error while deleting comment: {str(e)}")
        return jsonify({'error': _('An error occurred while deleting the comment')}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error while deleting comment: {str(e)}")
        return jsonify({'error': _('An unexpected error occurred')}), 500