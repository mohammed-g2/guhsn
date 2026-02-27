from typing import Union
from flask import Flask
from app.models import User
from app.ext import db
from app.errors import (
  UserNotFoundError, PasswordValidationError, UsernameAlreadyExistsError,
  EmailAlreadyExistsError, TokenError, TokenInvalidError)
from app.utils.security import generate_timed_token, decode_timed_token
from app.utils.send_mail import send_mail


class UserService:
  def __init__(self, app: Flask):
    self.app = app
  
  def get(self, id: int) -> Union[User, None]:
    """Get user by id."""
    return User.query.get(int(id))
  
  def get_by_email(self, email: str) -> Union[User, None]:
    """Get user by email account."""
    return User.query.filter_by(email=email).first()
  
  def get_by_username(self, username: str) -> Union[User, None]:
    """Get user py username."""
    return User.query.filter_by(username=username).first()
  
  def register_user(self, email: str, username: str, password: str) -> User:
    """
    Create a new user in the database and send account confirmation email

    :param email: provided email account
    :param username: provided username
    :param password: provided password
    :returns: `User` instance
    :raises EmailAlreadyExistsError: if provided email already registered
    :raises UsernameAlreadyExistsError: if provided username already registered
    """
    user = User.query.filter_by(email=email).first()
    if user is not None:
      raise EmailAlreadyExistsError()
    user = User.query.filter_by(username=username).first()
    if user is not None:
      raise UsernameAlreadyExistsError()
    
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    token = self.generate_confirmation_token(user)
    self.send_confirmation_mail(user, token)
    return user
  
  def authenticate(self, email: str, password: str) -> User:
    """
    verify login credentials

    :param email: the provided email address
    :param password: the provided password
    :return: verified user, instance of `User`
    :raises UserNotFoundError: if no matching email is found
    :raises PasswordValidationError: if password hash does not match
    """
    user = self.get_by_email(email)
    if user is None:
      raise UserNotFoundError()
    if not user.verify_password(password):
      raise PasswordValidationError()
    
    return user
  
  def generate_confirmation_token(self, user: User) -> str:
    """
    generate a token
    
    :param user: instance of `User`
    :returns: confirmation token with payload `{'confirm': user.id}`
    """
    return generate_timed_token({'confirm': user.id})

  def confirm_user(self, user: User, token: str) -> bool:
    """
    use provided toke to change the state of `user.confirmed`

    :return: true and confirm the user if token is valid
    :raises TokenInvalidError: if token pointed at different user's id
    :raises TokenError: if token in invalid, malformed, expired
    """
    decoded = decode_timed_token(token)
    if decoded['confirm'] != user.id:
      raise TokenInvalidError(message='Token does not match the user')
    if not user.confirmed:
      user.confirmed = True
      db.session.add(user)
      db.session.commit()
      return True

  def send_confirmation_mail(self, user: User, token: str) -> None:
    """
    Send confirmation email to the user
    """
    token = self.generate_confirmation_token(user)
    send_mail(
      to=user.email, 
      subject='Confirm Your Email', 
      template='email/confirm', 
      user=user, token=token)
