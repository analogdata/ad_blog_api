# Subscriber API Documentation

## Overview

The Subscriber API provides endpoints for managing newsletter subscribers. It allows users to subscribe, verify their subscription, and unsubscribe from newsletters. It also provides administrative endpoints for managing subscribers.

## Base URL

```
/api/v1/subscriber
```

## Authentication

- Public endpoints: No authentication required
- Admin endpoints: Requires admin user authentication

## Endpoints

### 1. Subscribe with Email

Creates a new subscriber with the provided email address.

- **URL**: `/`
- **Method**: `POST`
- **Auth Required**: No
- **Permissions**: None

#### Request Body

```json
{
  "email": "example@example.com"
}
```

#### Success Response

- **Code**: 201 CREATED
- **Content**:

```json
{
  "id": 1,
  "email": "example@example.com",
  "is_active": true,
  "is_verified": false,
  "verification_token": "random_token_string",
  "created_at": "2025-09-09T19:00:00",
  "subscribed_at": "2025-09-09T19:00:00",
  "verified_at": null,
  "unsubscribed_at": null
}
```

#### Error Responses

- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "Subscriber with email 'example@example.com' already exists"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 2. Verify Subscription

Verifies a subscriber using the verification token.

- **URL**: `/verify`
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
  "id": 1,
  "email": "example@example.com",
  "is_active": true,
  "is_verified": true,
  "verification_token": null,
  "created_at": "2025-09-09T19:00:00",
  "subscribed_at": "2025-09-09T19:00:00",
  "verified_at": "2025-09-09T19:05:00",
  "unsubscribed_at": null
}
```

#### Error Responses

- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Invalid verification token"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 3. Unsubscribe by Email

Unsubscribes a user using their email address.

- **URL**: `/unsubscribe`
- **Method**: `POST`
- **Auth Required**: No
- **Permissions**: None

#### Request Body

```json
{
  "email": "example@example.com"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "email": "example@example.com",
  "is_active": false,
  "is_verified": true,
  "verification_token": null,
  "created_at": "2025-09-09T19:00:00",
  "subscribed_at": "2025-09-09T19:00:00",
  "verified_at": "2025-09-09T19:05:00",
  "unsubscribed_at": "2025-09-09T20:00:00"
}
```

#### Error Responses

- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Subscriber with email 'example@example.com' not found"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 4. Get All Subscribers (Admin Only)

Retrieves a list of all subscribers with optional pagination and search.

- **URL**: `/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Permissions**: Admin
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum number of records to return (default: 100, max: 100)
  - `search`: Search term for subscriber email

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "items": [
    {
      "id": 1,
      "email": "example@example.com",
      "is_active": true,
      "is_verified": true,
      "verification_token": null,
      "created_at": "2025-09-09T19:00:00",
      "subscribed_at": "2025-09-09T19:00:00",
      "verified_at": "2025-09-09T19:05:00",
      "unsubscribed_at": null
    }
  ],
  "total": 1
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 5. Get Subscriber by ID (Admin Only)

Retrieves a specific subscriber by ID.

- **URL**: `/{subscriber_id}`
- **Method**: `GET`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `subscriber_id`: ID of the subscriber to retrieve

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "email": "example@example.com",
  "is_active": true,
  "is_verified": true,
  "verification_token": null,
  "created_at": "2025-09-09T19:00:00",
  "subscribed_at": "2025-09-09T19:00:00",
  "verified_at": "2025-09-09T19:05:00",
  "unsubscribed_at": null
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Subscriber with ID {subscriber_id} not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 6. Update Subscriber (Admin Only)

Updates a subscriber's information.

- **URL**: `/{subscriber_id}`
- **Method**: `PATCH`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `subscriber_id`: ID of the subscriber to update

#### Request Body

```json
{
  "is_active": false
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "email": "example@example.com",
  "is_active": false,
  "is_verified": true,
  "verification_token": null,
  "created_at": "2025-09-09T19:00:00",
  "subscribed_at": "2025-09-09T19:00:00",
  "verified_at": "2025-09-09T19:05:00",
  "unsubscribed_at": "2025-09-09T20:00:00"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Subscriber with ID {subscriber_id} not found"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 7. Delete Subscriber (Admin Only)

Deletes a subscriber.

- **URL**: `/{subscriber_id}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `subscriber_id`: ID of the subscriber to delete

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "message": "Subscriber with ID {subscriber_id} deleted successfully"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Subscriber with ID {subscriber_id} not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

## Data Models

### Subscriber

```json
{
  "id": 1,
  "email": "example@example.com",
  "is_active": true,
  "is_verified": true,
  "verification_token": null,
  "created_at": "2025-09-09T19:00:00",
  "subscribed_at": "2025-09-09T19:00:00",
  "verified_at": "2025-09-09T19:05:00",
  "unsubscribed_at": null
}
```

## Dependencies

### get_admin_user

This dependency function ensures that only users with the admin role can access the protected endpoints. It is used in the following endpoints:

- GET `/` (Get all subscribers)
- GET `/{subscriber_id}` (Get subscriber by ID)
- PATCH `/{subscriber_id}` (Update subscriber)
- DELETE `/{subscriber_id}` (Delete subscriber)

## Flow Diagrams

### Subscription Flow

```
User -> POST /api/v1/subscriber -> Create Subscriber -> Generate Verification Token -> Return Subscriber
User -> POST /api/v1/subscriber/verify -> Verify Subscriber -> Mark as Verified -> Return Subscriber
```

### Unsubscription Flow

```
User -> POST /api/v1/subscriber/unsubscribe -> Find Subscriber by Email -> Mark as Inactive -> Return Subscriber
```

### Admin Management Flow

```
Admin -> GET /api/v1/subscriber -> List All Subscribers
Admin -> GET /api/v1/subscriber/{id} -> Get Specific Subscriber
Admin -> PATCH /api/v1/subscriber/{id} -> Update Subscriber
Admin -> DELETE /api/v1/subscriber/{id} -> Delete Subscriber
```
