from fastapi import FastAPI, Response, Request, status, HTTPException
from authentication import *
from dbhandler import *
from fastapi.openapi.utils import get_openapi
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


class LoginModel(BaseModel):
    email: str
    password: str


@app.post("/api/login", tags=["Authentication"])
async def login(Credentials: LoginModel):
    """
    Login User and return JWT token
    """
    # implement login in future
    valid = False
    if valid:
        return {"message": "Login successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid credentials",
        )


# create RegisterModel from Prisma user model
class RegisterModel(BaseModel):
    email: str
    password: str
    name: str
    role: str


@app.post("/api/register", tags=["Authentication"])
async def register(User: RegisterModel):
    """
    Register User and return JWT token
    """
    # implement register in future
    valid = False
    if valid:
        return {"message": "Register successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Register failed",
        )


class LogoutModel(BaseModel):
    id: str
    token: str


@app.post("/api/logout", tags=["Authentication"])
async def logout():
    """
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


@app.get("/api/user/{user_id}", tags=["User"], response_model=UserInfoModel)
async def get_user(user_id: int):
    """
    Get details of a user by id. Requires authentication. Only if role is Admin or user_id is the same as the user_id of the authenticated user.
    """
    # get userid from token
    # check if user is admin or user_id is the same as the user_id of the authenticated user
    # if yes, return user info
    # else, return 403
    muster = UserInfoModel(
        id=user_id, email="asd@gmail.com", name="asd", role="Admin", places=[]
    )
    return muster
