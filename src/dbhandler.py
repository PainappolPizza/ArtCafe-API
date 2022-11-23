from __future__ import annotations


from prisma import Prisma
from prisma.models import User, Place, Object3D
from prisma.enums import Role, Importance
from database import client
from fastapi import HTTPException, status
from authentication import create_jwt_token
import os
import uuid


# User Database functions
async def create_prisma() -> Prisma:
    """
    Create Prisma Client
    """
    prisma = Prisma()
    await prisma.connect()
    return prisma


async def login_user(email: str, password: str, prisma: Prisma = global_prisma) -> str:
    """
    Login User and return JWT token
    """
    # authenticate with supabase
    # if user is not authenticated raise exception
    # create token and return it
    pass


async def register_user(
    email: str, password: str, name: str, role: Role, prisma: Prisma = global_prisma
) -> str:
    """
    Register User and return JWT token
    """
    # sign up user with supabase
    # if user is not authenticated raise exception
    # create User in database with prisma (you get the user_id from supabase)
    # create token and return it
    pass


async def logout_user(id: str, token: str, prisma: Prisma = global_prisma) -> None:
    """
    Logout User, revoke JWT token
    """
    # revoke token in supabase
    pass


async def get_user(user_id: str, prisma: Prisma = global_prisma) -> User:
    """
    Get User details
    """
    # get user from database
    # return user
    pass


async def get_users(condition: dict = {}, prisma: Prisma = global_prisma) -> list[User]:
    """
    Get all Users
    """
    # get users from database
    # return users
    pass


async def delete_user(user_id: str, prisma: Prisma = global_prisma) -> None:
    """
    Delete User
    """
    # delete user from supabase
    # delete user from database
    pass


async def update_user(
    user_id: str,
    email: str,
    password: str,
    name: str,
    role: Role,
    prisma: Prisma = global_prisma,
) -> User:
    """
    Update User
    """
    # update user in supabase
    # update user in database
    # return user
    pass


# Place Database functions


async def create_place(
    name: str,
    importance: str,
    story: str,
    uri: str,
    User: User | None,
    userId: str | None,
    prisma: Prisma = global_prisma,
) -> Place:
    """
    Create Place
    """
    # create place in database
    # return place
    pass


async def modify_place(
    place_id: str,
    name: str,
    importance: str,
    story: str,
    uri: str,
    User: User | None,
    userId: str | None,
    prisma: Prisma = global_prisma,
) -> Place:
    """
    Modify Place
    """
    # modify place in database
    # return place
    pass


async def delete_place(place_id: str, prisma: Prisma = global_prisma) -> None:
    """
    Delete Place
    """
    # delete place in database
    pass


async def get_place(place_id: str, prisma: Prisma = global_prisma) -> Place:
    """
    Get Place
    """
    # get place from database
    # return place
    pass


async def get_places(
    condition: dict = {}, prisma: Prisma = global_prisma
) -> list[Place]:
    """
    Get all Places
    """
    # get places from database
    # return places
    pass


# Object3d Database functions


def get_bytes_from_url(img_path: str) -> bytes:
    # get image from /scenes folder
    img_path = os.path.join(os.getcwd(), "scenes", img_path)
    with open(img_path, "rb") as f:
        img_bytes = f.read()
    return img_bytes


def get_img_from_bytes(img_bytes: bytes) -> str:
    with open("test.avif", "wb") as f:
        f.write(img_bytes)


async def create_object3d(
    location: Place, placeId: str, img_url: str, prisma: Prisma = global_prisma
) -> Object3D:
    """
    Create Object3D and return it
    param: location: Place
    param: placeId: str
    param: img_url: str
    """
    # create bytes from img_url
    img_bytes = get_bytes_from_url(img_url)
    # create uuid for object3d
    object3d_id = str(uuid.uuid4())

    # create Object3D type
    obj3d = Object3D(id=object3d_id, location=location, placeId=placeId, img=img_bytes)
    # create object3d in database
    response = await prisma.object3d.create(data=obj3d.dict())
    # if object3d is not created raise exception
    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Object3D could not be created",
        )

    return obj3d


async def modify_object3d(
    object3d_id: str,
    location: Place,
    placeId: str,
    img_url: str,
    prisma: Prisma = global_prisma,
) -> Object3D:
    """
    Modify Object3D
    params: object3d_id: str
    params: location: Place
    params: placeId: str
    params: img_url: str
    """
    obj3d = await prisma.object3d.find_unique(where={"id": object3d_id})
    if not obj3d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Object3D not found"
        )
    # update object3d in database
    update = await prisma.object3d.update(
        where={"id": object3d_id},
        data={
            "location": location,
            "placeId": placeId,
            "img": get_bytes_from_url(img_url),
        },
    )
    # if object3d is not updated raise exception
    if not update:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Object3D could not be updated",
        )
    return obj3d


async def delete_object3d(object3d_id: str, prisma: Prisma = global_prisma) -> None:
    """
    Delete Object3D
    params: object3d_id: str
    """
    # delete object3d from database
    delete = await prisma.object3d.delete(where={"id": object3d_id})
    # if object3d is not deleted raise exception
    if not delete:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Object3D could not be deleted",
        )
    return "OBJECT3D_DELETED"


async def get_object3d(object3d_id: str, prisma: Prisma = global_prisma) -> Object3D:
    """
    Get Object3D
    params: object3d_id: str
    """
    # get object3d from database
    obj3d = await prisma.object3d.find_unique(where={"id": object3d_id})
    # if object3d is not found raise exception
    if not obj3d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Object3D not found"
        )
    return obj3d


async def get_object3ds(
    condition: dict = {}, prisma: Prisma = global_prisma
) -> list[Object3D]:
    """
    Get all Object3Ds
    params: condition: dict
    """
    # get object3ds from database
    obj3ds = await prisma.object3d.find_many(where=condition)
    if not obj3ds:
        return []
    return obj3ds
