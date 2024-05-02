from fastapi import APIRouter, HTTPException, Depends
from app.database import get_nosql_db
from app.schemas.todo import TodoCreate, TodoDisplay, TodoUpdate, PyObjectId
from bson import ObjectId
from typing import List
from datetime import datetime, date
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)


@router.get("/users/{user_id}/todos", response_model=List[TodoDisplay])
async def get_all_todos(user_id: str, db=Depends(get_nosql_db)):
    '''
    Get all todos for a user

    Parameters:
    user_id (str): The user id

    Returns:
    List[TodoDisplay]: A list of TodoDisplay objects
    '''
    user = await db.users.find_one({"id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if 'todos' not in user:
        return [] 

    return [TodoDisplay(**todo) for todo in user['todos']]


@router.post("/users/{user_id}/todos", response_model=TodoDisplay)
async def add_todo_to_user(user_id: str, todo_data: TodoCreate, db=Depends(get_nosql_db)):
    '''
    Add a new todo to a user's todo list

    Parameters:
    user_id (str): The user id
    todo_data (TodoCreate): The data of the todo to be added

    Returns:
    TodoDisplay: The added todo
    '''
    todo_dict = todo_data.dict()
    todo_dict['id'] = str(ObjectId())
    todo_dict['created_date'] = datetime.now()

    try:
        result = await db.users.update_one(
            {"id": user_id},
            {"$push": {"todos": todo_dict}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found or todo not added")
        
        return TodoDisplay(**todo_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/users/{user_id}/todos/{todo_id}", response_model=TodoDisplay)
async def update_todo(user_id: str, todo_id: str, todo_update_data: TodoUpdate, db=Depends(get_nosql_db)):
    """
    Updates a specific todo for a given user based on the provided todo update data.
    It only updates fields that are explicitly provided and non-null.

    Parameters:
    - user_id (str): The unique identifier for the user.
    - todo_id (str): The unique identifier for the todo item.
    - todo_update_data (TodoUpdate): The data transfer object containing fields that might be updated.
    - db: A dependency that injects the database session.

    Returns:
    - TodoDisplay: The updated todo information.

    Raises:
    - HTTPException: If no update data is provided, if the todo is not found, or if a database operation fails.
    """

    update_data = {k: v for k, v in todo_update_data.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    try:
        result = await db.users.update_one(
            {"id": user_id, "todos.id": todo_id},
            {"$set": {f"todos.$.{k}": v for k, v in update_data.items()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Todo not found or no update needed")
        
        updated_user = await db.users.find_one(
            {"id": user_id, "todos.id": todo_id},
            {"todos.$": 1}
        )
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="Todo not found after update")
        
        updated_todo = updated_user["todos"][0]  
        return TodoDisplay(**updated_todo)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}/todos/{todo_id}", status_code=204)
async def delete_todo(user_id: str, todo_id: str, db=Depends(get_nosql_db)):
    """
    Deletes a specific todo from a user's list of todos.

    Parameters:
    - user_id (str): The unique identifier for the user.
    - todo_id (str): The unique identifier for the todo item.
    - db: A dependency that injects the database session.

    Returns:
    - None

    Raises:
    - HTTPException: If the todo is not found or if a database operation fails.
    """
    try:
        result = await db.users.update_one(
            {"id": user_id},
            {"$pull": {"todos": {"id": todo_id}}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Todo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return None


@router.patch("/users/{user_id}/todos/{todo_id}/complete", response_model=TodoDisplay)
async def complete_todo(user_id: str, todo_id: str, db=Depends(get_nosql_db)):
    """
    Toggles the completion status of a todo item. If the todo is currently marked as completed, 
    it will be set to incomplete, and vice versa.

    Parameters:
    - user_id (str): The unique identifier for the user.
    - todo_id (str): The unique identifier for the todo item.
    - db: A dependency that injects the database session.

    Returns:
    - TodoDisplay: The todo item with updated completion status.

    Raises:
    - HTTPException: If the user or todo is not found, or if the update fails.
    """
    user = await db.users.find_one({"id": user_id, "todos.id": todo_id})
    if not user:
        raise HTTPException(status_code=404, detail="User or Todo not found")

    todo = next((item for item in user['todos'] if item['id'] == todo_id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.get('completed'):
        new_completed = False
        new_completed_date = None  
    else:
        new_completed = True
        new_completed_date = datetime.now()

    result = await db.users.update_one(
        {"id": user_id, "todos.id": todo_id},
        {"$set": {
            "todos.$.completed": new_completed,
            "todos.$.completed_date": new_completed_date
        }}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update the todo item")

    updated_todo = await db.users.find_one(
        {"id": user_id, "todos.id": todo_id},
        {"todos.$": 1}
    )
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found after update")

    return TodoDisplay(**updated_todo['todos'][0])  

@router.get("/users/{user_id}/todos/check_reset", response_model=List[TodoDisplay])
async def check_and_reset_todos(user_id: str, db=Depends(get_nosql_db)):
    """
    Checks and resets the completed status of todos based on the date they were completed. 
    Todos that were completed before today's date will have their completion status reset.

    Parameters:
    - user_id (str): The unique identifier for the user.
    - db: A dependency that injects the database session.

    Returns:
    - List[TodoDisplay]: A list of todos that had their completion status reset.

    Raises:
    - HTTPException: If the user is not found or no todos need processing.
    """
    current_time = datetime.now()
    logging.info(f"Current time: {current_time}")

    user = await db.users.find_one({"id": user_id})
    if not user:
        logging.info("User not found")
        raise HTTPException(status_code=404, detail="User not found")

    if 'todos' not in user or not user['todos']:
        logging.info("No todos to process")
        return []  

    updated_todos = []
    completions_needed_reset = 0

    for todo in user['todos']:
        should_reset = False
        logging.info(f"Checking todo: {todo['id']}, Completed: {todo.get('completed')}, Completed Date: {todo.get('completed_date')}")
        
        if todo.get('completed'):
            completed_date = todo.get('completed_date')
            if completed_date and completed_date.date() < current_time.date():
                should_reset = True

        if should_reset:
            logging.info(f"Resetting todo: {todo['id']}")
            todo['completed'] = False
            todo['completed_date'] = None
            completions_needed_reset += 1
            updated_todos.append(todo)

            result = await db.users.update_one(
                {"id": user_id, "todos.id": todo['id']},
                {"$set": {
                    "todos.$.completed": False,
                    "todos.$.completed_date": None
                }}
            )
            logging.info(f"Update result for todo {todo['id']}: {result.modified_count}")

    if completions_needed_reset > 0:
        new_count = user.get('completed_todos', 0) + completions_needed_reset
        logging.info(f"Updating completed todos count: {new_count}")
        tree_index = next((index for index, tree in enumerate(user['trees']) if tree['name'] == 'Uncaria'), None)

        if tree_index is not None:
            new_stage = user['trees'][tree_index]['stage'] + (new_count // 4) - (user.get('completed_todos', 0) // 4)
            await db.users.update_one(
                {"id": user_id},
                {"$set": {
                    "completed_todos": new_count,
                    f"trees.{tree_index}.stage": new_stage
                }}
            )

    return [TodoDisplay(**todo) for todo in updated_todos]
