from fastapi import FastAPI, HTTPException, status as HTTPStatus
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from gotrue.types import Session, User as AuthUser
from gotrue.exceptions import APIError

from prisma.types import PlaceUpdateInput, UserUpdateInput, PlaceOrderByInput
from prisma.models import User, Place
from prisma.enums import Role, Importance
from prisma.errors import PrismaError


class LoginModel(BaseModel):
    email: str
    password: str


class SignOnResponse(BaseModel):
    token: str


class RegisterModel(BaseModel):
    email: str
    password: str
    name: str
    role: Role


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
    "Session",
    "AuthUser",
    "APIError",
    "User",
    "Place",
    "Role",
    "Importance",
    "PrismaError",
    "CORSMiddleware",
    "LoginModel",
    "SignOnResponse",
    "RegisterModel",
    "LogoutResponse",
    "PlaceUpdateInput",
    "UserUpdateInput",
    "PlaceCreateInput",
]
