from __future__ import annotations


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


@app.post("/api/login", response_model=SignOnResponse, tags=["Authentication"])
async def login(credentials: LoginModel):
    """
    Login User and return JWT token
    """
    session: Session | None = supabase.auth.sign_in(
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
    except PrismaError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Registration failed, cannot create user, {e}",
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


@app.get("/api/places/{city_name}", response_model=list[Place], tags=["Place"])
async def place_from_city(city_name: str, token: str):
    """
    Get all places from a city.
    Requires authentication.
    """
    # Silent validation
    _ = await user_from(token=token, prisma=prisma, supabase=supabase)

    try:
        places = await prisma.place.find_many(where={"city": city_name})
    except PrismaError:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"Places not found",
        )

    return places


@app.get("/api/places/{place_id}", response_model=Place, tags=["Place"])
async def place_from_id(place_id: str, token: str):
    """
    Get a place by id.
    Requires authentication.
    """
    # Silent validation
    _ = await user_from(token=token, prisma=prisma, supabase=supabase)

    try:
        place = await prisma.place.find_first(where={"id": place_id})
    except PrismaError:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"Place not found",
        )

    return place


@app.get("/api/places/{user_id}", response_model=list[Place], tags=["Place"])
async def place_from_user(user_id: str, token: str):
    """
    Get all places from a user.
    Requires authentication.
    """
    # Silent validation
    _ = await user_from(token=token, prisma=prisma, supabase=supabase)

    try:
        places = await prisma.place.find_many(where={"user_id": user_id})
    except PrismaError:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"Places not found",
        )

    return places


@app.get("/api/places/recent", response_model=list[Place], tags=["Place"])
async def recent_places(token: str):
    """
    Get all places from a user.
    Requires authentication.
    """
    # Silent validation
    _ = await user_from(token=token, prisma=prisma, supabase=supabase)

    try:
        # Take the last 12 places (in chronological order)
        places = await prisma.place.find_many(take=12, order={"createdAt": "desc"})
    except PrismaError:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"Places not found",
        )

    return places


@app.post("/api/places", response_model=Place, tags=["Place"])
async def create_place(
    place_data: PlaceCreateInput,
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
                "name": place_data.name,
                "city": place_data.city,
                "country": place_data.country,
                "geolocation": place_data.geolocation,
                "importance": place_data.importance,
                "story": place_data.story,
                "uri": place_data.uri,
            }
        )

    except PrismaError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_400_BAD_REQUEST,
            detail=f"Could not create location, {e}",
        )

    return place


@app.patch("/api/places/{place_id}", response_model=Place, tags=["Place"])
async def update_place(edits: PlaceUpdateInput, token: str):
    user = await user_from(token=token, prisma=prisma, supabase=supabase)

    if not user.role == Role.Admin:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Access denied",
        )

    try:
        place = await prisma.place.update(
            where={"id": edits.id},
            data={
                "name": edits.name,
                "city": edits.city,
                "country": edits.country,
                "geolocation": edits.geolocation,
                "importance": edits.importance,
                "story": edits.story,
                "uri": edits.uri,
            },
        )
    except PrismaError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_400_BAD_REQUEST,
            detail=f"Could not update location, {e}",
        )

    return place


@app.delete("/api/places/{place_id}", response_model=Place, tags=["Place"])
async def delete_place(place_id: str, token: str):
    user = await user_from(token=token, prisma=prisma, supabase=supabase)

    if not user.role == Role.Admin:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Access denied",
        )

    try:
        place = await prisma.place.delete(where={"id": place_id})
    except PrismaError as e:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete location, {e}",
        )

    return place


@app.get("/api/users/new_creators", response_model=list[User], tags=["User"])
async def new_creators(token: str):
    """
    Get all new creators.
    Requires authentication.
    """
    # Silent validation
    _ = await user_from(token=token, prisma=prisma, supabase=supabase)

    try:
        users = await prisma.user.find_many(where={"role": Role.Creator})
    except PrismaError:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"Users not found",
        )

    return users


@app.get("/api/users/accounts/{user_email}", response_model=User, tags=["User"])
async def user_from_email(user_email: str, token: str):
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


@app.patch("/api/users/{user_id}", response_model=User, tags=["User"])
async def update_user(edits: UserUpdateInput, token: str):
    user = await user_from(token=token, prisma=prisma, supabase=supabase)

    if not user.role == Role.Admin:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_403_FORBIDDEN,
            detail=f"Access denied",
        )

    try:
        user = await prisma.user.update(
            where={"id": edits.id},
            data={**edits},
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


@app.delete("/api/users/{user_id}", response_model=User, tags=["User"])
async def delete_user(user_id: str, token: str):
    user = await user_from(token=token, prisma=prisma, supabase=supabase)

    if not user.role == Role.Admin:
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
