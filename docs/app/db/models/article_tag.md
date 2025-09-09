# ArticleTag Model Documentation

The `ArticleTag` model implements a many-to-many relationship between articles and tags in the blog API.

## Model Overview

`ArticleTag` is a link table (also known as a junction table or association table) that connects the `Article` and `Tag` models. It enables articles to have multiple tags and tags to be associated with multiple articles.

## Fields and Properties

| Field | Type | Description | Constraints |
|-------|------|-------------|------------|
| `article_id` | Optional[int] | Foreign key to articles table | Primary key (composite), Foreign key |
| `tag_id` | Optional[int] | Foreign key to tags table | Primary key (composite), Foreign key |

## Table Structure

```
Table: article_tags
--------------------------
article_id (PK, FK) → articles.id
tag_id (PK, FK) → tags.id
```

## Relationships

The `ArticleTag` model serves as a link model for the many-to-many relationship between:

1. `Article.tags`: List of tags associated with an article
2. `Tag.articles`: List of articles associated with a tag

## Usage Flow

### Adding Tags to Articles

```python
# Using the Article model's helper method
article = Article(title="New Article", content="Content here...")
tag = Tag(name="Technology")
article.add_tag(tag)
db.add(article)
db.commit()

# Direct manipulation of the relationship
article.tags.append(tag)
db.add(article)
db.commit()
```

### Removing Tags from Articles

```python
# Using the Article model's helper method
article.remove_tag(tag_id=1)
db.add(article)
db.commit()

# Direct manipulation of the relationship
article.tags = [t for t in article.tags if t.id != tag_id]
db.add(article)
db.commit()
```

### Querying Articles by Tag

```python
# Get all articles with a specific tag
articles = db.query(Article).join(ArticleTag).join(Tag).filter(Tag.name == "Technology").all()

# Get all tags for a specific article
tags = db.query(Tag).join(ArticleTag).filter(ArticleTag.article_id == article_id).all()
```

## Design Considerations

1. **Composite Primary Key**: The table uses a composite primary key consisting of both `article_id` and `tag_id`, which:
   - Ensures each article-tag combination is unique
   - Prevents duplicate associations
   - Optimizes storage by avoiding an additional surrogate key

2. **No Additional Fields**: The model is kept minimal with just the foreign keys needed to establish the relationship. This is appropriate when no additional metadata about the relationship is needed.

3. **Optional Types**: Both foreign keys are defined as `Optional[int]` to accommodate SQLModel's initialization requirements, but in practice, they should always have values when used.

## Database Impact

- The composite primary key serves as an index for both columns, optimizing queries from both directions (articles → tags and tags → articles).
- No additional indexes are needed since the primary key columns are already indexed.

## Related Models

- `Article`: The article entity in the many-to-many relationship
- `Tag`: The tag entity in the many-to-many relationship
