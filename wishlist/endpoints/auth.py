import json

import bcrypt
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import wishlist.exceptions as exceptions
import wishlist.query as dbquery
from wishlist.database import get_client
from wishlist.schemas.token import Token
from wishlist.security import create_access_token, decode_access_token

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(
    client=Depends(get_client), token: str = Depends(oauth2_scheme)
):
    decoded_token = decode_access_token(token)
    try:
        print(decoded_token["sub"])
        sub = json.loads(decoded_token["sub"])
        return (await dbquery.get_user_by_slug(client, slug=sub["slug"]))[0]
    except (KeyError, IndexError) as exc:
        raise exceptions.AUTHORIZATION_EXCEPTION from exc


@router.post(
    "/token",
    response_model=Token,
    responses=exceptions.exceptions_to_mapping(
        (exceptions.not_found_exception_factory, exceptions.AUTHORIZATION_EXCEPTION)
    ),
)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    client=Depends(get_client),
):
    user = await dbquery.get_user_credentials(client, email=form_data.username)
    if not user:
        raise exceptions.not_found_exception_factory(form_data.username)
    if not bcrypt.checkpw(
        form_data.password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        raise exceptions.AUTHORIZATION_EXCEPTION
    return Token(
        access_token=create_access_token(
            {"sub": json.dumps({"slug": user.slug, "id": str(user.id)})}
        ),
        token_type="bearer",
    )
