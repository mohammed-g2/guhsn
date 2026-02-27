from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.ext import db


class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(64), unique=True, index=True)
  username = db.Column(db.String(64), unique=True, index=True)
  password_hash = db.Column(db.String(128))
  confirmed = db.Column(db.Boolean, default=False)
  role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

  def __repr__(self):
    return f'<User {self.username}>'
  
  @property
  def password(self):
    raise AttributeError('password is not a readable attribute')
  
  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)
  
  def verify_password(self, password: str) -> bool:
    return check_password_hash(self.password_hash, password)
