from fastapi import FastAPI
from .api import todos
from .api import users
from app.database import connect_to_mongo, close_mongo_connection

# uvicorn app.main:app --reload

app = FastAPI()

app.include_router(todos.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
