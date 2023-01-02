from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

import wishlist.exceptions as exceptions
from wishlist.config import settings


def create_access_token(data: dict, expiration: int = settings.jwt.expiration_minutes):
    data = data.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expiration)
    return jwt.encode(data, settings.jwt.secret_key, settings.jwt.algorithm)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, settings.jwt.secret_key, settings.jwt.algorithm)
    except JWTError as exc:
        raise exceptions.AUTHORIZATION_EXCEPTION from exc
