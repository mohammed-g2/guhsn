from app.ext import db


class Role(db.Model):
  """User roles."""
  __tablename__ = 'roles'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), unique=True)
  users = db.relationship('User', backref='role', lazy='dynamic')

  def __repr__(self):
    return f'<Role {self.name}>'