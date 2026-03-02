from flask import (
  render_template, redirect, url_for, flash, request, current_app)
from flask_login import (
  current_user, login_user, logout_user, login_required)
from app.errors import (
  LoginError, EmailAlreadyExistsError, UsernameAlreadyExistsError, 
  TokenError, UserNotFoundError, TokenPayloadError)
from . import auth_bp
from .forms import (
  LoginForm, RegisterForm, VerifyUserEmailForm, ChangePasswordForm)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  
  form = LoginForm()
  srv = current_app.user_service
  
  if form.validate_on_submit():
    try:
      user = srv.authenticate(form.email.data, form.password.data)
      login_user(user, remember=form.remember_me.data)
      next = request.args.get('next')
      if next is None or not next.startswith('/'):
        next = url_for('main.index')
      return redirect(next)
    except LoginError as e:
      flash('Username or password are not correct.', category='danger')


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
  srv = current_app.user_service

  if form.validate_on_submit():
    try:
      srv.register_user(
        username=form.username.data, 
        email=form.email.data, 
        password=form.password.data)
      flash(
        'A confirmation email has been sent, please check your email.',
        category='info')
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
  
  srv = current_app.user_service

  try:
    confirmed = srv.confirm_user(current_user, token)
    flash(f'Account confirmed.', category='info')
  except TokenError as e:
    flash('Could not confirm your account.', category='danger')
  
  return redirect(url_for('main.index'))


@auth_bp.route('/confirm')
@login_required
def resend_confirmation():
  if current_user.confirmed:
    return redirect(url_for('main.index'))
  srv = current_app.user_service
  srv.send_confirmation_mail(current_user)
  flash('A new email have been sent, please check your inbox.')

  return redirect(url_for('main.index'))


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  
  form = VerifyUserEmailForm()
  srv = current_app.user_service
  
  if form.validate_on_submit():
    try:
      srv.reset_password_request(email=form.email.data)
    except UserNotFoundError:
      pass
    flash(
      'Please check your inbox for password reset.', 
      category='warning')
    return redirect(url_for('main.index'))
  
  return render_template('auth/reset-password-request.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  
  form = ChangePasswordForm()
  srv = current_app.user_service
  
  if form.validate_on_submit():
    try:
      srv.reset_password(token, form.password.data)
      flash('Password has been reset, you can login now.')
      return redirect(url_for('auth.login'))
    except TokenPayloadError:
      flash('Invalid Token', category='danger')
  
  return render_template('auth/change-password.html', form=form)
