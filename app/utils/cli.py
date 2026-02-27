import os
from flask import Flask
from config import basedir


def create_cli_commands(app: Flask) -> None:
  @app.cli.command()
  def init():
    """Initialize the application."""
    os.makedirs(os.path.join(basedir, 'data'), exist_ok=True)
    print('> Created "data" folder.')
    os.makedirs(os.path.join(basedir, 'tmp'), exist_ok=True)
    print('> Created "tmp" folder.')

  @app.cli.command()
  def test():
    """Run unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


def create_shell_context(app: Flask) -> None:
  from app.ext import db
  from app.models import Role, User

  @app.shell_context_processor
  def shell_context():
    return dict(db=db, Role=Role, User=User)
