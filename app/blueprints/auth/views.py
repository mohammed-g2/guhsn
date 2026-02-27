from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app.errors import (
  LoginError, EmailAlreadyExistsError, UsernameAlreadyExistsError, 
  TokenError, UserNotFoundError, PasswordValidationError)
from . import auth_bp
from .forms import LoginForm, RegisterForm


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  
  form = LoginForm()
  svr = current_app.user_service
  
  if form.validate_on_submit():
    try:
      user = svr.authenticate(form.email.data, form.password.data)
      login_user(user, remember=form.remember_me.data)
      next = request.args.get('next')
      if next is None or not next.startswith('/'):
        next = url_for('main.index')
      return redirect(next)
    except LoginError as e:
      flash('Username or password are not correct.', category='danger')
      if isinstance(e, UserNotFoundError):
        pass
      elif isinstance(e, PasswordValidationError):
        pass
    

  return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  
  form = RegisterForm()
  svr = current_app.user_service

  if form.validate_on_submit():
    try:
      svr.register_user(
        username=form.username.data, 
        email=form.email.data, 
        password=form.password.data)
      flash('A confirmation email has been sent, please check your email.', category='info')
      flash('You can login now.', category='info')
      return redirect(url_for('auth.login'))
    except EmailAlreadyExistsError:
      form.email.errors.append('Email already registered.')
    except UsernameAlreadyExistsError:
      form.username.errors.append('Username already in use.')
    
  return render_template('auth/register.html', form=form)


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
  if current_user.confirmed:
    return redirect(url_for('main.index'))
  
  svr = current_app.user_service

  try:
    confirmed = svr.confirm_user(current_user, token)
    flash(f'Account confirmed.', category='info')
  except TokenError as e:
    flash('Could not confirm your account.', category='danger')
  
  return redirect(url_for('main.index'))


@auth_bp.route('/confirm')
@login_required
def resend_confirmation():
  if current_user.confirmed:
    return redirect(url_for('main.index'))
  svr = current_app.user_service
  svr.send_confirmation_mail(current_user)
  flash('A new email have been sent, please check your inbox.')

  return redirect(url_for('main.index'))


@auth_bp.route('/settings')
@login_required
def settings():
  return render_template('auth/settings.html')


@auth_bp.route('/update-user-data', methods=['POST'])
@login_required
def update_user_data():
  pass


@auth_bp.route('/update-user-email', methods=['POST'])
@login_required
def update_user_email():
  pass


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
  pass


@auth_bp.route('/reset-password/<token>')
def reset_password(token):
  pass
