import unittest
from flask import current_app
from app import create_app, db


class TestBasics(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.ctx = self.app.app_context()
    self.ctx.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.ctx.pop()

  def test_app_exists(self):
    self.assertIsNotNone(current_app)

  def test_app_testing(self):
    self.assertTrue(current_app.config['TESTING'])
    self.assertEqual(current_app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite://')
    self.assertEqual(str(db.get_engine().url), 'sqlite://')
