class AppError(Exception):
    status_code = 500
    detail = "Internal server error"


class EmailAlreadyExists(AppError):
    status_code = 409
    detail = "Email already registered."


class InvalidCredentials(AppError):
    status_code = 401
    detail = "Invalid email or password."


class InactiveUser(AppError):
    status_code = 403
    detail = "User is inactive."


class InvalidToken(AppError):
    status_code = 401
    detail = "Invalid token."


class InvalidTokenType(AppError):
    status_code = 401
    detail = "Invalid token type"


class TokenExpired(AppError):
    status_code = 401
    detail = "Token has expired."


class TokenReuseDetected(AppError):
    status_code = 401
    detail = "Token reuse detected! All sessions revoked for security reasons."


class UserNotFoundOrInactive(AppError):
    status_code = 401
    detail = "User not found or inactive."