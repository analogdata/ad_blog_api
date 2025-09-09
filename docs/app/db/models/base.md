# Base Models Documentation

The base module provides essential mixins that are used across the blog API's data models. These mixins provide reusable functionality for common tasks such as timestamp tracking, URL validation, soft deletion, and more.

## Mixins Overview

| Mixin | Purpose | Key Features |
|-------|---------|-------------|
| `URLValidationMixin` | Provides URL validation functionality | URL validation and normalization |
| `TimestampMixin` | Adds created_at and updated_at fields | Automatic timestamp generation |
| `SoftDeleteMixin` | Enables soft deletion of records | Marks records as deleted without removing from database |
| `AuditMixin` | Tracks who created and modified records | Links to user records for accountability |
| `HttpUrlFieldMixin` | Handles HttpUrl fields in SQLModel | Validates URL fields defined in url_fields |
| `SlugGeneratorMixin` | Generates slugs from a specified field | Creates URL-friendly slugs automatically |

## Detailed Description

### URLValidationMixin

This mixin provides methods for validating and normalizing URLs.

**Methods:**
- `validate_url(url: str) -> str`: Validates a URL and adds https:// prefix if not present
- `validate_url_dict(url_dict: Dict[str, str]) -> Dict[str, str]`: Validates all URLs in a dictionary

**Usage:**
```python
class MyModel(URLValidationMixin, SQLModel):
    website: str
    
    def save(self):
        self.website = self.validate_url(self.website)
        # Save to database
```

### TimestampMixin

Adds `created_at` and `updated_at` fields to models, automatically setting them to the current UTC time.

**Fields:**
- `created_at`: DateTime when the record was created
- `updated_at`: DateTime when the record was last updated

**Usage:**
```python
class MyModel(TimestampMixin, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    # created_at and updated_at are automatically added
```

### SoftDeleteMixin

Enables soft deletion of records, marking them as deleted without removing them from the database.

**Fields:**
- `is_deleted`: Boolean flag indicating if the record is deleted
- `deleted_at`: DateTime when the record was deleted

**Methods:**
- `soft_delete()`: Marks the record as deleted and sets deleted_at to current time
- `restore()`: Restores a soft-deleted record

**Usage:**
```python
# Instead of permanently deleting
db.delete(record)

# Use soft delete
record.soft_delete()
db.add(record)
db.commit()
```

### AuditMixin

Tracks who created and modified records by storing user IDs.

**Fields:**
- `created_by_id`: ID of the user who created the record
- `updated_by_id`: ID of the user who last updated the record

**Methods:**
- `set_created_by(user_id: int)`: Sets the user who created the record
- `set_updated_by(user_id: int)`: Sets the user who last updated the record

**Usage:**
```python
record = MyModel(name="Example")
record.set_created_by(current_user.id)
db.add(record)
db.commit()
```

### HttpUrlFieldMixin

Handles URL fields in SQLModel classes, ensuring they are properly validated and stored as strings in the database.

**Class Variables:**
- `url_fields`: List of field names that should be treated as URLs

**Methods:**
- `validate_url_fields()`: Validates all URL fields defined in url_fields and ensures they are stored as strings

**Features:**
- Automatically converts HttpUrl objects to strings before storage
- Validates URL format using Pydantic's HttpUrl validator
- Handles both string and object representations of URLs

**Usage:**
```python
class MyModel(HttpUrlFieldMixin, SQLModel, table=True):
    url_fields: ClassVar[list[str]] = ["website", "image_url"]
    
    id: int = Field(default=None, primary_key=True)
    website: str
    image_url: str
```

### SlugGeneratorMixin

Generates URL-friendly slugs from a specified field.

**Class Variables:**
- `slug_source_field`: Name of the field to use as source for the slug

**Methods:**
- `generate_slug(text: str) -> str`: Generates a URL-friendly slug from text
- `generate_slug_if_missing()`: Generates slug from source field if slug is missing

**Usage:**
```python
class MyModel(SlugGeneratorMixin, SQLModel, table=True):
    slug_source_field: ClassVar[str] = "title"
    
    id: int = Field(default=None, primary_key=True)
    title: str
    slug: str
```

## Flow and Usage Patterns

These mixins are designed to be used together to provide a comprehensive set of features for data models. A typical pattern is:

```python
class MyModel(
    TimestampMixin,
    SoftDeleteMixin,
    URLValidationMixin,
    AuditMixin,
    HttpUrlFieldMixin,
    SlugGeneratorMixin,
    SQLModel,
    table=True
):
    # Model-specific fields and methods
    pass
```

This approach allows for consistent behavior across models and reduces code duplication.
