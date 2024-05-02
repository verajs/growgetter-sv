from fastapi import APIRouter, HTTPException, Depends
from app.database import get_nosql_db
from pymongo.database import Database
from app.utils.analytics import calculate_avg_completion_time, calculate_completion_time
from typing import Optional

router = APIRouter()

@router.get("/users/{user_id}/average-completion-time", response_model=Optional[float])
async def get_average_completion_time(user_id: str, db: Database = Depends(get_nosql_db)):
    # Retrieve the user document with both todos and the stored average_completion_time
    user = await db.users.find_one({"id": user_id}, {"todos": 1, "average_completion_time": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    todos = user.get('todos', [])
    if not todos:  # Check if todos list is empty
        # If no todos, check if there's a stored average time
        return user.get('average_completion_time')

    avg_time_hours = calculate_avg_completion_time(todos)

    if avg_time_hours is None:
        # Return stored average if calculation yields None
        return user.get('average_completion_time')

    # Update the user's average completion time if a new one is calculated
    await db.users.update_one({"id": user_id}, {"$set": {"average_completion_time": avg_time_hours}})

    return avg_time_hours


@router.get("/users/{user_id}/todos/{todo_id}/completion-time", response_model=Optional[float])
async def get_todo_completion_time(user_id: str, todo_id: str, db: Database = Depends(get_nosql_db)):
    # Retrieve the user and then the specific todo
    user = await db.users.find_one({"id": user_id, "todos.id": todo_id}, {"todos.$": 1})
    if not user or not user.get('todos'):
        raise HTTPException(status_code=404, detail="Todo not found")

    todo = user['todos'][0]  # Extract the specific todo from the result
    completion_time_hours = calculate_completion_time(todo)
    
    if completion_time_hours is None:
        return None  # Could interpret as todo not completed or invalid date data

    return completion_time_hours
