from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.admin import Admin
from app.extensions import db, bcrypt

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('auth.register_user'))

        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Email or username already exists!')
            return redirect(url_for('auth.register_user'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('auth.login_user'))

    return render_template('register_user.html')

@bp.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        company_name = request.form['company_name']
        company_type = request.form['company_type']
        location_address = request.form['location_address']
        phone_number = request.form['phone_number']
        zip_code = request.form['zip_code']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('auth.register_admin'))

        if Admin.query.filter_by(email=email).first():
            flash('Email already exists!')
            return redirect(url_for('auth.register_admin'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_admin = Admin(
            company_name=company_name,
            company_type=company_type,
            location_address=location_address,
            phone_number=phone_number,
            zip_code=zip_code,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_admin)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('auth.login_admin'))

    return render_template('register_admin.html')

@bp.route('/login_user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Login failed. Check your email and password.')
            return redirect(url_for('auth.login_user'))

    return render_template('login_user.html')

@bp.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Admin.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Login failed. Check your email and password.')
            return redirect(url_for('auth.login_admin'))

    return render_template('login_admin.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login_user'))
