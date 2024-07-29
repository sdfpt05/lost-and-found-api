from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.models.claim import Claim
from app.extensions import db

bp = Blueprint('claim', __name__, url_prefix='/claim')

