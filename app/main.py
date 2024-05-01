from fastapi import FastAPI
from .api import todos
from .api import users
from app.database import connect_to_mongo, close_mongo_connection
from .api import analytics
# uvicorn app.main:app --reload
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust the allowed origins as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allowing all methods
    allow_headers=["*"],
)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
