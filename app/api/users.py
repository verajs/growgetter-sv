from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserDisplay, UserModel, PyObjectId
from app.utils.user_utils import get_password_hash, authenticate_user, create_access_token
from datetime import timedelta
from app.database import get_nosql_db
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


@router.get("/users/", response_model=list[UserDisplay])
async def get_users(db=Depends(get_nosql_db)):
    users = await db['users'].find({}).to_list(1000)
    return users


@router.post("/users/", response_model=UserDisplay)
async def create_user(user: UserCreate, db=Depends(get_nosql_db)):
    hashed_password = get_password_hash(user.password)
    new_user_data = user.dict()
    new_user_data['hashed_password'] = hashed_password
    del new_user_data['password']

    # Generate ObjectId for the id field
    new_user_data['id'] = str(ObjectId())

    new_user = UserModel(**new_user_data)
    try:
        result = await db['users'].insert_one(new_user.dict(by_alias=True))
        # Now that we've inserted the user, we don't need to add the _id to new_user_data
        new_user_data['id'] = result.inserted_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")
    return new_user.dict(by_alias=True)

@router.get("/users/{user_id}", response_model=UserDisplay)
async def get_user(user_id: str, db=Depends(get_nosql_db)):
    user = await db['users'].find_one({"id": PyObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_nosql_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)  # Correctly await the user authentication
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(data={"sub": user['username']}, expires_delta=access_token_expires)  # Ensure this function is awaited if async
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/users/{user_id}", response_model=UserDisplay)
async def update_user(user_id: str, update_data: UserUpdate, db=Depends(get_nosql_db)):
    update_json = update_data.dict(exclude_unset=True, by_alias=True)

    # Update the document using the ID from the URL
    result = await db['users'].update_one({"id": PyObjectId(user_id)}, {"$set": update_json})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no update needed")

    updated_user = await db['users'].find_one({"id": PyObjectId(user_id)})
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found after update")

    return updated_user


