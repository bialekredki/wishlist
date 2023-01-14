import re
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

import wishlist.exceptions as exceptions
from wishlist.config import settings

PASSWORD_STRENGTH_PATTERN = (
    r"^(?=(.*[a-z]){3,})(?=(.*[A-Z]){2,})(?=(.*[0-9]){2,})(?=.*[!@#$%^&*.,?/><\"\';:])"
)


def create_access_token(data: dict, expiration: int = settings.jwt.expiration_minutes):
    data = data.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expiration)
    return jwt.encode(data, settings.jwt.secret_key, settings.jwt.algorithm)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, settings.jwt.secret_key, settings.jwt.algorithm)
    except JWTError as exc:
        raise exceptions.AUTHORIZATION_EXCEPTION from exc


def is_password_safe(password: str) -> bool:
    if not re.match(PASSWORD_STRENGTH_PATTERN, password):
        return False
    digits_sequence = []
    for character in password:
        if re.match(r"[0-9]", character):
            digits_sequence.append(int(character))
            if (
                len(digits_sequence) > 2
                and digits_sequence[-1] - digits_sequence[-2] == 1
                and digits_sequence[-2] - digits_sequence[-3] == 1
            ):
                return False
        else:
            digits_sequence = []
    return True
