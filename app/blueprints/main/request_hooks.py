from flask import redirect, url_for, request, flash
from flask_login import current_user
from . import main_bp


@main_bp.before_app_request
def before_request():
  if current_user.is_authenticated\
      and not current_user.confirmed\
      and request.blueprint != 'auth'\
      and request.endpoint != 'static':
    flash(
      'Please confirm your account to continue using the website\'s features.',
      category='warning')
