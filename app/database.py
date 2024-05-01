from motor.motor_asyncio import AsyncIOMotorClient
import os
from fastapi import Depends

# Database connection string and client setup
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://sebastianazuajev:growthgetter3399@growthgetter.zm6myud.mongodb.net/?retryWrites=true&w=majority&appName=Growthgetter")  # Secure this in production
client: AsyncIOMotorClient = None

# Database instance
database = None

def get_database() -> AsyncIOMotorClient:
    return database

async def connect_to_mongo():
    global client, database
    client = AsyncIOMotorClient(MONGODB_URL)
    database = client['todo_list_db']

async def close_mongo_connection():
    client.close()

# Dependency to inject database into route handlers
async def get_nosql_db():
    db = get_database()
    try:
        yield db
    finally:
        # Potentially close db cursor or perform other cleanup actions
        pass
