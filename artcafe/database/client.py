import os

from typing import Optional
from prisma_def import Prisma
from supabase import create_client, Client as Supabase

from dotenv import load_dotenv

from async_property import async_cached_property
from functools import cached_property

load_dotenv("artcafe/database/.env")


class Clients:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key

    @cached_property
    def supabase(self) -> Supabase:
        return create_client(self.url, self.key)

    @async_cached_property
    async def prisma(self) -> Prisma:
        prisma = Prisma()
        await prisma.connect()
        return prisma


url: Optional[str] = os.environ.get("SUPABASE_URL")
key: Optional[str] = os.environ.get("SUPABASE_KEY")


if not url or not key:
    raise ValueError("Missing environment variables")
else:
    global_clients = Clients(url=url, key=key)


__all__ = ["Supabase", "Prisma", "global_clients"]
