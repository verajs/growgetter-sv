# API Documentation

## User Management Routes

### `GET /users/`
- Retrieves a list of all users.
- **Returns**: A list of users formatted according to the UserDisplay schema.

### `POST /users/`
- Creates a new user with the provided data.
- **Returns**: The created user's data formatted according to the UserDisplay schema.
- **Errors**: Raises HTTPException for duplicate email or username, or if creation fails.

### `GET /users/{user_id}`
- Retrieves a specific user by their unique identifier.
- **Returns**: The user's data formatted according to the UserDisplay schema.
- **Errors**: Raises HTTPException if the user is not found.

### `PUT /users/{user_id}`
- Updates the specified user with the provided update data.
- **Returns**: The updated user's data formatted according to the UserDisplay schema.
- **Errors**: Raises HTTPException if the user is not found or no update is needed.

### `POST /token`
- Authenticates a user and issues a JWT token upon successful authentication.
- **Returns**: A token response with JWT token and user's information.
- **Errors**: Raises HTTPException if authentication fails.

## Todo Management Routes

### `GET /users/{user_id}/todos`
- Retrieves all todos for a specified user.
- **Returns**: A list of todo displays.

### `POST /users/{user_id}/todos`
- Adds a new todo to a user's todo list.
- **Returns**: The added todo display.
- **Errors**: Raises HTTPException if the user is not found or the todo is not added.

### `GET /users/{user_id}/todos/{todo_id}/completion-time`
- Retrieves the completion time for a specific todo.
- **Returns**: The completion time in hours, or None if not calculable.

### `PUT /users/{user_id}/todos/{todo_id}`
- Updates a specific todo based on provided data.
- **Returns**: The updated todo information.
- **Errors**: Raises HTTPException if the todo is not found or no update is needed.

### `DELETE /users/{user_id}/todos/{todo_id}`
- Deletes a specific todo from a user's list.
- **Errors**: Raises HTTPException if the todo is not found or if a database operation fails.

### `PATCH /users/{user_id}/todos/{todo_id}/complete`
- Toggles the completion status of a todo.
- **Returns**: The todo with updated completion status.
- **Errors**: Raises HTTPException if the todo or user is not found.

### `GET /users/{user_id}/average-completion-time`
- Retrieves the average completion time of todos for a specific user.
- **Returns**: The average time in hours, or None if there are no todos.
- **Errors**: Raises HTTPException if the user is not found.


### `GET /users/{user_id}/todos/check_reset`
- Checks and resets the completed status of todos based on the completion date..
- **Returns**: a list of todos that had their completion status reset.
- **Errors**: Raises HTTPException if the user is not found or no todos need processing.