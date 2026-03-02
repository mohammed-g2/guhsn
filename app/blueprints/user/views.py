from flask import (
  render_template, redirect, url_for, flash, request, current_app)
from flask_login import current_user, login_required
from app.errors import (
  EmailAlreadyExistsError, UsernameAlreadyExistsError, 
  TokenError, PasswordValidationError)
from . import user_bp
from .forms import (
  ChangePasswordForm, UpdateUserProfileForm, UpdateEmailForm,
  VerifyUserPasswordForm)


def profile_form_handler(form):
  if form.validate_on_submit():
    srv = current_app.user_service
    user = current_user._get_current_object()
    try:
      srv.update_profile(user=user, username=form.username.data)
      flash('User profile updated.', category='info')
      return redirect(url_for('user.settings'))
    except UsernameAlreadyExistsError:
      form.username.errors.append('Username already in use.')


def email_form_handler(form):
  if form.validate_on_submit():
    srv = current_app.user_service
    user = current_user._get_current_object()
    try:
      srv.update_email_request(user=user, new_email=form.email.data)
      flash(
        'An email have been sent, please check you inbox.', 
        category='info')
      return redirect(url_for('user.settings'))
    except EmailAlreadyExistsError:
      form.email.errors.append(
        'This email is already associated with an account.')


def password_form_handler(form):
  if form.validate_on_submit():
    srv = current_app.user_service
    user = current_user._get_current_object()
    try:
      srv.password_change_request(
        user=user, password=form.password.data)
      flash(
        'An email have been sent, please check you inbox.',
        category='info')
      return redirect(url_for('user.settings'))
    except PasswordValidationError:
      flash('Incorrect Password.')


@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
  profile_form = UpdateUserProfileForm()
  email_form = UpdateEmailForm()
  password_form = VerifyUserPasswordForm()
  
  if request.method == 'POST':
    if profile_form.submit_profile.data:
      profile_form_handler(profile_form)
    elif email_form.submit_email.data:
      email_form_handler(email_form)
    elif password_form.submit_password.data:
      password_form_handler(password_form)
    return redirect(url_for('user.settings'))
  
  return render_template(
    'user/settings.html',
    profile_form=profile_form,
    email_form=email_form,
    password_form=password_form)


@user_bp.route('/update-user-email/<token>')
@login_required
def update_user_email(token):
  user = current_user._get_current_object()
  srv = current_app.user_service
  
  try:
    srv.update_email(user, token)
    flash('Email address updated.', category='info')
  except TokenError as e:
    flash(e, category='danger')
  
  return redirect(url_for('user.settings'))


@user_bp.route('/change-user-password/<token>', methods=['GET', 'POST'])
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
    return redirect(url_for('user.settings'))
  
  return render_template('user/change-password.html', form=form)
