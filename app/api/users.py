from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserDisplay, UserModel, PyObjectId, UserUpdate, UserResponse, TokenResponse
from app.utils.user_utils import get_password_hash, authenticate_user, create_access_token
from datetime import timedelta
from app.database import get_nosql_db
from bson import ObjectId
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

logging.basicConfig(level=logging.INFO)

@router.get("/users/", response_model=list[UserDisplay])
async def get_users(db=Depends(get_nosql_db)):
    """
    Retrieves a list of all users from the database.

    Parameters:
    - db: A dependency that injects the database session, provided by get_nosql_db.

    Returns:
    - list[UserDisplay]: A list of users formatted according to the UserDisplay schema.
    """
    users = await db['users'].find({}).to_list(1000)
    return users


@router.post("/users/", response_model=UserDisplay)
async def create_user(user: UserCreate, db=Depends(get_nosql_db)):
    """
    Creates a new user with the provided user data after performing validation checks
    for existing email and username.

    Parameters:
    - user (UserCreate): The user data required to create a new user.
    - db: A dependency that injects the database session, provided by get_nosql_db.

    Returns:
    - UserDisplay: The created user's data formatted according to the UserDisplay schema.

    Raises:
    - HTTPException: If the email or username is already registered or if there is a failure in user creation.
    """
    existing_user = await db['users'].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await db['users'].find_one({"username": user.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    new_user_data = user.dict()
    new_user_data['hashed_password'] = hashed_password
    del new_user_data['password']

    new_user_data['id'] = str(ObjectId())

    new_user = UserModel(**new_user_data)
    try:
        result = await db['users'].insert_one(new_user.dict(by_alias=True))
        new_user_data['id'] = result.inserted_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")
    return new_user.dict(by_alias=True)

@router.get("/users/{user_id}", response_model=UserDisplay)
async def get_user(user_id: str, db=Depends(get_nosql_db)):
    """
    Retrieves a specific user by their unique identifier.

    Parameters:
    - user_id (str): The unique identifier of the user.
    - db: A dependency that injects the database session, provided by get_nosql_db.

    Returns:
    - UserDisplay: The user's data formatted according to the UserDisplay schema.

    Raises:
    - HTTPException: If the user is not found.
    """
    user = await db['users'].find_one({"id": PyObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_nosql_db)):
    """
    Authenticates a user and issues a JWT token upon successful authentication.

    Parameters:
    - form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
    - db: A dependency that injects the database session, provided by get_nosql_db.

    Returns:
    - TokenResponse: The response containing the JWT token and user's information.

    Raises:
    - HTTPException: If the username or password is incorrect.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(data={"sub": user['username']}, expires_delta=access_token_expires)
    
    user_response = UserResponse(
        id=user['id'],  
        username=user['username'],
        email=user['email'],
        name=user.get('name', ''),  
        trees=user.get('trees', []),
        completed_todos=user.get('completed_todos', 0)
        
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.put("/users/{user_id}", response_model=UserDisplay)
async def update_user(user_id: str, update_data: UserUpdate, db=Depends(get_nosql_db)):
    """
    Updates the specified user with the provided update data.

    Parameters:
    - user_id (str): The unique identifier of the user.
    - update_data (UserUpdate): The data used to update the user.
    - db: A dependency that injects the database session, provided by get_nosql_db.

    Returns:
    - UserDisplay: The updated user's data formatted according to the UserDisplay schema.

    Raises:
    - HTTPException: If the user is not found, no update is needed, or the update fails.
    """
    update_json = update_data.dict(exclude_unset=True, by_alias=True)

    result = await db['users'].update_one({"id": PyObjectId(user_id)}, {"$set": update_json})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no update needed")

    updated_user = await db['users'].find_one({"id": PyObjectId(user_id)})
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found after update")

    return updated_user


