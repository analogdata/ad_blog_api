# User API Documentation

## Overview

The User API provides endpoints for managing user profiles and accounts. It allows users to view and update their own profiles, and provides administrative endpoints for managing users.

## Base URL

```
/api/v1/user
```

## Authentication

- User endpoints: Requires user authentication
- Admin endpoints: Requires admin authentication

## Endpoints

### 1. Get Current User Profile

Retrieves the profile of the currently authenticated user.

- **URL**: `/profile`
- **Method**: `GET`
- **Auth Required**: Yes
- **Permissions**: Any authenticated user

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-09-09T19:00:00"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 2. Update Current User Profile

Updates the profile of the currently authenticated user.

- **URL**: `/profile`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Permissions**: Any authenticated user

#### Request Body

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "email": "john.smith@example.com"
}
```

#### Success Response

- **Code**: 200 OK
- **Content** (when email is not changed):

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "role": "user",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-09-09T19:00:00"
  },
  "message": "Profile updated successfully",
  "email_changed": false
}
```

- **Content** (when email is changed):

```json
{
  "user": {
    "id": 1,
    "email": "john.smith@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-09-09T19:00:00"
  },
  "message": "Profile updated successfully. You need to verify your new email address. Please check your inbox for verification instructions.",
  "email_changed": true,
  "verification_required": true
}
```

#### Error Responses

- **Code**: 400 BAD REQUEST
  - **Content**: Validation error details
- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 3. List All Users (Admin Only)

Retrieves a list of all users.

- **URL**: `/list`
- **Method**: `GET`
- **Auth Required**: Yes
- **Permissions**: Admin
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum number of records to return (default: 100)

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
[
  {
    "id": 1,
    "email": "user1@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-09-09T19:00:00",
    "author_id": null
  },
  {
    "id": 2,
    "email": "user2@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "author",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-09-09T19:30:00",
    "author_id": 1
  }
]
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 4. Get User by Email (Admin Only)

Retrieves a specific user by email.

- **URL**: `/{email}`
- **Method**: `GET`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `email`: Email of the user to retrieve

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-09-09T19:00:00",
  "author_id": null
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "User with email user@example.com not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 5. Delete User (Admin Only)

Deletes a user.

- **URL**: `/{user_id}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `user_id`: ID of the user to delete

#### Success Response

- **Code**: 204 NO CONTENT

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "User with ID {user_id} not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 6. Reset User Password (Admin Only)

Resets a user's password.

- **URL**: `/{user_id}/reset-password`
- **Method**: `POST`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `user_id`: ID of the user to reset password for

#### Request Body

```json
{
  "password": "new_password"  // Optional, if not provided a random password will be generated
}
```

#### Success Response

- **Code**: 200 OK
- **Content** (with custom password):

```json
{
  "message": "Password reset successfully",
  "new_password": "new_password",
  "password_type": "custom"
}
```

- **Content** (with generated password):

```json
{
  "message": "Password reset successfully",
  "new_password": "random_generated_password",
  "password_type": "generated"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "User with ID {user_id} not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

## Data Models

### User Response (Regular User)

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-09-09T19:00:00"
}
```

### Admin User Response (Admin View)

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-09-09T19:00:00",
  "author_id": null
}
```

### Profile Update Response

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-09-09T19:00:00"
  },
  "message": "Profile updated successfully",
  "email_changed": false
}
```

## Dependencies

### CurrentUser

This dependency function provides the currently authenticated user. It is used in the following endpoints:

- GET `/profile` (Get current user profile)
- PUT `/profile` (Update current user profile)

### AdminUser

This dependency function ensures that only users with the admin role can access the protected endpoints. It is used in the following endpoints:

- GET `/list` (List all users)
- GET `/{email}` (Get user by email)
- DELETE `/{user_id}` (Delete user)
- POST `/{user_id}/reset-password` (Reset user password)

## Flow Diagrams

### User Profile Management Flow

```
User -> GET /api/v1/user/profile -> Return User Profile
User -> PUT /api/v1/user/profile -> Update User Profile -> Return Updated Profile
```

### Admin User Management Flow

```
Admin -> GET /api/v1/user/list -> List All Users
Admin -> GET /api/v1/user/{email} -> Get Specific User
Admin -> DELETE /api/v1/user/{user_id} -> Delete User
Admin -> POST /api/v1/user/{user_id}/reset-password -> Reset User Password
```

## Special Considerations

1. When a user updates their email address, they need to verify the new email before it becomes active.
2. Admin users can view additional information about users, such as their author_id if they are linked to an author profile.
3. When resetting a password as an admin, you can either provide a custom password or let the system generate a random one.
