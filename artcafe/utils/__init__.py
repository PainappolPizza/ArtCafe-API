from __future__ import annotations


import jwt
import os

from fastapi import HTTPException, status as HTTPStatus
from gotrue.errors import AuthError
from ..models import AuthResponse, SignInData, SignUpData, SignOnResponse

from prisma import Prisma
from prisma.errors import PrismaError
from prisma.models import User
from supabase.client import Client

from result import Ok, Err, Result
from dotenv import load_dotenv

from typing import Callable, Coroutine, Any, TypeVar

load_dotenv()

secret = os.environ.get("SECRET")

if not secret:
    raise ValueError("Missing environment variables")


class AuthFailed(Exception):
    ...


CT = TypeVar("CT", SignUpData, SignInData)


async def validate_user(
    *,
    credentials: CT,
    authenticate: Callable[[CT], AuthResponse],
    query: Callable[[], Coroutine[Any, Any, User | None]],
    predicate: Callable[[User], bool] | None = None,
) -> Result[tuple[str, User], AuthFailed]:
    try:
        response = authenticate(credentials)

        if not response.user or not response.user.email or not response.session:
            return Err(AuthFailed(f"User not found"))

        user = await query()

        if not user:
            return Err(AuthFailed(f"User not found"))

        if predicate and not predicate(user):
            return Err(AuthFailed("User not allowed"))

        return Ok((response.session.access_token, user))

    except Exception as e:
        return Err(AuthFailed(f"Unable to authenticate. Reason: {e!r}"))


def handle_result(result: Result[tuple[str, User], AuthFailed], /) -> SignOnResponse:
    match result:
        case Ok((token, user)):
            token = add_user(token, user)
            return SignOnResponse(token=token)
        case Err(e):
            raise HTTPException(
                status_code=HTTPStatus.HTTP_403_FORBIDDEN,
                detail=f"Login failed, {e!r}",
            )


def add_user(token: str, user: User) -> str:
    decoded = jwt.decode(
        token, options={"verify_signature": False}, algorithms=["HS256"]
    )
    decoded["user"] = user.dict(exclude={"joined"})
    return jwt.encode(decoded, secret)


def remove_user(token: str) -> str:
    decoded = jwt.decode(
        token, options={"verify_signature": False}, algorithms=["HS256"]
    )
    del decoded["user"]
    return jwt.encode(decoded, secret)


async def user_from(*, token: str, supabase: Client, prisma: Prisma) -> User:
    try:
        token = remove_user(token)
        user_response = supabase.auth.get_user(jwt=token)
    except AuthError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Invalid JWT token, {e!r}",
        )

    if not user_response.user or not user_response.user.email:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Invalid JWT token, {user_response!r}",
        )

    try:
        user = await prisma.user.find_first(where={"email": user_response.user.email})
    except PrismaError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found, no such email {user_response.user.email}",
        )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found, no such user",
        )

    return user
