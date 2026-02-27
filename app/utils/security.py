from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import (
  ExpiredSignatureError, InvalidSignatureError, DecodeError, InvalidTokenError)
from flask import current_app
from app.errors import (
  TokenError, TokenInvalidSignatureError, TokenExpiredError, TokenMalformedError)

def generate_timed_token(payload: dict, expiration: int=3600) -> str:
  """
  token default expires in 1 hour
  
  :returns: encoded token
  """
  _payload = payload.copy()
  _payload.update({
    'iat': datetime.now(timezone.utc), # Issued At
    'nbf': datetime.now(timezone.utc), # Not Before Time
    'exp': datetime.now(timezone.utc) + timedelta(seconds=expiration)
  })
  return jwt.encode(_payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def decode_timed_token(token: str) -> dict:
  """
  :returns: decoded payload
  :raises TokenExpiredError: raised when token is expired
  :raises TokenInvalidSignatureError: raised when token is tampered with
  :raises TokenMalformedError: raised when token is malformed or incomplete
  :raises TokenError: raised for any other error
  """
  try:
    return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
  except ExpiredSignatureError:
    raise TokenExpiredError()
  except InvalidSignatureError:
    raise TokenInvalidSignatureError()
  except DecodeError:
    raise TokenMalformedError()
  except InvalidTokenError as e:
    raise TokenError(message=e)
  except Exception as e:
    raise TokenError(message=e)
