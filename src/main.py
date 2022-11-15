from __future__ import annotations
import asyncio
from prisma import Prisma
from prisma.enums import Role


async def main() -> int:
    client = Prisma()
    await client.connect()

    user = await client.user.create(
        data={
            "email": "someemail@email.net",
            "name": "Robert",
            "role": Role.Admin,
            "score": 0,
        }
    )

    print(f"{user=!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
