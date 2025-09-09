# ArticleVersion Model Documentation

The `ArticleVersion` model implements version control for articles in the blog API, allowing tracking of changes and restoration of previous versions.

## Model Overview

`ArticleVersion` inherits from `AuditMixin` to provide audit capabilities and implements timestamp fields directly with database-driven defaults. It stores snapshots of article content at different points in time, enabling a comprehensive revision history.

## Fields and Properties

| Field | Type | Description | Indexes |
|-------|------|-------------|---------|
| `id` | int | Primary key | Primary key |
| `article_id` | int | Foreign key to articles table | Indexed |
| `version_number` | int | Sequential version number | Indexed |
| `title` | str | Article title at this version | - |
| `content` | Optional[str] | Article content at this version | - |
| `summary` | Optional[str] | Article summary at this version | - |
| `change_comment` | Optional[str] | Comment describing changes in this version | - |
| `created_at` | datetime | When this version was created (database-driven) | - |
| `updated_at` | datetime | When this version was last updated (database-driven) | - |
| `created_by_id` | Optional[int] | User who created this version (from AuditMixin) | - |
| `updated_by_id` | Optional[int] | User who last updated this version (from AuditMixin) | - |

## Relationships

| Relationship | Related Model | Type | Description |
|--------------|--------------|------|-------------|
| `article` | Article | Many-to-One | The article this version belongs to |

## Usage Flow

### Creating a New Version

When significant changes are made to an article, a new version can be created to preserve the previous state:

```python
# Using the Article model's helper method
version = article.create_version(
    user_id=current_user.id, 
    change_comment="Updated introduction and fixed typos"
)
db.add(version)
db.commit()

# Direct creation
from app.db.models.article_version import ArticleVersion

version = ArticleVersion(
    article_id=article.id,
    version_number=next_version_number,
    title=article.title,
    content=article.content,
    summary=article.summary,
    change_comment="Updated introduction and fixed typos",
    created_by_id=current_user.id
)
db.add(version)
db.commit()
```

### Viewing Version History

```python
# Using the Article model's helper method
history = article.get_version_history()

# Direct query
versions = db.query(ArticleVersion).filter(
    ArticleVersion.article_id == article.id
).order_by(ArticleVersion.version_number).all()
```

### Restoring a Previous Version

```python
# Using the Article model's helper method
article.restore_version(version_number=3)
db.add(article)
db.commit()

# Direct implementation
version = db.query(ArticleVersion).filter(
    ArticleVersion.article_id == article.id,
    ArticleVersion.version_number == 3
).first()

if version:
    article.title = version.title
    article.content = version.content
    article.summary = version.summary
    article.updated_at = datetime.now(timezone.utc)
    db.add(article)
    db.commit()
```

### Comparing Versions

```python
# Get two versions to compare
v1 = db.query(ArticleVersion).filter(
    ArticleVersion.article_id == article.id,
    ArticleVersion.version_number == 2
).first()

v2 = db.query(ArticleVersion).filter(
    ArticleVersion.article_id == article.id,
    ArticleVersion.version_number == 3
).first()

# Compare content (application logic would handle the actual diff)
import difflib
diff = difflib.unified_diff(
    v1.content.splitlines(),
    v2.content.splitlines(),
    lineterm=''
)
```

## Design Considerations

1. **Version Numbering**: Versions are numbered sequentially starting from 1, making it easy to identify the chronological order of changes.

2. **Complete Content Snapshots**: Each version stores a complete snapshot of the article's key fields (title, content, summary) rather than just the differences. This approach:
   - Simplifies restoration of previous versions
   - Makes it easier to view a specific version
   - Avoids complex diff/patch operations
   - Trades storage efficiency for operational simplicity

3. **Change Comments**: The `change_comment` field allows users to document the nature of changes, making the version history more meaningful.

4. **Audit Trail**: By inheriting from `AuditMixin`, each version records who created it, providing accountability.

## Database Impact

- The `article_id` index optimizes queries for retrieving all versions of a specific article.
- The `version_number` index optimizes queries for finding a specific version.
- As articles accumulate many versions over time, the `article_versions` table may grow significantly larger than the `articles` table.

## Related Models

- `Article`: The parent model that owns the versions
