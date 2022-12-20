from __future__ import annotations


from artcafe.models import *
from artcafe.utils import *
from artcafe.database import supabase, prisma

from typing import Optional


app = FastAPI(
    title="ArtCafe API",
    description="REST service for ArtCafe",
    version="0.2.17beta5",
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
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Login failed",
        )

    try:
        user = await prisma.user.find_first(
            where={"email": credentials.email}, include={"places": True}
        )
    except PrismaError:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Login failed",
        )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Login failed",
        )

    token = add_user(session.access_token, user)

    return {"token": token}


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
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
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
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Registration failed",
        )

    token = add_user(session.access_token, user)

    return {"token": token}


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
        token = remove_user(token)
        auth_user: AuthUser = supabase.auth.api.get_user(jwt=token)
    except APIError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Invalid JWT token, {e.msg}",
        )

    try:
        user = await prisma.user.find_first(
            where={"id": user_id}, include={"places": True}
        )
        req_user = await prisma.user.find_first(where={"email": auth_user.email or ""})
    except PrismaError:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    if not user or not req_user:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    # Check if user is allowed to access this user
    if (req_user.role != Role.Admin) or (req_user.email != user.email):
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
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
    user = await user_from(token=token, prisma=prisma, supabase=supabase)

    if not user.role == Role.Admin:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Access denied",
        )

    try:
        place = await prisma.place.create(
            data={
                "name": name,
                "city": city,
                "country": country,
                "geolocation": location,
                "importance": importance,
                "story": story,
                "uri": uri,
            }
        )

    except PrismaError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_400_BAD_REQUEST,
            detail=f"Could not create location, {e}",
        )

    return place


@app.get("/")
def root():
    return {
        "message": "Welcome to the ArtCafe API",
        "authors": "Antonino Rossi, Bertold Vincze, David Bobek, Dinu Scripnic",
    }
