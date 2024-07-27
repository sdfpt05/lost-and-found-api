from flask import Blueprint


bp = Blueprint('main', __name__)

from . import auth, admin, user, item, report, claim, reward, comment, password_reset
