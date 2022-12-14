###
# Methods for authenticating users
###
from fastapi import Response, Request
from dotenv import load_dotenv

load_dotenv()


async def authenticate_user(request: Request, response: Response) -> None:
    """
    Authenticate user with JWT token
    """
    # get jwt token from header
    # split it to get the token
    # check if token is valid in supabase
    # if token is not valid raise exception
    # if token is valid return user_id
    pass


async def create_jwt_token(id, email, password) -> str:
    """
    Create JWT token for user
    """
    # create token with jwt
    # return token
    pass
