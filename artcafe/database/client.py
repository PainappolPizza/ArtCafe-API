import os

from typing import Optional
from _prisma import Prisma
from supabase import create_client, Client as Supabase

from dotenv import load_dotenv


load_dotenv("artcafe/database/.env")


url: Optional[str] = os.environ.get("SUPABASE_URL")
key: Optional[str] = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Missing environment variables")
else:
    supabase: Supabase = create_client(
        supabase_url=url,
        supabase_key=key,
    )

    prisma = Prisma()
