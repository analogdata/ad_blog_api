# Permission Model Documentation

The `Permission` model implements role-based access control in the blog API, defining what actions users are authorized to perform.

## Model Overview

The `Permission` model defines granular permissions that can be assigned to users, controlling their access to various features and operations within the blog system.

## Fields and Properties

| Field | Type | Description | Indexes |
|-------|------|-------------|---------|
| `id` | int | Primary key | Primary key |
| `name` | PermissionName | Permission name (enum) | Indexed |
| `description` | Optional[str] | Description of the permission | - |
| `user_id` | int | Foreign key to users table | - |
| `created_at` | datetime | When the permission was created | - |
| `updated_at` | datetime | When the permission was last updated | - |

## Enumerations

### PermissionName Enum

The `PermissionName` enum defines all available permissions in the system:

| Permission | Description |
|------------|-------------|
| **Article Permissions** |
| `CREATE_ARTICLE` | Ability to create new articles |
| `EDIT_OWN_ARTICLE` | Ability to edit articles created by the user |
| `EDIT_ANY_ARTICLE` | Ability to edit any article regardless of author |
| `DELETE_OWN_ARTICLE` | Ability to delete articles created by the user |
| `DELETE_ANY_ARTICLE` | Ability to delete any article regardless of author |
| `PUBLISH_ARTICLE` | Ability to change article status to published |
| `SCHEDULE_ARTICLE` | Ability to schedule articles for future publication |
| `FEATURE_ARTICLE` | Ability to mark articles as featured |
| **User Management** |
| `CREATE_USER` | Ability to create new user accounts |
| `EDIT_OWN_PROFILE` | Ability to edit own user profile |
| `EDIT_ANY_PROFILE` | Ability to edit any user profile |
| `DELETE_USER` | Ability to delete user accounts |
| **Categories and Tags** |
| `MANAGE_CATEGORIES` | Ability to create, edit, and delete categories |
| `MANAGE_TAGS` | Ability to create, edit, and delete tags |
| **Analytics** |
| `VIEW_OWN_ANALYTICS` | Ability to view analytics for own content |
| `VIEW_ALL_ANALYTICS` | Ability to view analytics for all content |

## Relationships

| Relationship | Related Model | Type | Description |
|--------------|--------------|------|-------------|
| `user` | User | Many-to-One | User who has this permission |

## Usage Flow

### Assigning Permissions to Users

```python
from app.db.models.permission import Permission, PermissionName
from app.db.models.user import User

# Create a new permission for a user
permission = Permission(
    name=PermissionName.CREATE_ARTICLE,
    description="Allow user to create new articles",
    user_id=user.id
)
db.add(permission)
db.commit()

# Assign multiple permissions
permissions = [
    Permission(name=PermissionName.CREATE_ARTICLE, user_id=user.id),
    Permission(name=PermissionName.EDIT_OWN_ARTICLE, user_id=user.id),
    Permission(name=PermissionName.PUBLISH_ARTICLE, user_id=user.id)
]
db.add_all(permissions)
db.commit()
```

### Checking User Permissions

```python
# Using the User model's helper method
if user.has_permission(PermissionName.EDIT_ANY_ARTICLE):
    # Allow editing any article
    pass

# Direct query
has_permission = db.query(Permission).filter(
    Permission.user_id == user.id,
    Permission.name == PermissionName.PUBLISH_ARTICLE
).first() is not None
```

### Role-Based Permission Assignment

While not explicitly modeled, common permission sets can be assigned based on user roles:

```python
def assign_author_permissions(user_id):
    """Assign standard permissions for authors"""
    permissions = [
        Permission(name=PermissionName.CREATE_ARTICLE, user_id=user_id),
        Permission(name=PermissionName.EDIT_OWN_ARTICLE, user_id=user_id),
        Permission(name=PermissionName.DELETE_OWN_ARTICLE, user_id=user_id),
        Permission(name=PermissionName.EDIT_OWN_PROFILE, user_id=user_id),
        Permission(name=PermissionName.VIEW_OWN_ANALYTICS, user_id=user_id)
    ]
    db.add_all(permissions)
    db.commit()
```

## Design Considerations

1. **Enum-Based Permissions**: Using an enum for permission names ensures consistency and prevents typos when checking permissions.

2. **Granular Permissions**: The system uses fine-grained permissions rather than role-based access control, allowing for more flexible permission assignments.

3. **Direct User Association**: Permissions are directly associated with users rather than using a role intermediary, which simplifies queries but may require more database records.

4. **Timestamps**: Creation and update timestamps help track when permissions were granted.

## Database Impact

- The index on `name` optimizes permission lookups by name.
- Each permission is a separate record, which may lead to many records for users with multiple permissions.

## Related Models

- `User`: The user who has the permission

## Authorization Flow

The typical authorization flow using this model is:

1. User attempts an action (e.g., editing an article)
2. Application checks if the user has the required permission:
   - For own content: `EDIT_OWN_ARTICLE` and verify ownership
   - For any content: `EDIT_ANY_ARTICLE`
3. If the permission check passes, allow the action; otherwise, deny it

This granular permission system allows for flexible access control policies while maintaining security.
