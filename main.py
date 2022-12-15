from __future__ import annotations
from prisma_def import Prisma
from prisma_def.enums import Role
from fastapi import FastAPI, Response, Request, status, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from artcafe.authentication import *
import artcafe.dbhandler as db
from typing import Dict
from pydantic import BaseModel


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


class LoginModel(BaseModel):
    email: str
    password: str


@app.post("/api/login", tags=["Authentication"])
async def login(credentials: LoginModel):
    """
    Login User and return JWT token
    """
    token = await db.login_user(credentials.email, credentials.password)
    return {"token": token}


# create RegisterModel from Prisma user model
class RegisterModel(BaseModel):
    email: str
    password: str
    name: str
    role: Role


@app.post("/api/register", tags=["Authentication"])
async def register(credentials: RegisterModel):
    """
    Register User and return JWT token
    """
    token = await db.register_user(
        credentials.email, credentials.password, credentials.name, credentials.role
    )
    return {"Result": token}


class LogoutModel(BaseModel):
    id: str
    token: str


@app.post("/api/logout", tags=["Authentication"])
async def logout() -> Dict[str, str]:
    """
    Logout User, revoke JWT token
    Logout User, revoke JWT token
    """
    # implement logout in future
    valid = False
    if valid:
        return {"message": "Logout successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Logout failed",
        )


class UserInfoModel(BaseModel):
    id: str
    email: str
    name: str
    role: str
    places: list


@app.get("/api/user/{user_id}", tags=["User"])
async def get_user():
    """
    Get details of a user by id. Requires authentication. Only if role is Admin or user_id is the same as the user_id of the authenticated user.
    Get User details
    """
    # implement this in future
    valid = False
    if valid:
        return {"message": "User details"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Logout failed",
        )


@app.get("/hello")
def hello_world():
    return {"message": "Hello World"}
