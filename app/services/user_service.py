from typing import Union
from flask import Flask
from email_validator import validate_email, EmailNotValidError
from app.models import User
from app.ext import db
from app.errors import (
  UserNotFoundError, PasswordValidationError, UsernameAlreadyExistsError,
  EmailAlreadyExistsError, TokenError, TokenPayloadError)
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

  def confirm_user(self, user: User, token: str) -> bool:
    """
    use provided toke to change the state of `user.confirmed`

    :return: true and confirm the user if token is valid
    :raises TokenInvalidError: if token pointed at different user's id
    :raises TokenError: if token in invalid, malformed, expired
    """
    decoded = decode_timed_token(token)
    if decoded.get('confirm') != user.id:
      raise TokenPayloadError(message='Token does not match the user')
    if not user.confirmed:
      user.confirmed = True
      db.session.add(user)
      db.session.commit()
      return True

  def send_confirmation_mail(self, user: User) -> None:
    """
    Send account confirmation email to the user
    
    :param user: `User` model instance
    """
    token = generate_timed_token({'confirm': user.id})
    send_mail(
      to=user.email, 
      subject='Confirm Your Email', 
      template='email/auth/confirm', 
      user=user, token=token)
  
  def update_profile(self, user: User, username=None) -> None:
    """
    Update user profile info
    
    :param user: `User` model instance
    :param username: user's new username
    :raises UsernameAlreadyExistsError: if username name already in use
    """
    if username == user.username:
      return
    elif User.query.filter_by(username=username).first():
      raise UsernameAlreadyExistsError()
    user.username = username
    db.session.add(user)
    db.session.commit()
    
  
  def update_email_request(self, user: User, new_email: str) -> None:
    """
    Send email to update user's email address.
    
    :param user: `User` model instance
    :param new_email: user's new email
    :raises EmailAlreadyExistsError: if email already exists in database
    """
    email_found = User.query.filter_by(email=new_email).first()
    if email_found:
      raise EmailAlreadyExistsError()
    token = generate_timed_token({
      'email': user.email,
      'new-email': new_email
    })
    send_mail(
      to=new_email, 
      subject='Change Email Address', 
      template='email/auth/update-email', 
      token=token)
    
  def update_email(self, user: User, token: str) -> None:
    """
    Update user's email address
    
    :param user: `User` model instance
    :param token: token included in the url
    :raises TokenPayloadError: if user's email address is mismatched
    """
    decoded = decode_timed_token(token)
    if not user.email == decoded['email']:
      raise TokenPayloadError()
    user.email = decoded['new-email']
    db.session.add(user)
    db.session.commit()
  
  def password_change_request(self, user: User, password: str) -> None:
    """
    Request password change
    
    :param user: `User` model instance
    :param password: user's original password
    :raises PasswordValidationError: if provided password doesn't match
    """
    if not user.verify_password(password):
      raise PasswordValidationError()
    token = generate_timed_token({'change-password': user.id})
    send_mail(
      to=user.email,
      subject='Change Password',
      template='email/auth/change-password',
      token=token)
  
  def change_password(self, user: User, token: str, password: str) -> None:
    """
    Change password
    
    :param user: `User` model instance
    :param token: token included in the url
    :param password: the new password
    :raises TokenPayloadError: if provided token doesn't match
    """
    decoded = decode_timed_token(token)
    if not decoded.get('change-password') == user.id:
      raise TokenPayloadError()
    user.password = password
    db.session.add(user)
    db.session.commit()
  
  def reset_password_request(self, email: str) -> None:
    """
    Send email to request password reset
    
    :param email: user's email
    :raises UserNotFoundError: if user with given email not found
    """
    email_found = User.query.filter_by(email=email).first()
    if not email_found:
      raise UserNotFoundError()
    
    token = generate_timed_token({'reset-password': email})
    send_mail(
      to=email, 
      subject='Reset password', 
      template='email/auth/reset-password',
      token=token)
  
  def reset_password(self, token: str, password: str) -> None:
    """
    Reset user password
    
    :param token: token included in the url
    :param password: the new password
    :raises TokenPayloadError: if email in the token is invalid
    """
    decoded = decode_timed_token(token)
    try:
      email_info = validate_email(
        decoded.get('reset-password'), check_deliverability=False)
      try:
        email = email_info.normalized
      except AttributeError:
        # older version of email-validator fix
        email = email_info.email
    except EmailNotValidError:
      raise TokenPayloadError()
    
    user = User.query.filter_by(email=email).first()
    if not user:
      raise TokenPayloadError()
    
    user.password = password
    db.session.add(user)
    db.session.commit()
