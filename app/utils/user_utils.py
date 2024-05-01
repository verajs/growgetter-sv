from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient

SECRET_KEY = "SUPERKEY"  # Replace with a real key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(db: AsyncIOMotorClient, username: str, password: str):
    user = await db['users'].find_one({"username": username})  # Make sure to await the db call
    if user and pwd_context.verify(password, user['hashed_password']):
        return user
    return None

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
