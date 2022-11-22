from __future__ import annotations
from prisma import Prisma
from prisma.models import User,Place,Object3D
from prisma.enums import Role,Importance
from database import client
from fastapi import HTTPException, status
from authentication import create_jwt_token


# User Database functions


async def login_user(email: str, password: str) -> str:
    """
    Login User and return JWT token
    """
    # authenticate with supabase
    # if user is not authenticated raise exception
    # create token and return it
    pass


async def register_user(email: str, password: str, name: str, role: Role) -> str:
    """
    Register User and return JWT token
    """
    # sign up user with supabase
    # if user is not authenticated raise exception
    # create User in database with prisma (you get the user_id from supabase)
    # create token and return it
    pass


async def logout_user(id: str, token: str) -> None:
    """
    Logout User, revoke JWT token
    """
    # revoke token in supabase
    pass


async def get_user(user_id: str) -> User:
    """
    Get User details
    """
    # get user from database
    # return user
    pass


async def get_users(condition: dict = {}) -> list[User]:
    """
    Get all Users
    """
    # get users from database
    # return users
    pass


async def delete_user(user_id: str) -> None:
    """
    Delete User
    """
    # delete user from supabase
    # delete user from database
    pass


async def update_user(user_id: str, email:str, password:str, name: str, role: Role) -> User:
    """
    Update User
    """
    # update user in supabase
    # update user in database
    # return user
    pass


# Place Database functions


async def create_place(name:str,importance:str,story:str,uri:str,User:User | None, userId:str|None)-> Place:
    """
    Create Place
    """
    # create place in database
    # return place
    pass


async def modify_place(place_id:str,name:str,importance:str,story:str,uri:str,User:User | None, userId:str|None)-> Place:
    """
    Modify Place
    """
    # modify place in database
    # return place
    pass


async def delete_place(place_id:str)-> None:
    """
    Delete Place
    """
    # delete place in database
    pass


async def get_place(place_id:str)-> Place:
    """
    Get Place
    """
    # get place from database
    # return place
    pass


async def get_places(condition: dict = {}) -> list[Place]:
    """
    Get all Places
    """
    # get places from database
    # return places
    pass


# Object3d Database functions


async def create_object3d(location:Place,placeId:str,img_url:str) -> Object3D:
    """
    Create Object3D
    """
    # create object3d in database
    # return object3d
    pass


async def modify_object3d(object3d_id:str,location:Place,placeId:str,img_url:str) -> Object3D:
    """
    Modify Object3D
    """
    # modify object3d in database
    # return object3d
    pass


async def delete_object3d(object3d_id:str) -> None:
    """
    Delete Object3D
    """
    # delete object3d in database
    pass


async def get_object3d(object3d_id:str) -> Object3D:
    """
    Get Object3D
    """
    # get object3d from database
    # return object3d
    pass


async def get_object3ds(condition: dict = {}) -> list[Object3D]:
    """
    Get all Object3Ds
    """
    # get object3ds from database
    # return object3ds
    pass


