import jwt
from prisma.models import User

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNjcxNTI5MTE5LCJzdWIiOiJhMjE1YjNkMy1lODVjLTRkYzgtOGFkMy1jNTUxY2ZhM2E2NzEiLCJlbWFpbCI6ImFkbWluQGFydGNhZmUuYXQiLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7fSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTY3MTUyNTUxOX1dLCJzZXNzaW9uX2lkIjoiNTg0NmQwOWQtOTM3NC00OTU4LWI2ZGItNDZhNDExODVlNzBkIn0.syZDOSx1ViRuGiOzKmrb_0g5lOGVevVwx8IYt9-35jM"
secret = "hI3sM6sZ0/hZj0IHJOjtoNdquv6jc6Dt6JNNYP5DbLBq+qRWNNXQ33WN2nNn38odkbLsKkM/oSmVJIR9aDXPvQ=="


def add_user(token: str, user: User) -> str:
    decoded = jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256"])
    decoded["user"] = user
    return jwt.encode(decoded, secret)


def remove_user(token: str) -> str:
    decoded = jwt.decode(token, options={"verify_signature": False},  algorithms=["HS256"])
    del decoded["user"]
    return jwt.encode(decoded, secret)


added = add_user(token, {"name": "test"})
print(added)

removed = remove_user(added)
print(removed)

assert removed == token
