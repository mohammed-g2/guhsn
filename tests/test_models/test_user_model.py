import unittest
from app import create_app, db
from app.models import User


class TestUserModel(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.ctx = self.app.app_context()
    self.ctx.push()
    db.create_all()
  
  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.ctx.pop()
  
  def test_create_users(self):
    user_1 = User(username='user 1')
    user_2 = User(username='user 2')
    db.session.add_all([user_1, user_2])
    db.session.commit()

    self.assertListEqual(User.query.all(), [user_1, user_2])

  def test_password_is_not_readable(self):
    user = User(password='pass')
    with self.assertRaises(AttributeError):
      user.password

  def test_password_is_hashed(self):
    user = User(password='pass1')
    self.assertNotEqual(user.password_hash, 'pass1')

  def test_password_salts_are_random(self):
    user_1 = User(password='pass1')
    user_2 = User(password='pass2')
    self.assertNotEqual(user_1.password_hash, user_2.password_hash)

  def test_verify_password_method(self):
    user = User(password='pass1')

    self.assertFalse(user.verify_password('pass2'))
    self.assertTrue(user.verify_password('pass1'))
