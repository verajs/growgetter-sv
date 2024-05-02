from datetime import datetime
from typing import List


def parse_datetime(date_str: str) -> datetime:
    """
    Convert a datetime string in ISO format to a datetime object.

    Parameters:
    - date_str (str): The datetime string in ISO 8601 format ('YYYY-MM-DDTHH:MM:SS').

    Returns:
    - datetime: The corresponding datetime object, or None if the string cannot be parsed.
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')  
    except ValueError:
        return None

def calculate_avg_completion_time(todos: List[dict]) -> int:
    """
    Calculate the average time taken to complete tasks in hours.

    Parameters:
    - todos (List[dict]): A list of dictionaries, each representing a task with keys 'completed',
                          'completed_date', and 'created_date'.

    Returns:
    - int: The average completion time of the completed tasks in hours, rounded to the nearest hour.
           Returns None if no tasks have been completed.
    """
    total_time = 0
    count = 0
    
    for todo in todos:
        if todo.get('completed') and todo.get('completed_date') and todo.get('created_date'):
            created_date = todo['created_date']
            completed_date = todo['completed_date']

            if isinstance(created_date, str):
                created_date = parse_datetime(created_date)
            if isinstance(completed_date, str):
                completed_date = parse_datetime(completed_date)

            if created_date and completed_date:
                completion_time = completed_date - created_date
                total_time += completion_time.total_seconds()
                count += 1

    if count == 0:
        return None  

    return round((total_time / count) / 3600)  

def calculate_completion_time(todo: dict) -> int:
    """
    Calculate the time taken to complete a single task in hours.

    Parameters:
    - todo (dict): A dictionary representing a task with keys 'completed', 'completed_date',
                   and 'created_date'.

    Returns:
    - int: The time taken to complete the task in hours, rounded to the nearest hour.
           Returns None if the task is incomplete or if dates are not valid.
    """
    if todo.get('completed') and todo.get('completed_date') and todo.get('created_date'):
        created_date = todo['created_date']
        completed_date = todo['completed_date']

        if isinstance(created_date, str):
            created_date = parse_datetime(created_date)
        if isinstance(completed_date, str):
            completed_date = parse_datetime(completed_date)

        if created_date and completed_date:
            completion_time = completed_date - created_date
            return round(completion_time.total_seconds() / 3600) 

    return None  
