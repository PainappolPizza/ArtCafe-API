from __future__ import annotations

import requests
from main import RegisterModel, LoginModel, LogoutModel, Role
from pprint import pprint

base_url = "https://xgqxhw.deta.dev"


def make_user():
    email = input("Enter email: ")
    password = input("Enter password: ")
    name = input("Enter name: ")
    role = Role.User

    """
    Use the requests module to make a request to the API's register endpoint
    """
    response = requests.post(
        f"{base_url}/api/register",
        json={
            "email": email,
            "password": password,
            "name": name,
            "role": role,
        },
    )

    if response.status_code == 200:
        print("User created successfully")
        print(response.json())
    else:
        print("Failed to create user")
        print(response.json())


def login():
    email = input("Email: ")
    password = input("Password: ")

    response = requests.post(
        f"{base_url}/api/login",
        json={
            "email": email,
            "password": password,
        },
    )

    if response.status_code == 200:
        print("Login successful")
        print(response.json())

    else:
        print("Login failed")
        print(response.status_code)


def logout():
    response = requests.post(
        f"{base_url}/api/logout",
    )

    if response.status_code == 200:
        print("Logout successful")
        pprint(response.json())

    else:
        print("Logout failed")
        print(response.status_code)
