# Category Model Documentation

The `Category` model represents content classification in the blog API, organizing articles into logical groups.

## Model Overview

The `Category` model inherits from multiple mixins to provide a rich set of features:
- `TimestampMixin`: Tracks creation and update times
- `HttpUrlFieldMixin`: Validates URL fields
- `SlugGeneratorMixin`: Automatically generates URL-friendly slugs

## Fields and Properties

| Field | Type | Description | Indexes |
|-------|------|-------------|---------|
| `id` | int | Primary key | Primary key |
| `name` | str | Category name | Unique, Indexed |
| `description` | Optional[str] | Category description | - |
| `slug` | str | URL-friendly version of name | Unique, Indexed |
| `category_icon` | Optional[str] | URL to category icon | URL validation |
| `category_image` | Optional[str] | URL to category image | URL validation |
| `created_at` | datetime | When the category was created (from TimestampMixin) | - |
| `updated_at` | datetime | When the category was last updated (from TimestampMixin) | - |

## Class Variables

| Variable | Type | Description |
|----------|------|-------------|
| `url_fields` | ClassVar[list[str]] | List of fields to validate as URLs: "category_icon", "category_image" |
| `slug_source_field` | ClassVar[str] | Field used to generate slug: "name" |

## Relationships

| Relationship | Related Model | Type | Description |
|--------------|--------------|------|-------------|
| `articles` | Article | One-to-Many | Articles belonging to this category |

## Usage Flow

### Category Creation

```python
# Create a new category
category = Category(
    name="Technology",
    description="Articles about software, hardware, and tech trends",
    category_icon="https://example.com/icons/tech.svg",
    category_image="https://example.com/images/tech-banner.jpg"
)
db.add(category)
db.commit()
```

### Assigning Articles to Categories

```python
# Create an article with a category
article = Article(
    title="Introduction to FastAPI",
    content="FastAPI is a modern web framework...",
    category_id=category.id
)
db.add(article)
db.commit()

# Update an article's category
article.category_id = new_category.id
db.add(article)
db.commit()

# Using the relationship
article.category = category
db.add(article)
db.commit()
```

### Retrieving Articles by Category

```python
# Get all articles in a category
articles = db.query(Article).filter(Article.category_id == category.id).all()

# Using the relationship
articles = category.articles

# Get published articles in a category
from app.db.models.article import Status
published_articles = db.query(Article).filter(
    Article.category_id == category.id,
    Article.status == Status.PUBLISHED
).all()
```

## Design Considerations

1. **Name Uniqueness**: Category names must be unique, which is enforced by a database constraint. This ensures consistent classification and prevents confusion.

2. **Slug Generation**: The `SlugGeneratorMixin` automatically creates a URL-friendly slug from the category name, which can be used in URLs (e.g., `/categories/technology`).

3. **Visual Elements**: The model includes fields for both an icon (typically small, for use in navigation) and an image (typically larger, for use in headers or category pages).

4. **URL Validation**: The `HttpUrlFieldMixin` ensures that all URLs (category_icon, category_image) are properly formatted.

## Database Impact

- Unique indexes on `name` and `slug` ensure uniqueness and optimize lookups by these fields.
- The relationship with articles creates a one-to-many association, where each article belongs to at most one category.

## Related Models

- `Article`: Articles belonging to the category

## Hierarchical Categories

The current implementation uses a flat category structure. If hierarchical categories (categories with subcategories) are needed, the model could be extended with:

```python
# Add to Category model
parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")
parent: Optional["Category"] = Relationship(back_populates="children", foreign_keys=[parent_id])
children: List["Category"] = Relationship(back_populates="parent", foreign_keys=[parent_id])
```

This would allow for creating category trees, enabling more complex content organization.
