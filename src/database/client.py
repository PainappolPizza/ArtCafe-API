import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
client: Client = create_client(url, key)

__all__ = [client.__name__]
