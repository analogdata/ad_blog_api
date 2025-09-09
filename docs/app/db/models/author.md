# Author Model Documentation

The `Author` model represents content creators in the blog API, providing profile information and linking to their published articles.

## Model Overview

The `Author` model inherits from multiple mixins to provide a rich set of features:
- `URLValidationMixin`: Validates URL fields
- `HttpUrlFieldMixin`: Validates URL fields and ensures they are stored as strings
- `SlugGeneratorMixin`: Automatically generates URL-friendly slugs

The model also implements timestamp fields directly with database-driven defaults:

## Fields and Properties

| Field | Type | Description | Indexes |
|-------|------|-------------|---------|
| `id` | int | Primary key | Primary key |
| `name` | str | Author's name | Unique, Indexed |
| `bio` | Optional[str] | Author's biography | - |
| `slug` | str | URL-friendly version of name | Unique, Indexed |
| `profile_image` | Optional[str] | URL to author's profile image | URL validation |
| `website` | Optional[str] | URL to author's personal website | URL validation |
| `social_media` | Optional[Dict[str, str]] | Dictionary of social media platforms and URLs | JSON column |
| `created_at` | datetime | When the author was created (database-driven) | - |
| `updated_at` | datetime | When the author was last updated (database-driven) | - |

## Class Variables

| Variable | Type | Description |
|----------|------|-------------|
| `url_fields` | ClassVar[list[str]] | List of fields to validate as URLs: "profile_image", "website" |
| `slug_source_field` | ClassVar[str] | Field used to generate slug: "name" |

## Relationships

| Relationship | Related Model | Type | Description |
|--------------|--------------|------|-------------|
| `articles` | Article | One-to-Many | Articles written by this author |
| `user` | User | One-to-One | User account associated with this author |

## Methods

### Social Media Management

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `validate_social_media()` | None | Author | Validates all social media URLs |
| `add_social_media(platform, url)` | str, str | None | Adds or updates a social media profile |
| `remove_social_media(platform)` | str | bool | Removes a social media profile, returns True if successful |
| `get_social_media_platforms()` | None | List[str] | Returns a list of all social media platforms for this author |

## Usage Flow

### Author Creation

```python
# Create a new author
author = Author(
    name="Jane Smith",
    bio="Technology writer with 10 years of experience",
    profile_image="https://example.com/images/jane-smith.jpg",
    website="https://janesmith.com"
)
db.add(author)
db.commit()
```

### Managing Social Media Profiles

```python
# Add social media profiles
author.add_social_media("twitter", "https://twitter.com/janesmith")
author.add_social_media("linkedin", "https://linkedin.com/in/janesmith")
db.add(author)
db.commit()

# Remove a social media profile
author.remove_social_media("twitter")
db.add(author)
db.commit()

# Get all platforms
platforms = author.get_social_media_platforms()
```

### Linking with User Account

```python
# Link author to user account
user = User(email="jane@example.com", password="secure_password")
db.add(user)
db.commit()

author.user = user
db.add(author)
db.commit()
```

### Retrieving Author's Articles

```python
# Get all articles by this author
articles = db.query(Article).filter(Article.author_id == author.id).all()

# Using the relationship
articles = author.articles
```

## Design Considerations

1. **Name Uniqueness**: Author names must be unique, which is enforced by a database constraint. This ensures consistent attribution and prevents confusion.

2. **Slug Generation**: The `SlugGeneratorMixin` automatically creates a URL-friendly slug from the author's name, which can be used in URLs (e.g., `/authors/jane-smith`).

3. **Social Media as JSON**: Social media profiles are stored as a JSON dictionary, allowing flexible storage of various platforms without requiring schema changes for each new platform.

4. **URL Validation**: The `URLValidationMixin` and `HttpUrlFieldMixin` ensure that all URLs (profile image, website, social media) are properly formatted.

5. **User Association**: An author can be associated with a user account, enabling authentication and authorization for content management.

## Database Impact

- Unique indexes on `name` and `slug` ensure uniqueness and optimize lookups by these fields.
- The `social_media` field uses a JSON column type, which provides flexibility but may impact query performance if filtering on specific social media platforms is needed.

## Related Models

- `Article`: Articles written by the author
- `User`: User account associated with the author
