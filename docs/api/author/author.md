# Author API Documentation

## Overview

The Author API provides endpoints for managing author profiles in the blog system. It allows for creating, retrieving, updating, and deleting authors, as well as managing their social media links. The API includes both public endpoints and endpoints restricted to admin users or the authors themselves.

## Base URL

```
/api/v1/author
```

## Authentication

- Public endpoints: No authentication required
- Author endpoints: Requires author user authentication
- Admin endpoints: Requires admin user authentication

## Endpoints

### 1. Get All Authors

Retrieves a list of all authors with optional pagination and search.

- **URL**: `/`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum number of records to return (default: 100, max: 100)
  - `search`: Search term for author name or bio

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "items": [
    {
      "id": 1,
      "name": "John Doe",
      "slug": "john-doe",
      "bio": "Tech writer and AI researcher",
      "profile_image": "https://example.com/profile.jpg",
      "website": "https://johndoe.com",
      "social_media": {
        "twitter": "https://twitter.com/johndoe",
        "linkedin": "https://linkedin.com/in/johndoe"
      }
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

### 2. Create Author (Admin Only)

Creates a new author.

- **URL**: `/`
- **Method**: `POST`
- **Auth Required**: Yes
- **Permissions**: Admin

#### Request Body

```json
{
  "name": "Jane Smith",
  "bio": "Experienced tech writer and AI researcher",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://janesmith.com",
  "social_media": {
    "twitter": "https://twitter.com/janesmith",
    "linkedin": "https://linkedin.com/in/janesmith"
  }
}
```

#### Success Response

- **Code**: 201 CREATED
- **Content**:

```json
{
  "id": 2,
  "name": "Jane Smith",
  "slug": "jane-smith",
  "bio": "Experienced tech writer and AI researcher",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://janesmith.com",
  "social_media": {
    "twitter": "https://twitter.com/janesmith",
    "linkedin": "https://linkedin.com/in/janesmith"
  }
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "Author with name 'Jane Smith' already exists"}`
  - **Content**: `{"detail": "Author with slug 'jane-smith' already exists"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 3. Get Popular Authors

Retrieves a list of popular authors with their article counts.

- **URL**: `/popular`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **Query Parameters**:
  - `limit`: Maximum number of authors to return (default: 10, max: 50)

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "slug": "john-doe",
    "profile_image": "https://example.com/profile.jpg",
    "article_count": 15
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "slug": "jane-smith",
    "profile_image": "https://example.com/profile2.jpg",
    "article_count": 10
  }
]
```

#### Error Responses

- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 4. Get Author by Slug

Retrieves a specific author by their slug.

- **URL**: `/slug/{slug}`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **URL Parameters**:
  - `slug`: Slug of the author to retrieve

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "bio": "Tech writer and AI researcher",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://johndoe.com",
  "social_media": {
    "twitter": "https://twitter.com/johndoe",
    "linkedin": "https://linkedin.com/in/johndoe"
  }
}
```

#### Error Responses

- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Author with slug 'john-doe' not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 5. Get Author by ID

Retrieves a specific author by their ID.

- **URL**: `/{author_id}`
- **Method**: `GET`
- **Auth Required**: No
- **Permissions**: None
- **URL Parameters**:
  - `author_id`: ID of the author to retrieve

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "bio": "Tech writer and AI researcher",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://johndoe.com",
  "social_media": {
    "twitter": "https://twitter.com/johndoe",
    "linkedin": "https://linkedin.com/in/johndoe"
  }
}
```

#### Error Responses

- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Author with ID 1 not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 6. Get Own Author Profile (Author Only)

Allows authors to retrieve their own profile information.

- **URL**: `/me`
- **Method**: `GET`
- **Auth Required**: Yes
- **Permissions**: Author

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "bio": "Tech writer and AI researcher",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://johndoe.com",
  "social_media": {
    "twitter": "https://twitter.com/johndoe",
    "linkedin": "https://linkedin.com/in/johndoe"
  }
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "You don't have an author profile"}`
  - **Content**: `{"detail": "Author profile not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 7. Update Own Author Profile (Author Only)

Allows authors to update their own profile information.

- **URL**: `/me`
- **Method**: `PATCH`
- **Auth Required**: Yes
- **Permissions**: Author

#### Request Body

```json
{
  "bio": "Updated biography for my profile",
  "website": "https://mynewwebsite.com"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "bio": "Updated biography for my profile",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://mynewwebsite.com",
  "social_media": {
    "twitter": "https://twitter.com/johndoe",
    "linkedin": "https://linkedin.com/in/johndoe"
  }
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "You don't have an author profile"}`
  - **Content**: `{"detail": "Author profile not found"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 8. Add or Update Social Media Link (Author Only)

Allows authors to add or update social media links on their own profile.

- **URL**: `/me/social-media`
- **Method**: `POST`
- **Auth Required**: Yes
- **Permissions**: Author

#### Request Body

```json
{
  "platform": "instagram",
  "url": "https://instagram.com/johndoe"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "bio": "Tech writer and AI researcher",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://johndoe.com",
  "social_media": {
    "twitter": "https://twitter.com/johndoe",
    "linkedin": "https://linkedin.com/in/johndoe",
    "instagram": "https://instagram.com/johndoe"
  }
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "You don't have an author profile"}`
  - **Content**: `{"detail": "Author profile not found"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 9. Delete Social Media Link (Author Only)

Allows authors to delete social media links from their own profile.

- **URL**: `/me/social-media/{platform}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Permissions**: Author
- **URL Parameters**:
  - `platform`: Platform name (e.g., twitter, linkedin)

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "bio": "Tech writer and AI researcher",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://johndoe.com",
  "social_media": {
    "linkedin": "https://linkedin.com/in/johndoe"
  }
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "You don't have an author profile"}`
  - **Content**: `{"detail": "Author profile not found"}`
  - **Content**: `{"detail": "Social media platform 'twitter' not found for author"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 10. Update Author (Admin Only)

Updates an existing author with a complete replacement (PUT).

- **URL**: `/{author_id}`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `author_id`: ID of the author to update

#### Request Body

```json
{
  "name": "John Smith",
  "bio": "Updated biography",
  "profile_image": "https://example.com/new-profile.jpg",
  "website": "https://johnsmith.com",
  "social_media": {
    "twitter": "https://twitter.com/johnsmith",
    "github": "https://github.com/johnsmith"
  }
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "John Smith",
  "slug": "john-smith",
  "bio": "Updated biography",
  "profile_image": "https://example.com/new-profile.jpg",
  "website": "https://johnsmith.com",
  "social_media": {
    "twitter": "https://twitter.com/johnsmith",
    "github": "https://github.com/johnsmith"
  }
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Author with ID 1 not found"}`
- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "Author with name 'John Smith' already exists"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 11. Partially Update Author (Admin Only)

Partially updates an existing author (PATCH).

- **URL**: `/{author_id}`
- **Method**: `PATCH`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `author_id`: ID of the author to update

#### Request Body

```json
{
  "bio": "Updated biography"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "bio": "Updated biography",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://johndoe.com",
  "social_media": {
    "twitter": "https://twitter.com/johndoe",
    "linkedin": "https://linkedin.com/in/johndoe"
  }
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Author with ID 1 not found"}`
- **Code**: 409 CONFLICT
  - **Content**: `{"detail": "Author with name 'John Smith' already exists"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 12. Delete Author (Admin Only)

Deletes an author.

- **URL**: `/{author_id}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `author_id`: ID of the author to delete

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "message": "Author with ID 1 deleted successfully"
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Author with ID 1 not found"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 13. Add or Update Social Media Link (Admin Only)

Allows admins to add or update social media links for an author.

- **URL**: `/{author_id}/social-media`
- **Method**: `POST`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `author_id`: ID of the author to update

#### Request Body

```json
{
  "platform": "youtube",
  "url": "https://youtube.com/c/johndoe"
}
```

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "bio": "Tech writer and AI researcher",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://johndoe.com",
  "social_media": {
    "twitter": "https://twitter.com/johndoe",
    "linkedin": "https://linkedin.com/in/johndoe",
    "youtube": "https://youtube.com/c/johndoe"
  }
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Author with ID 1 not found"}`
- **Code**: 422 UNPROCESSABLE ENTITY
  - **Content**: Validation error details
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

### 14. Delete Social Media Link (Admin Only)

Allows admins to delete social media links for an author.

- **URL**: `/{author_id}/social-media/{platform}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Permissions**: Admin
- **URL Parameters**:
  - `author_id`: ID of the author to update
  - `platform`: Platform name (e.g., twitter, linkedin)

#### Success Response

- **Code**: 200 OK
- **Content**:

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "bio": "Tech writer and AI researcher",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://johndoe.com",
  "social_media": {
    "linkedin": "https://linkedin.com/in/johndoe"
  }
}
```

#### Error Responses

- **Code**: 401 UNAUTHORIZED
  - **Content**: `{"detail": "Not authenticated"}`
- **Code**: 403 FORBIDDEN
  - **Content**: `{"detail": "Not authorized"}`
- **Code**: 404 NOT FOUND
  - **Content**: `{"detail": "Author with ID 1 not found"}`
  - **Content**: `{"detail": "Social media platform 'twitter' not found for author"}`
- **Code**: 500 INTERNAL SERVER ERROR
  - **Content**: `{"detail": "An unexpected error occurred"}`
- **Code**: 503 SERVICE UNAVAILABLE
  - **Content**: `{"detail": "Database error occurred"}`

## Data Models

### Author Response

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "bio": "Tech writer and AI researcher",
  "profile_image": "https://example.com/profile.jpg",
  "website": "https://johndoe.com",
  "social_media": {
    "twitter": "https://twitter.com/johndoe",
    "linkedin": "https://linkedin.com/in/johndoe"
  }
}
```

### Author List Response

```json
{
  "items": [
    {
      "id": 1,
      "name": "John Doe",
      "slug": "john-doe",
      "bio": "Tech writer and AI researcher",
      "profile_image": "https://example.com/profile.jpg",
      "website": "https://johndoe.com",
      "social_media": {
        "twitter": "https://twitter.com/johndoe",
        "linkedin": "https://linkedin.com/in/johndoe"
      }
    }
  ],
  "total": 1
}
```

### Author Article Count

```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "profile_image": "https://example.com/profile.jpg",
  "article_count": 15
}
```

### Social Media Update

```json
{
  "platform": "instagram",
  "url": "https://instagram.com/johndoe"
}
```

## Dependencies

### get_admin_user

This dependency function ensures that only users with the admin role can access the protected endpoints. It is used in the following endpoints:

- POST `/` (Create a new author)
- PUT `/{author_id}` (Update an author)
- PATCH `/{author_id}` (Partially update an author)
- DELETE `/{author_id}` (Delete an author)
- POST `/{author_id}/social-media` (Add or update social media link)
- DELETE `/{author_id}/social-media/{platform}` (Delete social media link)

### get_author_user

This dependency function ensures that only users with the author role can access the protected endpoints. It is used in the following endpoints:

- GET `/me` (Get author's own profile)
- PATCH `/me` (Update author's own profile)
- POST `/me/social-media` (Add or update social media link)
- DELETE `/me/social-media/{platform}` (Delete social media link)

## Flow Diagrams

### Author Creation Flow

```
Admin -> POST /api/v1/author -> Create Author -> Generate Slug -> Return Author
```

### Author Self-Management Flow

```
Author -> GET /api/v1/author/me -> Get Own Profile
Author -> PATCH /api/v1/author/me -> Update Own Profile
Author -> POST /api/v1/author/me/social-media -> Add/Update Social Media
Author -> DELETE /api/v1/author/me/social-media/{platform} -> Delete Social Media
```

### Admin Author Management Flow

```
Admin -> PUT /api/v1/author/{id} -> Update Author
Admin -> PATCH /api/v1/author/{id} -> Partially Update Author
Admin -> DELETE /api/v1/author/{id} -> Delete Author
Admin -> POST /api/v1/author/{id}/social-media -> Add/Update Social Media
Admin -> DELETE /api/v1/author/{id}/social-media/{platform} -> Delete Social Media
```

### Public Author Access Flow

```
User -> GET /api/v1/author -> List All Authors
User -> GET /api/v1/author/popular -> Get Popular Authors
User -> GET /api/v1/author/slug/{slug} -> Get Author by Slug
User -> GET /api/v1/author/{id} -> Get Author by ID
```
