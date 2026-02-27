class AuthError(Exception):
  """Base class for authentication errors."""
  def __init__(self, message='Authentication failed', status_code=401):
    super().__init__(message)
    self.status_code = status_code


class LoginError(AuthError):
  """Base class for user login errors."""
  pass


class UserNotFoundError(LoginError): pass

class PasswordValidationError(LoginError): pass


class RegistrationError(AuthError):
  """Base class for user registration errors."""
  def __init__(self, message='Registration Failed', status_code=409):
    super().__init__(message, status_code)


class EmailAlreadyExistsError(RegistrationError): pass

class UsernameAlreadyExistsError(RegistrationError): pass


class TokenError(AuthError):
  """Base class for all token related errors."""
  def __init__(self, message='Invalid Token', status_code=401):
    super().__init__(message, status_code)


class TokenExpiredError(TokenError):
  def __init__(self, message='Token Expired'):
    super().__init__(message)

class TokenInvalidSignatureError(TokenError):
  def __init__(self, message='Invalid Signature Error'):
    super().__init__(message)

class TokenMalformedError(TokenError):
  def __init__(self, message='Malformed Token'):
    super().__init__(message)

class TokenPayloadError(TokenError):
  def __init__(self, message='Payload does not match the context'):
    super().__init__(self, message)

