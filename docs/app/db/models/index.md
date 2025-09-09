# Database Models Overview

This document provides a comprehensive overview of the database models used in the blog API, their relationships, and key features.

## Model Hierarchy

The blog API uses the following models to represent its data structure:

1. **Core Content Models**
   - [Article](./article.md): Blog posts with rich content and metadata
   - [ArticleVersion](./article_version.md): Version history for articles
   - [Category](./category.md): Content classification
   - [Tag](./tag.md): Content labeling
   - [ArticleTag](./article_tag.md): Many-to-many relationship between articles and tags

2. **User Models**
   - [User](./user.md): Authentication and authorization
   - [Author](./author.md): Content creator profiles
   - [Permission](./permission.md): Fine-grained access control
   - [Subscriber](./subscriber.md): Newsletter subscribers

3. **Base Components**
   - [Base Mixins](./base.md): Reusable functionality for models

## Entity Relationship Diagram

```
┌─────────────┐     ┌───────────────┐     ┌────────────┐
│    User     │     │    Author     │     │  Article   │
├─────────────┤     ├───────────────┤     ├────────────┤
│ id          │─┐   │ id            │  ┌─>│ id         │
│ email       │ │   │ name          │  │  │ title      │
│ password    │ │   │ bio           │  │  │ content    │
│ role        │ │   │ slug          │<─┘  │ status     │
│ permissions │<┼───┤ user          │     │ author_id  │─┐
└─────────────┘ │   └───────────────┘     │ category_id│─┼─┐
                │                          └────────────┘ │ │
                │                                 ▲       │ │
                │                                 │       │ │
┌─────────────┐ │   ┌───────────────┐     ┌──────┴─────┐ │ │
│ Permission  │ │   │ ArticleVersion │     │ ArticleTag │ │ │
├─────────────┤ │   ├───────────────┤     ├────────────┤ │ │
│ id          │ │   │ id            │     │ article_id │<┘ │
│ name        │ │   │ article_id    │─────┤ tag_id     │   │
│ user_id     │<┘   │ version_number│     └────────────┘   │
└─────────────┘     │ title         │           │          │
                    │ content       │           ▼          │
                    └───────────────┘     ┌────────────┐   │
                                          │    Tag     │   │
┌─────────────┐     ┌───────────────┐     ├────────────┤   │
│ Subscriber  │     │   Category    │     │ id         │   │
├─────────────┤     ├───────────────┤     │ name       │   │
│ id          │     │ id            │     │ slug       │   │
│ email       │     │ name          │<────┤ articles   │   │
│ is_verified │     │ description   │     └────────────┘   │
└─────────────┘     │ slug          │<────────────────────┘
                    └───────────────┘
```

## Key Relationships

| Relationship | Type | Description |
|--------------|------|-------------|
| User → Author | One-to-One | A user can have one author profile |
| User → Permission | One-to-Many | A user can have multiple permissions |
| Author → Article | One-to-Many | An author can write multiple articles |
| Category → Article | One-to-Many | A category can contain multiple articles |
| Article ↔ Tag | Many-to-Many | Articles can have multiple tags, tags can be applied to multiple articles |
| Article → ArticleVersion | One-to-Many | An article can have multiple versions |

## Model Features

### Content Management

- **Articles**: Core content with rich metadata, SEO optimization, and version control
- **Categories**: Primary content organization
- **Tags**: Flexible content labeling and discovery

### User Management

- **Users**: Authentication, authorization, and profile management
- **Authors**: Public profiles for content creators
- **Permissions**: Fine-grained access control

### Advanced Features

- **Full-text Search**: Articles include a search vector for PostgreSQL full-text search
- **Vector Embeddings**: Articles support semantic search via vector embeddings
- **Version Control**: Article history is preserved with the ability to restore previous versions
- **Soft Delete**: Records can be marked as deleted without being permanently removed

## Database Optimizations

The models include several optimizations for performance:

1. **Strategic Indexing**:
   - Composite indexes for common query patterns
   - Full-text search indexes
   - Vector similarity search indexes

2. **Denormalization**:
   - Calculated fields like `read_time`
   - Pre-computed search vectors

3. **Constraints**:
   - Uniqueness constraints for data integrity
   - Check constraints for data validation

## Common Workflows

### Content Creation Flow

1. User creates an article (draft status)
2. Article is edited and categorized
3. Tags are added
4. Article is published or scheduled
5. Versions are created to track changes

### User Registration Flow

1. User registers with email and password
2. Email verification is sent
3. User verifies email
4. User can be associated with an author profile
5. Permissions are assigned based on role

### Content Discovery Flow

1. Articles can be found by category
2. Articles can be found by tag
3. Articles can be found by full-text search
4. Articles can be found by semantic similarity
5. Related content can be suggested based on shared tags
