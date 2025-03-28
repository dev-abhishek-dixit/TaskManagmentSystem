# Task Management API

A RESTful API for task management built with Django REST Framework and JWT authentication.

## Features

- JWT Authentication
- CRUD operations for tasks
- Task assignment to users
- Task status management (pending/completed)
- Task filtering by status and assigned user
- Overdue task tracking
- Rate limiting
- Mysql Database
- Django Default caching LocMemCache (for production we should use Redis,datambase etc)

## Prerequisites

- Python 3.13.2
- Mysql 8.0
- Redis (optional, for caching)

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```
Note: if any Library fails then downgrate its version from requirement.txt

3. Set up MySQL:
   - Install PostgreSQL if not already installed
   - Create a new database:
   ```bash
   createdb taskmanagement
   ```

4. Configure environment variables:
   Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=your-db-name
   DB_USER=user-name
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. Apply migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication

#### Get JWT Token
```
POST /api/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

#### Refresh JWT Token
```
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "your_refresh_token"
}
```

### Tasks

#### List All Tasks
```
GET /api/tasks/
Authorization: Bearer your.jwt.token
```

#### Create Task
```
POST /api/tasks/
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "title": "Task Title",
    "description": "Task Description",
    "status": "pending",
    "due_date": "2024-03-27T15:00:00Z",
    "assigned_to_id": 1
}
```

#### Get Single Task
```
GET /api/tasks/{id}/
Authorization: Bearer your.jwt.token
```

#### Update Task
```
PUT /api/tasks/{id}/
Authorization: Bearer your.jwt.token
Content-Type: application/json

{
    "title": "Updated Title",
    "description": "Updated Description",
    "status": "completed",
    "due_date": "2024-03-28T15:00:00Z",
    "assigned_to_id": 2
}
```

#### Delete Task
```
DELETE /api/tasks/{id}/
Authorization: Bearer your.jwt.token
```


#### Filter Tasks
```
GET /api/tasks/?status=pending
GET /api/tasks/?assigned_to=1
GET /api/tasks/?status=pending&assigned_to=1
Authorization: Bearer your.jwt.token
```

### Users

#### List All Users
```
GET /api/users/
Authorization: Bearer your.jwt.token
```

#### Get Single User
```
GET /api/users/{id}/
Authorization: Bearer your.jwt.token
```

## Response Format

All API responses follow this format:
```json
{
    "status": "success",
    "message": "Operation message",  // for create/update/delete operations
    "data": {
        // Response data
    }
}
```

## Error Responses

- 400 Bad Request: Invalid data
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource not found
- 429 Too Many Requests: Rate limit exceeded

## Rate Limiting

- 5 requests per minute per user for task operations (used 5 for testing purpous)

## Example Usage
- Added a postman collection with variables just set Django server url
- No need to set up jwt token, when you hit login api with username and password token will be set automatically  

## Run Test

```bash
python manage.py test
```