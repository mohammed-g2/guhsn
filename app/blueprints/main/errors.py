from flask import render_template
from flask_wtf.csrf import CSRFError
from . import main_bp


@main_bp.app_errorhandler(404)
def page_not_found(e):
  return render_template('errors/404.html')


@main_bp.app_errorhandler(500)
def internal_server_error(e):
  return render_template('errors/500.html')

@main_bp.app_errorhandler(CSRFError)
def csrf_error(e):
  return render_template('errors/400.html')
