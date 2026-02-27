from flask import redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message  = 'Please login to view this page.'
login_manager.login_message_category = 'info'

def init_auth(user_service):
  @login_manager.user_loader
  def load_user(id):
    return user_service.get(id)

  @login_manager.unauthorized_handler
  def unauthorized():
    if request.blueprint == 'api':
      abort(400)
    return redirect(url_for('auth.login'))
