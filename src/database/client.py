import os

from prisma import Prisma
from supabase import create_client, Client

from dataclasses import dataclass
from dotenv import load_dotenv

from async_property import async_cached_property
from functools import cached_property

load_dotenv()


@dataclass(frozen=True, kw_only=True)
class Clients:
    url: str
    key: str

    @cached_property
    def client(self) -> Client:
        return create_client(self.url, self.key)

    @async_cached_property
    async def prisma(self) -> Prisma:
        prisma = Prisma()
        await prisma.connect()
        return prisma


url: str | None = os.environ.get("SUPABASE_URL")
key: str | None = os.environ.get("SUPABASE_KEY")


if not url or not key:
    raise ValueError("Missing environment variables")
else:
    global_clients = Clients(url=url, key=key)


__all__ = ["Clients", "global_clients"]
