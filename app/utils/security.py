import jwt
from jwt.exceptions import (
  ExpiredSignatureError, InvalidSignatureError, DecodeError, InvalidTokenError)
from flask import current_app
from app.errors import (
  TokenError, TokenInvalidSignatureError, TokenExpiredError, TokenMalformedError)

def generate_timed_token(payload: dict, expiration: int=3600) -> str:
  """
  token default expires in 1 hour
  """
  _payload = payload.copy()
  _payload.update({'exp': expiration})
  return jwt.encode(_payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def decode_timed_token(token: str) -> dict:
  """:return: decoded payload else return error message"""
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
