# User Model Documentation

The `User` model implements authentication, authorization, and user management in the blog API, serving as the foundation for access control and content ownership.

## Model Overview

The `User` model represents user accounts in the system, with support for authentication, role-based access control, and profile management.

## Fields and Properties

| Field | Type | Description | Indexes |
|-------|------|-------------|---------|
| `id` | int | Primary key | Primary key |
| `email` | str | User's email address | Unique, Indexed |
| `password` | str | Bcrypt-hashed password | - |
| `first_name` | Optional[str] | User's first name | - |
| `last_name` | Optional[str] | User's last name | - |
| `role` | UserRole | User's role (admin or author) | - |
| `is_active` | bool | Whether the account is active | - |
| `is_verified` | bool | Whether the email has been verified | - |
| `verification_token` | Optional[str] | Token for email verification | - |
| `verified_at` | Optional[datetime] | When the email was verified | - |
| `last_login` | Optional[datetime] | When the user last logged in | - |
| `profile_image` | Optional[str] | URL to user's profile image | - |
| `preferences` | Optional[Dict[str, Any]] | User preferences | JSON column |
| `created_at` | datetime | When the user was created | - |
| `updated_at` | datetime | When the user was last updated | - |
| `author_id` | Optional[int] | Foreign key to authors table | - |

## Enumerations

### UserRole Enum

The `UserRole` enum defines the available roles in the system:

| Role | Description |
|------|-------------|
| `ADMIN` | Administrator with full system access |
| `AUTHOR` | Content creator with limited permissions |

## Relationships

| Relationship | Related Model | Type | Description |
|--------------|--------------|------|-------------|
| `permissions` | Permission | One-to-Many | Permissions assigned to this user |
| `author` | Author | One-to-One | Author profile associated with this user |

## Methods

### Authentication and Password Management

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `hash_password()` (staticmethod) | str | str | Hashes a password using bcrypt |
| `verify_password(password)` | str | bool | Checks if provided password matches stored hash |

### Account Management

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `generate_verification_token()` | None | str | Generates a verification token for email verification |
| `verify_user()` | None | None | Marks user as verified |
| `update_last_login()` | None | None | Updates the last login timestamp |

### Authorization and Access Control

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `has_permission(permission_name)` | str | bool | Checks if user has a specific permission |
| `is_admin()` | None | bool | Checks if user has admin role |
| `can_edit_article(article)` | Article | bool | Checks if user can edit the given article |

### Profile Management

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `get_full_name()` | None | str | Gets user's full name |
| `validate_email()` | None | User | Validates email format |

## Usage Flow

### User Registration

```python
# Create a new user (password is automatically hashed)
user = User(
    email="user@example.com",
    password="secure_password",  # Will be hashed automatically
    first_name="John",
    last_name="Doe",
    role=UserRole.AUTHOR
)

# Generate verification token
verification_token = user.generate_verification_token()
db.add(user)
db.commit()

# Send verification email (application logic)
send_verification_email(user.email, verification_token)
```

### Authentication

```python
# Find user by email
user = db.query(User).filter(User.email == email).first()

# Verify password
if user and user.verify_password(password):
    # Authentication successful
    user.update_last_login()
    db.add(user)
    db.commit()
    # Generate JWT or session token (application logic)
else:
    # Authentication failed
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

### Email Verification

```python
# When user clicks verification link
user = db.query(User).filter(
    User.verification_token == token
).first()

if user:
    user.verify_user()
    db.add(user)
    db.commit()
```

### Permission Checking

```python
# Check if user can perform an action
if user.has_permission("edit_any_article") or (
    user.has_permission("edit_own_article") and user.can_edit_article(article)
):
    # Allow editing
    pass
else:
    # Deny access
    raise HTTPException(status_code=403, detail="Permission denied")
```

### Author Association

```python
# Create author profile for user
author = Author(
    name=user.get_full_name(),
    bio="New author"
)
db.add(author)
db.commit()

# Link author to user
user.author_id = author.id
author.user = user
db.add(user)
db.add(author)
db.commit()
```

## Design Considerations

1. **Password Security**: Passwords are automatically hashed using bcrypt, a secure password-hashing function designed to be slow and resist brute-force attacks.

2. **Email Verification**: The model includes a verification flow to ensure email addresses are valid, reducing spam and improving security.

3. **Role-Based Access Control**: The combination of roles and permissions provides a flexible authorization system:
   - Roles (admin, author) provide broad access levels
   - Permissions provide fine-grained control over specific actions

4. **User Preferences**: The `preferences` JSON field allows storing user-specific settings without requiring schema changes.

5. **Author Association**: Users can be associated with author profiles, separating authentication/authorization concerns from content creation.

## Database Impact

- The unique index on `email` ensures each email can only have one account and optimizes lookups during authentication.
- The `permissions` relationship may result in multiple database records per user, depending on the number of permissions assigned.

## Related Models

- `Permission`: Defines what actions the user can perform
- `Author`: Author profile associated with the user

## Authentication Flow

The typical authentication flow using this model is:

1. User registers with email and password
2. Password is automatically hashed before storage
3. Verification email is sent with a token
4. User verifies email by clicking the link
5. User logs in with email and password
6. Application checks password hash and grants access if valid

## Authorization Flow

The authorization flow depends on both roles and permissions:

1. For role-based checks: `user.role == UserRole.ADMIN`
2. For permission-based checks: `user.has_permission("permission_name")`
3. For content ownership checks: `user.can_edit_article(article)`

This multi-layered approach provides flexible and secure access control.
