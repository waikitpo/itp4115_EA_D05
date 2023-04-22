from flask import redirect, url_for
from functools import wraps

from flask_login import current_user
from app.models import User, Company, session


def user_permission_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        type = session.get('type')
        if type == 'user':
            return func(*args, **kwargs)
        else:
            return redirect(url_for('404'))
    return wrapper

def company_permission_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        type = session.get('type')
        if type == 'company':
            return func(*args, **kwargs)
        else:
            return redirect(url_for('404'))
    return wrapper