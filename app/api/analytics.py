from fastapi import APIRouter, HTTPException, Depends
from app.database import get_nosql_db
from pymongo.database import Database
from app.utils.analytics import calculate_avg_completion_time, calculate_completion_time
from typing import Optional

router = APIRouter()

@router.get("/users/{user_id}/average-completion-time", response_model=Optional[float])
async def get_average_completion_time(user_id: str, db: Database = Depends(get_nosql_db)):
    """
    Retrieves the average completion time of todos for a specific user. If the average completion time
    is already calculated and no new todos are added, it returns the stored average. Otherwise, it
    recalculates the average completion time based on the user's todos.

    Parameters:
    - user_id (str): The unique identifier for the user.
    - db (Database): A dependency that injects the database session, provided by get_nosql_db.

    Returns:
    - Optional[float]: The average completion time of todos in hours. Returns None if there are no todos.

    Raises:
    - HTTPException: If the user is not found.
    """
    user = await db.users.find_one({"id": user_id}, {"todos": 1, "average_completion_time": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    todos = user.get('todos', [])
    if not todos:  
     
        return user.get('average_completion_time')

    avg_time_hours = calculate_avg_completion_time(todos)

    if avg_time_hours is None:
        return user.get('average_completion_time')

    await db.users.update_one({"id": user_id}, {"$set": {"average_completion_time": avg_time_hours}})

    return avg_time_hours


@router.get("/users/{user_id}/todos/{todo_id}/completion-time", response_model=Optional[float])
async def get_todo_completion_time(user_id: str, todo_id: str, db: Database = Depends(get_nosql_db)):
    """
    Retrieves the completion time for a specific todo of a user. It calculates the time based on the 
    start and end times of the todo.

    Parameters:
    - user_id (str): The unique identifier for the user.
    - todo_id (str): The unique identifier for the todo item.
    - db (Database): A dependency that injects the database session, provided by get_nosql_db.

    Returns:
    - Optional[float]: The completion time of the todo in hours. Returns None if the completion time
      is not calculable or the todo doesn't have the necessary time fields.

    Raises:
    - HTTPException: If the todo or user is not found.
    """
    user = await db.users.find_one({"id": user_id, "todos.id": todo_id}, {"todos.$": 1})
    if not user or not user.get('todos'):
        raise HTTPException(status_code=404, detail="Todo not found")

    todo = user['todos'][0]  
    completion_time_hours = calculate_completion_time(todo)
    
    if completion_time_hours is None:
        return None  
    return completion_time_hours
