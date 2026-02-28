from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
  email = EmailField('Email', validators=[DataRequired(), Length(max=64), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember_me = BooleanField('keep me logged in')
  submit = SubmitField('Login')


class RegisterForm(FlaskForm):
  email = EmailField('Email', validators=[DataRequired(), Length(max=64), Email()])
  username = StringField('Username', validators=[
    DataRequired(), Length(3, 36),
    Regexp(
      '^[A-Za-z][A-Za-z0-9_.]*$', 0, 
      'Username must have only letters, numbers, dots or underscores.')])
  password = PasswordField('Password', validators=[
    DataRequired(), Length(min=6), 
    EqualTo('password2', message='Password must match.')])
  password2 = PasswordField('Confirm password', validators=[DataRequired()])
  terms = BooleanField('I agree on terms and services', validators=[DataRequired()])
  submit = SubmitField('Sign Up')


class ChangePasswordForm(FlaskForm):
  password = PasswordField('New Password', validators=[
    DataRequired(), Length(min=6), 
    EqualTo('password2', message='Password must match.')])
  password2 = PasswordField('Confirm password', validators=[DataRequired()])
  submit = SubmitField('Change Password')


# settings page forms

class UpdateUserProfileForm(FlaskForm):
  username = StringField('Update Username', validators=[
    DataRequired(), Length(3, 36),
    Regexp(
      '^[A-Za-z][A-Za-z0-9_.]*$', 0, 
      'Username must have only letters, numbers, dots or underscores.')])
  submit_profile = SubmitField('Update')


class UpdateUserEmailForm(FlaskForm):
  email = EmailField('Update Email', validators=[DataRequired(), Length(max=64), Email()])
  submit_email = SubmitField('Update')


class VerifyUserPasswordForm(FlaskForm):
  password = PasswordField('Current Password', validators=[DataRequired(), Length(min=6)])
  submit_password = SubmitField('Submit')
