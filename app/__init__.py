from flask import Flask
from config import options
from app.ext import db, migrate, mail, csrf, login_manager, init_auth


def create_app(config_name: str) -> Flask:
  """
  Create and initialize the application
  
  :param config_name: configuration name taken from config.options,
  use configuration ENV in ".env" file
  :return: application instance
  """
  app = Flask(__name__)
  app.config.from_object(options[config_name])
  options[config_name].init_app(app)

  db.init_app(app)
  migrate.init_app(app, db)
  mail.init_app(app)
  csrf.init_app(app)
  login_manager.init_app(app)
  init_auth(app.user_service)

  if app.config['ENV'] != 'production':
    migrate.init_app(app, db)

  with app.app_context():
    from app.models import User, Role

  from app.blueprints import main_bp, auth_bp

  app.register_blueprint(main_bp)
  app.register_blueprint(auth_bp, url_prefix='/auth')

  return app
