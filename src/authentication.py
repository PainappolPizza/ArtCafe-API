###
# Methods for authenticating users
###
import jwt
from fastapi import FastAPI, Response, Request, status, HTTPException, Header
import supabase
from dotenv import load_dotenv
import os

load_dotenv()

async def authenticate_user(request: Request, response: Response) -> None:
    """
    Authenticate user and return JWT token
    """
    # get jwt token from header
    token:str | None = request.headers.get("Authorization")
    # split it to get the token
    token = token.split(" ")[1]
    # decode token
    try:
        decoded_token = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials",
        )

    user_id = decoded_token.get("user_id")
    user_id:str = decoded_token["user_id"]
    user_email:str = decoded_token["email"]
    user_password:str = decoded_token["password"]
    if not user_id or not user_email or not user_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials",
        )

    # login user to supabase
    supabase.auth.sign_in(email=user_email, password=user_password)
    # if user is not authenticated raise exception
    if not supabase.auth.user():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials",
        )
    # add user_id to request
    request.state.user_id = user_id
    

async def create_jwt_token(id,email, password)-> str:
    """
    Create JWT token for user
    """
    # create token
    token:str = jwt.encode({"user_id":id,"email":email,"password":password},key=os.getenv("JWT_SECRET"),algorithm="HS256")
    # return token
    return token