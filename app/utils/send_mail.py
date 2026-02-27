from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app.ext import mail

def _send_async_mail(app, msg: str):
  with app.app_context():
    mail.send(msg)


def send_mail(to: str, subject: str, template: str, **kwargs):
  """
  :param to: the recipient, user's email account
  :param subject: email subject
  :param template: email template without file extension, should have 2 versions
  ".txt" and ".html"
  """
  msg = Message(
    current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
    sender=current_app.config['MAIL_SENDER'],
    recipients=[to])
  msg.body = render_template(template + '.txt', **kwargs)
  msg.html = render_template(template + '.html', **kwargs)

  thr = Thread(
    target=_send_async_mail, 
    args=[current_app._get_current_object(), msg])
  thr.start()
