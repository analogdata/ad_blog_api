# Tag API Documentation

## Overview

The Tag API provides endpoints for managing blog tags. It allows for creating, retrieving, updating, and deleting tags. The API includes both public endpoints and endpoints restricted to admin users.

## Base URL

```
/api/v1/tag
```

## Authentication

- Public endpoints: No authentication required
- Admin endpoints: Requires admin user authentication

## Endpoints

### 1. Get All Tags

Retrieves a list of all tags with optional pagination and search.

- **URL**: `/`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum number of records to return (default: 100, max: 100)
  - `search`: Search term for tag name or description

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "items": [
    {
      "id": 1,
      "name": "JavaScript",
      "slug": "javascript",
      "description": "Articles about JavaScript programming"
    }
  ],
  "total": 1
}
```

#### Error Responses

- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 2. Create Tag (Admin Only)

Creates a new tag.

- **URL**: `/`
- **Method**: `POST`
- **Auth Required**: Yes
- **Permissions**: Admin

#### Request Body

```json
{
  "name": "Python",
  "description": "Articles about Python programming"
}
```

#### Success Response

- **Code**: 201 CREATED
- **Content**:

```json
{
  "id": 2,
  "name": "Python",
  "slug": "python",
  "description": "Articles about Python programming"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "Tag with name 'Python' already exists"}`
  - **Content**: `{"detail": "Tag with slug 'python' already exists"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 3. Get Popular Tags

Retrieves a list of popular tags with their article counts.

- **URL**: `/popular`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **Query Parameters**:
  - `limit`: Maximum number of tags to return (default: 10, max: 50)

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
[
  {
    "id": 1,
    "name": "JavaScript",
    "slug": "javascript",
    "article_count": 15
  },
  {
    "id": 2,
    "name": "Python",
    "slug": "python",
    "article_count": 10
  }
]
```

#### Error Responses

- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 4. Get Tag by Slug

Retrieves a specific tag by its slug.

- **URL**: `/slug/{slug}`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **URL Parameters**:
  - `slug`: Slug of the tag to retrieve

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "JavaScript",
  "slug": "javascript",
  "description": "Articles about JavaScript programming"
}
```

#### Error Responses

- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Tag with slug 'javascript' not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 5. Get Tag by ID

Retrieves a specific tag by its ID.

- **URL**: `/{tag_id}`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **URL Parameters**:
  - `tag_id`: ID of the tag to retrieve

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "JavaScript",
  "slug": "javascript",
  "description": "Articles about JavaScript programming"
}
```

#### Error Responses

- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Tag with ID 1 not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 6. Update Tag (Admin Only)

Updates an existing tag with a complete replacement (PUT).

- **URL**: `/{tag_id}`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `tag_id`: ID of the tag to update

#### Request Body

```json
{
  "name": "JavaScript ES6",
  "description": "Articles about modern JavaScript programming"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "JavaScript ES6",
  "slug": "javascript-es6",
  "description": "Articles about modern JavaScript programming"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Tag with ID 1 not found"}`
- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "Tag with name 'JavaScript ES6' already exists"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 7. Partially Update Tag (Admin Only)

Partially updates an existing tag (PATCH).

- **URL**: `/{tag_id}`
- **Method**: `PATCH`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `tag_id`: ID of the tag to update

#### Request Body

```json
{
  "description": "Updated description for JavaScript tag"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "JavaScript",
  "slug": "javascript",
  "description": "Updated description for JavaScript tag"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Tag with ID 1 not found"}`
- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "Tag with name 'JavaScript' already exists"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 8. Delete Tag (Admin Only)

Deletes a tag.

- **URL**: `/{tag_id}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `tag_id`: ID of the tag to delete

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "message": "Tag with ID 1 deleted successfully"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Tag with ID 1 not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

## Data Models

### Tag Response

```json
{
  "id": 1,
  "name": "JavaScript",
  "slug": "javascript",
  "description": "Articles about JavaScript programming"
}
```

### Tag List Response

```json
{
  "items": [
    {
      "id": 1,
      "name": "JavaScript",
      "slug": "javascript",
      "description": "Articles about JavaScript programming"
    }
  ],
  "total": 1
}
```

### Tag Article Count

```json
{
  "id": 1,
  "name": "JavaScript",
  "slug": "javascript",
  "article_count": 15
}
```

## Dependencies

### AdminUser

This dependency function ensures that only users with the admin role can access the protected endpoints. It is used in the following endpoints:

- POST `/` (Create a new tag)
- PUT `/{tag_id}` (Update a tag)
- PATCH `/{tag_id}` (Partially update a tag)
- DELETE `/{tag_id}` (Delete a tag)

## Flow Diagrams

### Tag Creation Flow

```
Admin -> POST /api/v1/tag -> Create Tag -> Generate Slug -> Return Tag
```

### Tag Update Flow

```
Admin -> PUT /api/v1/tag/{id} -> Update Tag -> Update Slug if Name Changed -> Return Tag
Admin -> PATCH /api/v1/tag/{id} -> Partially Update Tag -> Update Slug if Name Changed -> Return Tag
```

### Tag Deletion Flow

```
Admin -> DELETE /api/v1/tag/{id} -> Delete Tag -> Return Success Message
```

### Public Tag Access Flow

```
User -> GET /api/v1/tag -> List All Tags
User -> GET /api/v1/tag/popular -> Get Popular Tags
User -> GET /api/v1/tag/slug/{slug} -> Get Tag by Slug
User -> GET /api/v1/tag/{id} -> Get Tag by ID
```
