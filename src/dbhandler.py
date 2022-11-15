from __future__ import annotations
import asyncio
from prisma import Prisma
from prisma.enums import Role

###
# Get user from database
# Params:
#   email: str
# Returns:
#   user: Prisma.user | None
# Path: src\dbhandler.py
###
async def get_user(email: str) -> Prisma.user | None:
    client = Prisma()
    await client.connect()
    user = await client.user.find_first(
        where={
            "email": email
        }
    )
    return user

