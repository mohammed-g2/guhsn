from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app.errors import (
  LoginError, EmailAlreadyExistsError, UsernameAlreadyExistsError, 
  TokenError, UserNotFoundError, PasswordValidationError)
from . import auth_bp
from .forms import (
  LoginForm, RegisterForm, UpdateUserProfileForm, UpdateUserEmailForm,
  VerifyUserPasswordForm, ChangePasswordForm)


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
  srv = current_app.user_service

  if form.validate_on_submit():
    try:
      srv.register_user(
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


def profile_form_handler(form):
  if form.validate_on_submit():
    srv = current_app.user_service
    user = current_user._get_current_object()
    try:
      srv.update_profile(user=user, username=form.username.data)
      flash('User profile updated.', category='info')
      return redirect(url_for('auth.settings'))
    except UsernameAlreadyExistsError:
      form.username.errors.append('Username already in use.')


def email_form_handler(form):
  if form.validate_on_submit():
    srv = current_app.user_service
    user = current_user._get_current_object()
    try:
      srv.update_email_request(user=user, email=form.email.data)
      flash('An email have been sent, please check you inbox.', category='info')
      return redirect(url_for('auth.settings'))
    except EmailAlreadyExistsError:
      form.email.errors.append('This email is already associated with an account.')


def password_form_handler(form):
  if form.validate_on_submit():
    srv = current_app.user_service
    user = current_user._get_current_object()
    try:
      srv.password_change_request(user=user, password=form.password.data)
      flash('An email have been sent, please check you inbox.', category='info')
      return redirect(url_for('auth.settings'))
    except PasswordValidationError:
      form.password.errors.append('Incorrect Password.')


@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
  profile_form = UpdateUserProfileForm()
  email_form = UpdateUserEmailForm()
  password_form = VerifyUserPasswordForm()
  
  if request.method == 'POST':
    if profile_form.submit_profile.data:
      profile_form_handler(profile_form)
    elif email_form.submit_email.data:
      email_form_handler(email_form)
    elif password_form.submit_password.data:
      password_form_handler(password_form)
      
  return render_template(
    'auth/settings.html',
    profile_form=profile_form,
    email_form=email_form,
    password_form=password_form)


@auth_bp.route('/update-user-email/<token>')
@login_required
def update_user_email(token):
  user = current_user._get_current_object()
  srv = current_app.user_service
  
  try:
    srv.update_email(user, token)
    flash('Email address updated.', category='info')
  except TokenError as e:
    flash(e, category='danger')
  
  return redirect(url_for('auth.settings'))


@auth_bp.route('/change-user-password/<token>', methods=['GET', 'POST'])
@login_required
def change_password(token):
  user = current_user._get_current_object()
  srv = current_app.user_service
  form = ChangePasswordForm()
  
  if form.validate_on_submit():
    try:
      srv.change_password(
        user=user, token=token, password=form.password.data)
      flash('Password changed.')
    except TokenError as e:
      flash(e, category='danger')
    return redirect(url_for('auth.settings'))
  
  return render_template('auth/change-password.html', form=form)


@auth_bp.route('/reset-password/<token>')
def reset_password(token):
  pass
