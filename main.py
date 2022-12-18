from __future__ import annotations

# FastAPI
from fastapi import FastAPI, Response, Request, status, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Database
from artcafe.database import supabase, prisma

# import artcafe.dbhandler as db


# Typing
from typing import Dict, Union, Optional
from gotrue.types import Session, User as AuthUser

# Exported Interfaces
from prisma import Prisma
from gotrue.exceptions import APIError
from prisma.models import User, Place
from prisma.enums import Role, Importance
from prisma.errors import PrismaError


app = FastAPI(
    title="ArtCafe API",
    description="REST service for ArtCafe",
    version="0.0.1",
    contact={
        "name": "ArtCafe",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await prisma.connect()


@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()


class LoginModel(BaseModel):
    email: str
    password: str


class SignOnResponse(BaseModel):
    token: str
    user: User


@app.post("/api/login", response_model=SignOnResponse, tags=["Authentication"])
async def login(credentials: LoginModel):
    """
    Login User and return JWT token
    """
    session: Optional[Session] = supabase.auth.sign_in(
        email=credentials.email, password=credentials.password
    )

    if not session or not session.user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Login failed",
        )

    try:
        user = await prisma.user.find_first(
            where={"email": credentials.email}, include={"places": True}
        )
    except PrismaError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Login failed",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Login failed",
        )

    return {"token": session.access_token, "user": user}


class RegisterModel(BaseModel):
    email: str
    password: str
    name: str
    role: Role


@app.post("/api/register", response_model=SignOnResponse, tags=["Authentication"])
async def register(credentials: RegisterModel):
    """
    Register User and return JWT token
    """
    session: Session = supabase.auth.sign_up(
        email=credentials.email, password=credentials.password
    )

    if not session or not session.user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Registration failed",
        )

    try:
        user = await prisma.user.create(
            data={
                "email": credentials.email,
                "name": credentials.name,
                "role": credentials.role,
                "score": 0,
            }
        )
    except PrismaError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Registration failed",
        )

    return {"token": session.access_token, "user": user}


class LogoutResponse(BaseModel):
    message: str


@app.post("/api/logout", response_model=LogoutResponse, tags=["Authentication"])
async def logout():
    """
    Logout User, revoke JWT token
    """
    supabase.auth.sign_out()

    return {"message": "Logout successful"}


@app.get("/api/user/{user_id}", response_model=User, tags=["User"])
async def get_user(user_id: str, token: str):
    """
    Get details of a user by id.
    Requires authentication.
    Only if role is Admin or user_id is the same as the user_id of the authenticated user.
    Get User details
    """

    # Validate token
    try:
        auth_user: AuthUser = supabase.auth.api.get_user(jwt=token)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid JWT token, {e.msg}",
        )

    try:
        user = await prisma.user.find_first(
            where={"id": user_id}, include={"places": True}
        )
        req_user = await prisma.user.find_first(where={"email": auth_user.email or ""})
    except PrismaError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    if not user or not req_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    # Check if user is allowed to access this user
    if (req_user.role != Role.Admin) or (req_user.email != user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied",
        )

    return user


@app.post("/api/places", response_model=Place, tags=["Place"])
async def create_place(
    name: str,
    city: str,
    country: str,
    location: str,
    importance: Importance,
    story: str,
    uri: str,
    token: str,
):
    try:
        auth_user: AuthUser = supabase.auth.api.get_user(jwt=token)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid JWT token {e.msg}",
        )

    try:
        user = await prisma.user.find_first(where={"email": auth_user.email or ""})
    except PrismaError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with email: {auth_user.email=}, got {user=}",
        )

    if not user.role == Role.Admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied",
        )

    try:
        place = await prisma.place.create(
            data={
                "name": name,
                "city": city,
                "country": country,
                "location": location,
                "importance": importance,
                "story": story,
                "uri": uri,
            }
        )

    except PrismaError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not create location",
        )

    return place


@app.get("/")
def root():
    return {
        "message": "Welcome to the ArtCafe API",
        "authors": "Antonino Rossi, Bertold Vincze, David Bobek, Dinu Scripnic",
    }
