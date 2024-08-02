from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.extensions import db, bcrypt, mail
from flask_mail import Message
from werkzeug.security import generate_password_hash
from flask_babel import gettext as _
import secrets

bp = Blueprint('password_reset', __name__, url_prefix='/password_reset')

@bp.route('/request', methods=['GET', 'POST'])
def request_password_reset():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(32)  # Generate a secure token
            expiration = current_app.config.get('PASSWORD_RESET_EXPIRATION', 3600)  # Default to 1 hour
            reset_token = PasswordResetToken(user_id=user.id, token=token, expiration=expiration)
            db.session.add(reset_token)
            db.session.commit()
            
            reset_link = url_for('password_reset.reset_password', token=token, _external=True)
            msg = Message(_('Password Reset Request'), recipients=[email])
            msg.body = _('Please use the following link to reset your password: {}').format(reset_link)
            try:
                mail.send(msg)
                flash(_('If the email is registered, you will receive a password reset link.'), 'info')
            except Exception as e:
                current_app.logger.error(f"Failed to send password reset email: {e}")
                flash(_('Failed to send password reset email. Please try again later.'), 'error')
            
            return redirect(url_for('auth.login'))
        else:
            # To prevent user enumeration, we'll show the same message even if the email doesn't exist
            flash(_('If the email is registered, you will receive a password reset link.'), 'info')
            return redirect(url_for('auth.login'))

    return render_template('password_reset_request.html')

@bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    token_entry = PasswordResetToken.query.filter_by(token=token).first()
    if not token_entry or token_entry.is_expired():
        flash(_('Invalid or expired token.'), 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash(_('Passwords do not match!'), 'error')
            return redirect(url_for('password_reset.reset_password', token=token))

        if not is_password_strong(new_password):
            flash(_('Password is not strong enough. Please choose a stronger password.'), 'error')
            return redirect(url_for('password_reset.reset_password', token=token))

        user = User.query.get(token_entry.user_id)
        if user:
            user.password = generate_password_hash(new_password)
            db.session.delete(token_entry)
            db.session.commit()
            flash(_('Password has been reset successfully!'), 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(_('User not found.'), 'error')
            return redirect(url_for('auth.login'))

    return render_template('password_reset_confirm.html', token=token)

def is_password_strong(password):
    """
    Check if the password meets the strength requirements.
    Implement your password strength policy here.
    """
    # Example: Password should be at least 8 characters long
    return len(password) >= 8
