from fastapi import FastAPI
from authentication import *
from dbhandler import *


app = FastAPI()
    

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/api/register")
async def register():
    return {"message": "Hello World"}


@app.post("/api/login")
async def login():
    return {"message": "Hello World"}
    
    
@app.post("/api/logout")
async def logout():
    return {"message": "Hello World"}


@app.get("/api/user/{user_id}")
async def get_user():
    return {"message": "Hello World"}

