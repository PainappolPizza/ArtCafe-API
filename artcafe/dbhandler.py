from __future__ import annotations

from typing import Final
from _prisma import Prisma, Base64
from _prisma.models import User, Place, Object3D
from _prisma.enums import Role, Importance
from _prisma.types import PlaceWhereInput, Object3DWhereInput, PlaceCreateInput

# from database import client
from fastapi import HTTPException, status

# from authentication import create_jwt_token
import os
import uuid

from .database.client import global_clients, Clients


EMPTY_DICT: Final[dict] = {}


async def login_user(
    email: str, password: str, clients: Clients = global_clients
) -> str:
    """
    Login User and return JWT token
    """
    # authenticate with supabase
    # if user is not authenticated raise exception
    # create token and return it
    session = clients.supabase.auth.sign_in(email=email, password=password)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    return session.access_token


async def register_user(
    email: str, password: str, name: str, role: Role, clients: Clients = global_clients
) -> str:
    """
    Register User and return JWT token
    """
    # sign up user with supabase
    # if user is not authenticated raise exception
    # create User in database with prisma (you get the user_id from supabase)
    # create token and return it
    result = clients.supabase.auth.sign_up(email=email, password=password)

    return f"User with id {result.id} was created"

    # prisma: Prisma = await clients.prisma
    #
    # user = await prisma.user.create(
    #     data={
    #         "id": result["data"]["id"],
    #         "email": email,
    #         "name": name,
    #         "role": role,
    #     }
    # )


async def logout_user(id: str, token: str, clients: Clients = global_clients) -> None:
    """
    Logout User, revoke JWT token
    """
    # revoke token in supabase
    global_clients.supabase.auth.sign_out()


async def get_user(user_id: str, clients: Clients = global_clients) -> User:
    """
    Get User details
    """
    # get user from database
    # return user
    pass


async def get_users(
    condition: dict = {}, clients: Clients = global_clients
) -> list[User]:
    """
    Get all Users
    """
    # get users from database
    # return users
    pass


async def delete_user(user_id: str, clients: Clients = global_clients) -> None:
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
    clients: Clients = global_clients,
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
    city: str,
    country: str,
    geoLocation: str,
    importance: Importance,
    story: str,
    uri: str,
    User: User | None,
    userId: str | None,
    clients: Clients = global_clients,
) -> Place:
    """
    Create Place
    """
    # create place in database
    # return place

    prisma: Prisma = await clients.prisma

    response = await prisma.place.create(
        data=PlaceCreateInput(
            name=name,
            city=city,
            country=country,
            geolocation=geoLocation,
            importance=importance,
            story=story,
            uri=uri,
        )
    )

    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Place could not be created",
        )

    return response


async def modify_place(
    place_id: str,
    name: str,
    city: str,
    geolocation: str,
    country: str,
    importance: Importance,
    story: str,
    uri: str,
    User: User | None,
    userId: str | None,
    clients: Clients = global_clients,
) -> Place:
    """
    Modify Place
    """
    # modify place in database
    # return place
    prisma: Prisma = await clients.prisma

    place = await prisma.place.find_unique(where={"id": place_id})

    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Place not found"
        )

    place = await prisma.place.update(
        where={"id": place_id},
        data={
            "city": city,
            "country": country,
            "geolocation": geolocation,
            "importance": importance,
            "story": story,
            "uri": uri,
        },
    )

    if not place:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Place could not be modified",
        )

    return place


async def delete_place(place_id: str, clients: Clients = global_clients) -> None:
    """
    Delete Place
    """
    # delete place in database
    prisma: Prisma = await clients.prisma

    place = await prisma.place.find_unique(where={"id": place_id})

    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Place not found"
        )

    delete = await prisma.place.delete(where={"id": place_id})

    if not delete:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Place could not be deleted",
        )


async def get_place(place_id: str, clients: Clients = global_clients) -> Place:
    """
    Get Place
    """
    # get place from database
    # return place
    prisma: Prisma = await clients.prisma

    place = await prisma.place.find_unique(where={"id": place_id})

    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Place not found"
        )

    return place


async def get_places(
    condition: PlaceWhereInput = {}, clients: Clients = global_clients
) -> list[Place]:
    """
    Get all Places
    """
    prisma: Prisma = await clients.prisma

    places = await prisma.place.find_many(where=condition)

    return places


# Object3d Database functions


def get_bytes_from_url(img_path: str) -> bytes:
    # get image from /scenes folder
    img_path = os.path.join(os.getcwd(), "scenes", img_path)
    with open(img_path, "rb") as f:
        img_bytes = f.read()
    return img_bytes


def get_img_from_bytes(img_bytes: bytes) -> None:
    with open("test.avif", "wb") as f:
        f.write(img_bytes)


async def create_object3d(
    location: Place, placeId: str, img_url: str, clients: Clients = global_clients
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

    prisma: Prisma = await clients.prisma

    # create Object3D type
    obj3d = Object3D(id=object3d_id, location=location, placeId=placeId, img=img_bytes)
    # create object3d in database
    response = await prisma.object3d.create(data={"data": Base64(img_bytes)})

    # if object3d is not created raise exception
    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Object3D could not be created",
        )

    return obj3d


async def modify_object3d(
    object3d_id: str,
    placeId: str,
    img_url: str,
    clients: Clients = global_clients,
) -> Object3D:
    """
    Modify Object3D
    params: object3d_id: str
    params: location: Place
    params: placeId: str
    params: img_url: str
    """
    prisma: Prisma = await clients.prisma

    obj3d = await prisma.object3d.find_unique(where={"id": object3d_id})

    if not obj3d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Object3D not found"
        )

    location = await prisma.place.find_unique(where={"id": placeId})

    update = await prisma.object3d.update(
        where={"id": object3d_id},
        data={
            "data": Base64(get_bytes_from_url(img_url)),
        },
    )

    if not update:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Object3D could not be updated",
        )

    return obj3d


async def delete_object3d(object3d_id: str, clients: Clients = global_clients) -> None:
    """
    Delete Object3D
    params: object3d_id: str
    """

    prisma: Prisma = await clients.prisma

    delete = await prisma.object3d.delete(where={"id": object3d_id})
    # if object3d is not deleted raise exception
    if not delete:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Object3D could not be deleted",
        )


async def get_object3d(object3d_id: str, clients: Clients = global_clients) -> Object3D:
    """
    Get Object3D
    params: object3d_id: str
    """
    prisma: Prisma = await clients.prisma

    obj3d = await prisma.object3d.find_unique(where={"id": object3d_id})

    if not obj3d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Object3D not found"
        )

    return obj3d


async def get_object3ds(
    condition: Object3DWhereInput = {},
    clients: Clients = global_clients,
) -> list[Object3D]:
    """
    Get all Object3Ds
    params: condition: dict
    """
    prisma: Prisma = await clients.prisma

    # get object3ds from database
    obj3ds = await prisma.object3d.find_many(where=condition)

    return obj3ds
