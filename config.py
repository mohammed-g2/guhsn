import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
  ADMIN_EMAIL = os.environ.get('ADMIN')
  # Mail Server config
  MAIL_SERVER = os.environ.get('MAIL_SERVER')
  MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
  MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
    ['true', 'on', '1']
  # Mail Sender config
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
  MAIL_SUBJECT_PREFIX = '[Ghusn]'
  MAIL_SENDER = 'Ghusn Admin <Ghusn@email.com>'
  # Database config
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  @staticmethod
  def init_app(app):
    from app.services import UserService
    app.user_service = UserService(app)


class DevelopmentConfig(Config):
  DEBUG = True
  ENV = 'development'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or\
    f'sqlite:///{os.path.join(basedir, 'data', 'dev.sqlite')}'


class TestingConfig(Config):
  TESTING = True
  ENV = 'testing'
  SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'


class ProductionConfig(Config):
  ENV = 'production'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or\
    f'sqlite:///{os.path.join(basedir, 'data', 'data.sqlite')}'


options = {
  'development': DevelopmentConfig,
  'testing': TestingConfig,
  'production': ProductionConfig
}