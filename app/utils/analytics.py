from datetime import datetime
from typing import List


def parse_datetime(date_str):
    """Utility function to safely parse datetime strings to datetime objects."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')  # Adjust the format string as necessary
    except ValueError:
        return None

def calculate_avg_completion_time(todos: List[dict]):
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
        return None  # No completed todos with valid dates

    return round((total_time / count) / 3600)  # Returns average time rounded to nearest hour

def calculate_completion_time(todo: dict):
    if todo.get('completed') and todo.get('completed_date') and todo.get('created_date'):
        created_date = todo['created_date']
        completed_date = todo['completed_date']

        if isinstance(created_date, str):
            created_date = parse_datetime(created_date)
        if isinstance(completed_date, str):
            completed_date = parse_datetime(completed_date)

        if created_date and completed_date:
            completion_time = completed_date - created_date
            return round(completion_time.total_seconds() / 3600)  # Convert to hours and round

    return None  # Return None if not completed or dates are invalid
