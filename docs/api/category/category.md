# Category API Documentation

## Overview

The Category API provides endpoints for managing blog categories. It allows for creating, retrieving, updating, and deleting categories. The API includes both public endpoints and endpoints restricted to admin users.

## Base URL

```
/api/v1/category
```

## Authentication

- Public endpoints: No authentication required
- Admin endpoints: Requires admin user authentication

## Endpoints

### 1. Get All Categories

Retrieves a list of all categories with optional pagination and search.

- **URL**: `/`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum number of records to return (default: 100, max: 100)
  - `search`: Search term for category name or description

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "items": [
    {
      "id": 1,
      "name": "Technology",
      "slug": "technology",
      "description": "Articles about technology",
      "image_url": "https://example.com/images/technology.jpg"
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

### 2. Create Category (Admin Only)

Creates a new category.

- **URL**: `/`
- **Method**: `POST`
- **Auth Required**: Yes
- **Permissions**: Admin

#### Request Body

```json
{
  "name": "Science",
  "description": "Articles about scientific discoveries",
  "image_url": "https://example.com/images/science.jpg"
}
```

#### Success Response

- **Code**: 201 CREATED
- **Content**:

```json
{
  "id": 2,
  "name": "Science",
  "slug": "science",
  "description": "Articles about scientific discoveries",
  "image_url": "https://example.com/images/science.jpg"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "Category with name 'Science' already exists"}`
  - **Content**: `{"detail": "Category with slug 'science' already exists"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 3. Get Popular Categories

Retrieves a list of popular categories with their article counts.

- **URL**: `/popular`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **Query Parameters**:
  - `limit`: Maximum number of categories to return (default: 10, max: 50)

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
[
  {
    "id": 1,
    "name": "Technology",
    "slug": "technology",
    "image_url": "https://example.com/images/technology.jpg",
    "article_count": 15
  },
  {
    "id": 2,
    "name": "Science",
    "slug": "science",
    "image_url": "https://example.com/images/science.jpg",
    "article_count": 10
  }
]
```

#### Error Responses

- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 4. Get Category by Slug

Retrieves a specific category by its slug.

- **URL**: `/slug/{slug}`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **URL Parameters**:
  - `slug`: Slug of the category to retrieve

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "Technology",
  "slug": "technology",
  "description": "Articles about technology",
  "image_url": "https://example.com/images/technology.jpg"
}
```

#### Error Responses

- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Category with slug 'technology' not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 5. Get Category by ID

Retrieves a specific category by its ID.

- **URL**: `/{category_id}`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **URL Parameters**:
  - `category_id`: ID of the category to retrieve

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "Technology",
  "slug": "technology",
  "description": "Articles about technology",
  "image_url": "https://example.com/images/technology.jpg"
}
```

#### Error Responses

- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Category with ID 1 not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 6. Update Category (Admin Only)

Updates an existing category with a complete replacement (PUT).

- **URL**: `/{category_id}`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `category_id`: ID of the category to update

#### Request Body

```json
{
  "name": "Technology & Innovation",
  "description": "Articles about technology and innovation",
  "image_url": "https://example.com/images/tech-innovation.jpg"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "Technology & Innovation",
  "slug": "technology-innovation",
  "description": "Articles about technology and innovation",
  "image_url": "https://example.com/images/tech-innovation.jpg"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Category with ID 1 not found"}`
- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "Category with name 'Technology & Innovation' already exists"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 7. Partially Update Category (Admin Only)

Partially updates an existing category (PATCH).

- **URL**: `/{category_id}`
- **Method**: `PATCH`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `category_id`: ID of the category to update

#### Request Body

```json
{
  "description": "Updated description for technology category"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "Technology",
  "slug": "technology",
  "description": "Updated description for technology category",
  "image_url": "https://example.com/images/technology.jpg"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Category with ID 1 not found"}`
- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "Category with name 'Technology' already exists"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 8. Delete Category (Admin Only)

Deletes a category.

- **URL**: `/{category_id}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `category_id`: ID of the category to delete

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "message": "Category with ID 1 deleted successfully"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Category with ID 1 not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

## Data Models

### Category Response

```json
{
  "id": 1,
  "name": "Technology",
  "slug": "technology",
  "description": "Articles about technology",
  "image_url": "https://example.com/images/technology.jpg"
}
```

### Category List Response

```json
{
  "items": [
    {
      "id": 1,
      "name": "Technology",
      "slug": "technology",
      "description": "Articles about technology",
      "image_url": "https://example.com/images/technology.jpg"
    }
  ],
  "total": 1
}
```

### Category Article Count

```json
{
  "id": 1,
  "name": "Technology",
  "slug": "technology",
  "image_url": "https://example.com/images/technology.jpg",
  "article_count": 15
}
```

## Dependencies

### AdminUser

This dependency function ensures that only users with the admin role can access the protected endpoints. It is used in the following endpoints:

- POST `/` (Create a new category)
- PUT `/{category_id}` (Update a category)
- PATCH `/{category_id}` (Partially update a category)
- DELETE `/{category_id}` (Delete a category)

## Flow Diagrams

### Category Creation Flow

```
Admin -> POST /api/v1/category -> Create Category -> Generate Slug -> Return Category
```

### Category Update Flow

```
Admin -> PUT /api/v1/category/{id} -> Update Category -> Update Slug if Name Changed -> Return Category
Admin -> PATCH /api/v1/category/{id} -> Partially Update Category -> Update Slug if Name Changed -> Return Category
```

### Category Deletion Flow

```
Admin -> DELETE /api/v1/category/{id} -> Delete Category -> Return Success Message
```

### Public Category Access Flow

```
User -> GET /api/v1/category -> List All Categories
User -> GET /api/v1/category/popular -> Get Popular Categories
User -> GET /api/v1/category/slug/{slug} -> Get Category by Slug
User -> GET /api/v1/category/{id} -> Get Category by ID
```
