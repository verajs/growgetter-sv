from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient

SECRET_KEY = "SUPERKEY"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
    plain_password (str): The plaintext password to verify.
    hashed_password (str): The hashed password to verify against.

    Returns:
    bool: True if the password is correct, False otherwise.
    """    
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a hash for the given password.

    Args:
    password (str): The password to hash.

    Returns:
    str: The hashed password.
    """
    return pwd_context.hash(password)

async def authenticate_user(db: AsyncIOMotorClient, username: str, password: str):
    """
    Authenticate a user against a database.

    Args:
    db (AsyncIOMotorClient): The database client.
    username (str): The username of the user to authenticate.
    password (str): The password of the user to authenticate.

    Returns:
    dict: User information if authentication is successful, None otherwise.
    """
    user = await db['users'].find_one({"username": username})  
    if user and pwd_context.verify(password, user['hashed_password']):
        return user
    return None

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token with an optional expiry time.

    Args:
    data (dict): The data to encode in the token.
    expires_delta (timedelta, optional): The amount of time until the token expires. Defaults to 15 minutes.

    Returns:
    str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
