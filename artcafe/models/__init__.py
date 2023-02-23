from fastapi import FastAPI, HTTPException, status as HTTPStatus
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from gotrue.types import (
    AuthResponse,
    User as AuthUser,
    SignInWithEmailAndPasswordCredentials as SignInData,
    SignUpWithEmailAndPasswordCredentials as SignUpData,
)
from gotrue.errors import AuthError

from prisma.types import UserUpdateInput, UserCreateWithoutRelationsInput
from prisma.models import User
from prisma.enums import Role, Importance, Gender
from prisma.errors import PrismaError, MissingRequiredValueError

from typing import TypedDict


class SignOnResponse(BaseModel):
    token: str


class Credentials(BaseModel):
    email: str
    password: str

    def into_signin(self) -> SignInData:
        return {"email": self.email, "password": self.password}

    def into_signup(self) -> SignUpData:
        return {"email": self.email, "password": self.password}


class UserCreateModel(TypedDict):
    name: str
    surname: str
    username: str
    role: Role
    gender: Gender
    location: str


class RegisterModel(BaseModel):
    user_data: UserCreateModel
    credentials: Credentials


class LogoutResponse(BaseModel):
    message: str


class PlaceCreateInput(BaseModel):
    name: str
    city: str
    country: str
    geolocation: str
    importance: Importance
    uri: str
    story: str


__all__ = [
    "FastAPI",
    "HTTPException",
    "HTTPStatus",
    "BaseModel",
    "AuthUser",
    "AuthError",
    "User",
    "Role",
    "Importance",
    "PrismaError",
    "CORSMiddleware",
    "SignOnResponse",
    "RegisterModel",
    "LogoutResponse",
    "UserUpdateInput",
    "PlaceCreateInput",
    "MissingRequiredValueError",
    "UserCreateWithoutRelationsInput",
    "Gender",
    "Credentials",
    "AuthResponse",
]
