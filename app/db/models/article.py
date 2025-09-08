from datetime import datetime, timezone
from typing import Optional, List, ClassVar
import enum

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import (
    Column,
    Text,
    UniqueConstraint,
    Index,
    text,
    CheckConstraint,
    column,
    func,
    ForeignKey,
    Integer,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
from app.db.models.base import (
    TimestampMixin,
    SoftDeleteMixin,
    URLValidationMixin,
    AuditMixin,
    HttpUrlFieldMixin,
    SlugGeneratorMixin,
)

# Forward refs / related models
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.article_version import ArticleVersion
from app.db.models.tag import Tag
from app.db.models.author import Author
from app.db.models.category import Category
from app.db.models.article_tag import ArticleTag


class Status(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"


# -----------------------------------------------------------------------------
# Article model with generated full-text search column + proper indexes
# -----------------------------------------------------------------------------
class Article(
    TimestampMixin,
    SoftDeleteMixin,
    URLValidationMixin,
    AuditMixin,
    HttpUrlFieldMixin,
    SlugGeneratorMixin,
    SQLModel,
    table=True,
):
    __tablename__ = "articles"

    # For your existing mixins
    url_fields: ClassVar[list[str]] = [
        "featured_image",
        "header_image",
        "seo_image",
        "canonical_url",
    ]
    slug_source_field: ClassVar[str] = "title"

    # --- Columns ---
    id: int = Field(default=None, primary_key=True)

    # Core
    title: str = Field(index=True)
    slug: str = Field()
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    summary: Optional[str] = None

    # Media
    featured_image: Optional[str] = None
    header_image: Optional[str] = None

    # Status
    status: Status = Field(default=Status.DRAFT)
    is_featured: bool = Field(default=False)

    # SEO
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    seo_image: Optional[str] = None
    canonical_url: Optional[str] = None

    # Metrics
    views: int = Field(default=0)
    likes: int = Field(default=0)
    read_time: Optional[int] = None  # minutes

    # Timestamps
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    # FKs
    author_id: Optional[int] = Field(
        default=None, 
        sa_column=Column(Integer, ForeignKey("authors.id", ondelete="SET NULL"))
    )
    category_id: Optional[int] = Field(
        default=None, 
        sa_column=Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    )

    # Relationships
    author: Optional["Author"] = Relationship(back_populates="articles")
    category: Optional["Category"] = Relationship(back_populates="articles")
    tags: List["Tag"] = Relationship(back_populates="articles", link_model=ArticleTag)
    versions: List["ArticleVersion"] = Relationship(back_populates="article")

    # --- FTS column (will be updated by application code or triggers) ---
    # Regular TSVECTOR column instead of a generated column to avoid immutable function issues
    search_vector: Optional[str] = Field(
        default=None,
        sa_column=Column(TSVECTOR, nullable=True),
    )

    # --- Vector embedding for semantic search ---
    # Using 1536 dimensions (OpenAI's text-embedding-3-large model)
    # Can be adjusted based on the embedding model used
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(Vector(1536), nullable=True),
    )

    # --- Table args / indexes ---
    __table_args__ = (
        # Uniqueness - only slug needs to be unique, titles can repeat
        UniqueConstraint("slug", name="uq_articles_slug"),
        # Common filter paths
        Index("ix_articles_author_status", "author_id", "status"),
        Index("ix_articles_category_status", "category_id", "status"),
        Index("ix_articles_published_at", "published_at"),
        Index("ix_articles_featured", "is_featured"),
        # Status + published_at index for list pages
        Index("ix_articles_status_published_at", "status", "published_at"),
        # Full-text search GIN index
        Index(
            "ix_articles_search_vector",
            "search_vector",
            postgresql_using="gin",
        ),
        # Trigram GIN indexes for fuzzy search on title/summary
        Index(
            "ix_articles_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
        Index(
            "ix_articles_summary_trgm",
            "summary",
            postgresql_using="gin",
            postgresql_ops={"summary": "gin_trgm_ops"},
        ),
        # Non-negative constraints for counters
        CheckConstraint("views >= 0", name="ck_articles_views_nonneg"),
        CheckConstraint("likes >= 0", name="ck_articles_likes_nonneg"),
        # Case-insensitive title search index
        Index("ix_articles_title_lower", func.lower(column("title"))),
        # Vector similarity search index using IVFFLAT (approximate nearest neighbor)
        Index(
            "ix_articles_embedding_vector_idx",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={"lists": 100},
        ),
    )

    # --- Helpers ---
    def publish(self) -> None:
        self.status = Status.PUBLISHED
        self.published_at = datetime.now(timezone.utc)

    def schedule(self, scheduled_time: datetime) -> None:
        self.status = Status.SCHEDULED
        self.scheduled_at = scheduled_time

    def draft(self) -> None:
        self.status = Status.DRAFT
        self.published_at = None
        self.scheduled_at = None

    def feature(self) -> None:
        self.is_featured = True

    def unfeature(self) -> None:
        self.is_featured = False

    def add_tag(self, tag: "Tag") -> None:
        if not any(t.id == tag.id for t in self.tags):
            self.tags.append(tag)

    def remove_tag(self, tag_id: int) -> bool:
        initial = len(self.tags)
        self.tags = [t for t in self.tags if t.id != tag_id]
        return len(self.tags) < initial

    def calculate_read_time(self) -> int:
        if not self.content:
            self.read_time = 0
            return 0
        words = len(self.content.split())
        minutes = max(1, round(words / 200))
        self.read_time = minutes
        return minutes

    async def increment_view(self, session) -> int:
        """Atomically increment the view count at the database level

        Args:
            session: SQLAlchemy async session

        Returns:
            The new view count
        """
        sql = "UPDATE articles SET views = views + 1 WHERE id = :id RETURNING views"
        result = await session.execute(text(sql), {"id": self.id})
        new_count = result.scalar_one()
        self.views = new_count  # Update the model instance to match DB
        return new_count

    async def increment_like(self, session) -> int:
        """Atomically increment the like count at the database level

        Args:
            session: SQLAlchemy async session

        Returns:
            The new like count
        """
        sql = "UPDATE articles SET likes = likes + 1 WHERE id = :id RETURNING likes"
        result = await session.execute(text(sql), {"id": self.id})
        new_count = result.scalar_one()
        self.likes = new_count  # Update the model instance to match DB
        return new_count

    def create_version(
        self, user_id: int, change_comment: Optional[str] = None
    ) -> "ArticleVersion":
        from app.db.models.article_version import ArticleVersion

        next_version = (
            1 if not self.versions else max(v.version_number for v in self.versions) + 1
        )
        return ArticleVersion(
            article_id=self.id,
            version_number=next_version,
            title=self.title,
            content=self.content,
            summary=self.summary,
            change_comment=change_comment,
            created_by_id=user_id,
        )

    def restore_version(self, version_number: int) -> None:
        for v in self.versions:
            if v.version_number == version_number:
                self.title = v.title
                self.content = v.content
                self.summary = v.summary
                self.updated_at = datetime.now(timezone.utc)
                return
        raise ValueError(f"Version {version_number} not found")

    def get_version_history(self) -> List[dict]:
        if not self.versions:
            return []
        return [
            {
                "version": v.version_number,
                "title": v.title,
                "created_at": v.created_at,
                "created_by": v.created_by_id,
                "comment": v.change_comment,
            }
            for v in sorted(self.versions, key=lambda x: x.version_number)
        ]

    async def update_search_vector(self, session) -> None:
        """Update the search_vector column with weighted text from title, summary, and content

        This method should be called after any changes to title, summary, or content.
        It uses the unaccent function and to_tsvector to create a weighted search vector.

        Args:
            session: SQLAlchemy async session to execute the SQL query
        """
        # Use raw SQL to leverage PostgreSQL's text search functions
        sql = """
        UPDATE articles
        SET search_vector =
            setweight(to_tsvector('english', unaccent(coalesce(title,''))), 'A') ||
            setweight(to_tsvector('english', unaccent(coalesce(summary,''))), 'B') ||
            setweight(to_tsvector('english', unaccent(coalesce(content,''))), 'C')
        WHERE id = :id
        """
        await session.execute(text(sql), {"id": self.id})

    @classmethod
    async def update_all_search_vectors(cls, session) -> int:
        """Update search_vector for all articles in the database

        Args:
            session: SQLAlchemy async session

        Returns:
            Number of articles updated
        """
        sql = """
        UPDATE articles
        SET search_vector =
            setweight(to_tsvector('english', unaccent(coalesce(title,''))), 'A') ||
            setweight(to_tsvector('english', unaccent(coalesce(summary,''))), 'B') ||
            setweight(to_tsvector('english', unaccent(coalesce(content,''))), 'C')
        """
        result = await session.execute(text(sql))
        return result.rowcount
