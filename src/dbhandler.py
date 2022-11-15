from __future__ import annotations
from prisma import Prisma
from prisma.models import User
from prisma.enums import Role


async def get_user(email: str, client: Prisma = Prisma()) -> User | None:
    """
    Fetch user from database

    Args:
        email (str): email of user to fetch

    Returns:
        User | None: User object if found, None if not found
    """
    await client.connect()
    user = await client.user.find_first(where={"email": email})
    return user
