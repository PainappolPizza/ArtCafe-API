from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from artcafe.models import *
from artcafe.utils import *
from artcafe.database import supabase, prisma


app = FastAPI(
    title="ArtCafe API",
    description="REST service for ArtCafe",
    version="0.2.17beta6",
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


@app.post("/api/login", tags=["Authentication"])
async def login(credentials: Credentials) -> SignOnResponse:
    """
    Login User and return JWT token
    """
    result = await validate_user(
        credentials=credentials.into_signin(),
        authenticate=supabase.auth.sign_in_with_password,
        query=lambda: prisma.user.find_first(where={"email": credentials.email}),
    )

    return handle_result(result)


@app.post("/api/register", tags=["Authentication"])
async def register(register_data: RegisterModel) -> SignOnResponse:
    """
    Register User and return JWT token
    """
    result = await validate_user(
        credentials=register_data.credentials.into_signup(),
        authenticate=supabase.auth.sign_up,
        query=lambda: prisma.user.create(
            data={**register_data.user_data, "email": register_data.credentials.email},
        ),
    )

    return handle_result(result)


@app.post("/api/logout", tags=["Authentication"])
async def logout() -> LogoutResponse:
    """
    Logout User, revoke JWT token
    """
    supabase.auth.sign_out()

    return LogoutResponse(message="Logged out successfully")


@app.get("/api/user/{user_id}", tags=["User"])
async def get_user(user_id: str, token: str) -> User:
    """
    Get details of a user by id.
    Requires authentication.
    Only if role is Admin or user_id is the same as the user_id of the authenticated user.
    Get User details
    """

    # Validate token
    try:
        token = remove_user(token)
        admin = supabase.auth.get_user(jwt=token)
    except AuthError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Invalid JWT token, {e!r}",
        )

    if not admin.user or not admin.user.email:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Invalid JWT token, {admin!r}",
        )

    try:
        user = await prisma.user.find_first(
            where={"id": user_id},
        )
        superuser = await prisma.user.find_first(where={"email": admin.user.email})
    except PrismaError:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    if not user or not superuser:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    # Check if user is allowed to access this user
    if (superuser.role != Role.ADMIN) and (user.id != superuser.id):
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Access denied",
        )

    return user


@app.get("/api/users/new_creators", tags=["User"])
async def new_creators(token: str) -> list[User]:
    """
    Get all new creators.
    Requires authentication.
    """
    # Silent validation
    _ = await user_from(token=token, prisma=prisma, supabase=supabase)

    try:
        users = await prisma.user.find_many(where={"role": Role.USER})
    except PrismaError:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"Users not found",
        )

    return users


@app.get("/api/users/accounts/{user_email}", tags=["User"])
async def user_from_email(user_email: str, token: str) -> User:
    """
    Get user from email.
    Requires authentication.
    """
    # Silent validation
    _ = await user_from(token=token, prisma=prisma, supabase=supabase)

    try:
        user = await prisma.user.find_first(where={"email": user_email})
    except PrismaError:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    return user


@app.patch("/api/users/{user_id}", tags=["User"])
async def update_user(edits: UserUpdateInput, token: str) -> User:
    user = await user_from(token=token, prisma=prisma, supabase=supabase)

    if not user.role == Role.ADMIN:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Access denied",
        )

    try:
        user = await prisma.user.update(
            where={"id": user.id},
            data=edits,
        )
    except PrismaError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_400_BAD_REQUEST,
            detail=f"Could not update user, {e}",
        )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    return user


@app.delete("/api/users/{user_id}", tags=["User"])
async def delete_user(user_id: str, token: str) -> User:
    user = await user_from(token=token, prisma=prisma, supabase=supabase)

    if not user.role == Role.ADMIN:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Access denied",
        )

    try:
        user = await prisma.user.delete(where={"id": user_id})
    except PrismaError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete user, {e}",
        )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    return user


@app.get("/")
def root():
    return {
        "message": "Welcome to the ArtCafe API",
        "authors": "Antonino Rossi, Bertold Vincze, David Bobek, Dinu Scripnic",
    }
