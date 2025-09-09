# Article Model Documentation

The `Article` model is a core component of the blog API, representing blog posts with comprehensive features for content management, SEO optimization, and advanced search capabilities.

## Model Overview

The `Article` model inherits from multiple mixins to provide a rich set of features:
- `SoftDeleteMixin`: Enables soft deletion
- `URLValidationMixin`: Validates URL fields
- `AuditMixin`: Tracks who created and modified articles
- `HttpUrlFieldMixin`: Validates URL fields and ensures they are stored as strings
- `SlugGeneratorMixin`: Automatically generates URL-friendly slugs

The model also implements timestamp fields directly with database-driven defaults:

## Fields and Properties

| Field | Type | Description | Indexes |
|-------|------|-------------|---------|
| `id` | int | Primary key | Primary key |
| `title` | str | Article title | Indexed, Case-insensitive index |
| `slug` | str | URL-friendly version of title | Unique constraint |
| `content` | Optional[str] | Main article content | Full-text search |
| `summary` | Optional[str] | Brief summary of article | Trigram index |
| `featured_image` | Optional[str] | URL to featured image | URL validation |
| `header_image` | Optional[str] | URL to header image | URL validation |
| `status` | Status | Article status (draft, published, scheduled) | Composite indexes with author, category |
| `is_featured` | bool | Whether article is featured | Indexed |
| `seo_title` | Optional[str] | SEO-optimized title | - |
| `seo_description` | Optional[str] | SEO meta description | - |
| `seo_keywords` | Optional[str] | SEO keywords | - |
| `seo_image` | Optional[str] | Image for social sharing | URL validation |
| `canonical_url` | Optional[str] | Canonical URL for SEO | URL validation |
| `views` | int | View count | Check constraint (non-negative) |
| `likes` | int | Like count | Check constraint (non-negative) |
| `read_time` | Optional[int] | Estimated reading time in minutes | - |
| `scheduled_at` | Optional[datetime] | When article is scheduled to publish | - |
| `published_at` | Optional[datetime] | When article was published | Indexed |
| `author_id` | Optional[int] | Foreign key to authors table | Indexed with status |
| `category_id` | Optional[int] | Foreign key to categories table | Indexed with status |
| `search_vector` | Optional[str] | PostgreSQL TSVECTOR for full-text search | GIN index |
| `embedding` | Optional[List[float]] | Vector embedding for semantic search | IVFFLAT index |

## Relationships

| Relationship | Related Model | Type | Description |
|--------------|--------------|------|-------------|
| `author` | Author | Many-to-One | Author of the article |
| `category` | Category | Many-to-One | Category the article belongs to |
| `tags` | Tag | Many-to-Many | Tags associated with the article (via ArticleTag) |
| `versions` | ArticleVersion | One-to-Many | Version history of the article |

## Indexes and Constraints

The `Article` model includes several specialized indexes for performance optimization:

1. **Uniqueness Constraints**:
   - `uq_articles_slug`: Ensures slug uniqueness

2. **Common Filter Indexes**:
   - `ix_articles_author_status`: Optimizes filtering by author and status
   - `ix_articles_category_status`: Optimizes filtering by category and status
   - `ix_articles_published_at`: Optimizes sorting by publication date
   - `ix_articles_featured`: Optimizes filtering for featured articles
   - `ix_articles_status_published_at`: Optimizes listing articles by status and publication date

3. **Full-text Search Indexes**:
   - `ix_articles_search_vector`: GIN index for full-text search
   - `ix_articles_title_trgm`: Trigram GIN index for fuzzy search on title
   - `ix_articles_summary_trgm`: Trigram GIN index for fuzzy search on summary
   - `ix_articles_title_lower`: Case-insensitive title search

4. **Vector Search Index**:
   - `ix_articles_embedding_vector_idx`: IVFFLAT index for approximate nearest neighbor search

5. **Check Constraints**:
   - `ck_articles_views_nonneg`: Ensures views count is non-negative
   - `ck_articles_likes_nonneg`: Ensures likes count is non-negative

## Methods

### Status Management

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `publish()` | None | None | Sets status to PUBLISHED and updates published_at timestamp |
| `schedule(scheduled_time)` | datetime | None | Sets status to SCHEDULED and updates scheduled_at timestamp |
| `draft()` | None | None | Sets status to DRAFT and clears published_at and scheduled_at |
| `feature()` | None | None | Sets is_featured to True |
| `unfeature()` | None | None | Sets is_featured to False |

### Tag Management

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `add_tag(tag)` | Tag | None | Adds a tag to the article if not already present |
| `remove_tag(tag_id)` | int | bool | Removes a tag from the article, returns True if successful |

### Metrics and Content

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `calculate_read_time()` | None | int | Calculates and sets read time based on content length |
| `increment_view(session)` | SQLAlchemy session | int | Atomically increments view count |
| `increment_like(session)` | SQLAlchemy session | int | Atomically increments like count |

### Version Management

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `create_version(user_id, change_comment)` | int, Optional[str] | ArticleVersion | Creates a new version of the article |
| `restore_version(version_number)` | int | None | Restores article to a previous version |
| `get_version_history()` | None | List[dict] | Returns version history as a list of dictionaries |

### Search Optimization

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `update_search_vector(session)` | SQLAlchemy session | None | Updates the search_vector with weighted text from title, summary, and content |
| `update_all_search_vectors(session)` (classmethod) | SQLAlchemy session | int | Updates search vectors for all articles, returns count of updated articles |

## Usage Flow

The `Article` model supports the following typical workflows:

### Article Creation and Publishing Flow

1. Create a draft article:
   ```python
   article = Article(title="New Article", content="Content here...")
   article.calculate_read_time()
   db.add(article)
   db.commit()
   ```

2. Update and publish:
   ```python
   article.content = "Updated content"
   article.calculate_read_time()
   article.publish()
   article.update_search_vector(session)
   db.add(article)
   db.commit()
   ```

3. Schedule for future publication:
   ```python
   from datetime import datetime, timedelta, timezone
   future = datetime.now(timezone.utc) + timedelta(days=2)
   article.schedule(future)
   db.add(article)
   db.commit()
   ```

### Version Control Flow

1. Create a new version:
   ```python
   version = article.create_version(user_id=1, change_comment="Updated introduction")
   db.add(version)
   db.commit()
   ```

2. View version history:
   ```python
   history = article.get_version_history()
   ```

3. Restore a previous version:
   ```python
   article.restore_version(version_number=2)
   db.add(article)
   db.commit()
   ```

### Search Optimization Flow

1. Update search vector after content changes:
   ```python
   article.title = "New Title"
   article.content = "New content"
   await article.update_search_vector(session)
   db.add(article)
   db.commit()
   ```

2. Perform full-text search:
   ```sql
   SELECT * FROM articles 
   WHERE search_vector @@ to_tsquery('english', 'search:* & term:*')
   ORDER BY ts_rank(search_vector, to_tsquery('english', 'search:* & term:*')) DESC;
   ```

3. Perform vector similarity search:
   ```sql
   SELECT * FROM articles
   ORDER BY embedding <-> :query_embedding
   LIMIT 10;
   ```

## Advanced Features

### Full-Text Search

The `Article` model includes a `search_vector` column that combines weighted text from the title (weight A), summary (weight B), and content (weight C). This enables powerful full-text search capabilities using PostgreSQL's text search functions.

### Vector Embeddings

The `embedding` column stores a 1536-dimensional vector representation of the article content, compatible with OpenAI's text-embedding-3-large model. This enables semantic search capabilities, allowing users to find articles with similar meaning even if they don't share the same keywords.
