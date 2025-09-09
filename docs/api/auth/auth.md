# Authentication API Documentation

## Overview

The Authentication API provides endpoints for user registration, authentication, email verification, and password management. It implements JWT-based authentication with access and refresh tokens.

## Base URL

```
/api/v1/auth
```

## Authentication

- Most endpoints: No authentication required
- Register endpoint: Requires admin authentication

## Endpoints

### 1. Register User (Admin Only)

Registers a new user with email and password.

- **URL**: `/register`
- **Method**: `POST`
- **Auth Required**: Yes (Admin)
- **Permissions**: Admin

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

#### Success Response

- **Code**: 201 CREATED
- **Content**:

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-09-09T19:00:00"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 400 BAD REQUEST
  - **Content**: Validation error details
- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "User with this email already exists"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 2. Login

Authenticates a user and returns JWT tokens.

- **URL**: `/login`
- **Method**: `POST`
- **Auth Required**: No
- **Permissions**: None

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Invalid email or password"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Email not verified. Please verify your email before using this service."}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 3. Refresh Token

Gets a new access token using a refresh token.

- **URL**: `/refresh`
- **Method**: `POST`
- **Auth Required**: No
- **Permissions**: None

#### Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Invalid refresh token"}`
  - **Content**: `{"detail": "User not found"}`
  - **Content**: `{"detail": "User is inactive"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Email not verified. Please verify your email before using this service."}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 4. Verify Email

Verifies a user's email address using a verification token.

- **URL**: `/verify-email`
- **Method**: `POST`
- **Auth Required**: No
- **Permissions**: None

#### Request Body

```json
{
  "token": "verification_token_string"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "message": "Email verified successfully"
}
```

#### Error Responses

- **Code**: 400 BAD REQUEST
  - **Content**: `{"detail": "Invalid verification token"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 5. Forgot Password

Requests a password reset for a user.

- **URL**: `/forgot-password`
- **Method**: `POST`
- **Auth Required**: No
- **Permissions**: None

#### Request Body

```json
{
  "email": "user@example.com"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "message": "If your email is registered, you will receive a password reset link"
}
```

#### Error Responses

- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 6. Reset Password

Resets a user's password using a reset token.

- **URL**: `/reset-password`
- **Method**: `POST`
- **Auth Required**: No
- **Permissions**: None

#### Request Body

```json
{
  "token": "reset_token_string",
  "password": "new_password",
  "confirm_password": "new_password"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "message": "Password reset successful"
}
```

#### Error Responses

- **Code**: 400 BAD REQUEST
  - **Content**: `{"detail": "Passwords do not match"}`
  - **Content**: `{"detail": "Invalid reset token"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`

### 7. Logout

Logs out a user (client-side implementation).

- **URL**: `/logout`
- **Method**: `POST`
- **Auth Required**: No
- **Permissions**: None

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "message": "Logout successful"
}
```

## Data Models

### User

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

### Token

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Dependencies

### AdminUser

This dependency function ensures that only users with the admin role can access the protected endpoints. It is used in the following endpoints:

- POST `/register` (Register a new user)

### verify_refresh_token

This function verifies the refresh token and extracts the token data. It is used in:

- POST `/refresh` (Refresh access token)

### create_tokens

This function creates new access and refresh tokens for a user. It is used in:

- POST `/login` (Login)
- POST `/refresh` (Refresh access token)

## Flow Diagrams

### Registration Flow

```
Admin -> POST /api/v1/auth/register -> Create User -> Generate Verification Token -> Send Verification Email -> Return User
User -> POST /api/v1/auth/verify-email -> Verify Email -> Mark as Verified
```

### Authentication Flow

```
User -> POST /api/v1/auth/login -> Authenticate -> Generate Tokens -> Return Tokens
User -> Use Access Token for API Requests
User -> When Access Token Expires -> POST /api/v1/auth/refresh -> Generate New Tokens -> Return Tokens
User -> POST /api/v1/auth/logout -> Clear Tokens (Client-side)
```

### Password Reset Flow

```
User -> POST /api/v1/auth/forgot-password -> Generate Reset Token -> Send Reset Email
User -> POST /api/v1/auth/reset-password -> Verify Token -> Update Password -> Return Success
```

## Security Considerations

1. JWT tokens are used for authentication
2. Access tokens have a short lifespan (typically 30 minutes)
3. Refresh tokens have a longer lifespan (typically 7 days)
4. Password reset tokens expire after a short period (typically 1 hour)
5. Email verification is required before using the API
6. Passwords are hashed using bcrypt
7. User registration is restricted to admin users only
