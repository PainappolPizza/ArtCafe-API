from __future__ import annotations


import jwt
import os

from fastapi import HTTPException, status as HTTPStatus
from gotrue.errors import AuthError

from prisma import Prisma
from prisma.errors import PrismaError
from prisma.models import User
from supabase.client import Client

from dotenv import load_dotenv

load_dotenv()

secret = os.environ.get("SECRET")

if not secret:
    raise ValueError("Missing environment variables")


def add_user(token: str, user: User) -> str:
    decoded = jwt.decode(
        token, options={"verify_signature": False}, algorithms=["HS256"]
    )
    user.createdAt = user.createdAt.isoformat()
    decoded["user"] = user.dict()
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
        auth_user = supabase.auth.api.get_user(jwt=token)
    except AuthError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Invalid JWT token, {e.msg}",
        )

    try:
        user = await prisma.user.find_first(where={"email": auth_user.email})
    except PrismaError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found, no such email {auth_user.email}",
        )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found, no such user",
        )

    return user
