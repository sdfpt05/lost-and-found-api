from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.extensions import db, bcrypt, mail
from flask_mail import Message

bp = Blueprint('password_reset', __name__, url_prefix='/password_reset')

@bp.route('/request', methods=['GET', 'POST'])
def request_password_reset():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = PasswordResetToken.generate_token(user)
            db.session.add(token)
            db.session.commit()
            
            reset_link = url_for('password_reset.reset_password', token=token.token, _external=True)
            msg = Message('Password Reset Request', recipients=[email])
            msg.body = f'Please use the following link to reset your password: {reset_link}'
            mail.send(msg)

            flash('If the email is registered, you will receive a password reset link.')
            return redirect(url_for('auth.login_user'))

    return render_template('password_reset_request.html')

@bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    token_entry = PasswordResetToken.query.filter_by(token=token).first()
    if not token_entry or token_entry.is_expired():
        flash('Invalid or expired token.')
        return redirect(url_for('auth.login_user'))

    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('password_reset.reset_password', token=token))

        user = User.query.get(token_entry.user_id)
        if user:
            user.password = new_password
            db.session.delete(token_entry)
            db.session.commit()
            flash('Password has been reset successfully!')
            return redirect(url_for('auth.login_user'))
        else:
            flash('User not found.')
            return redirect(url_for('auth.login_user'))

    return render_template('password_reset_confirm.html', token=token)
