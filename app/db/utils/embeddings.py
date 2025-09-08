"""
Utility functions for generating and working with vector embeddings.
"""

import os
from typing import List, Optional, Dict, Any
import logging
from functools import lru_cache

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.article import Article

# Configure logging
logger = logging.getLogger(__name__)

# Default embedding model configuration
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-large"
DEFAULT_EMBEDDING_DIMENSION = 1536
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


async def generate_embedding(
    text: str,
    model: str = DEFAULT_EMBEDDING_MODEL,
    api_key: Optional[str] = None,
) -> List[float]:
    """
    Generate embeddings for a text using OpenAI's API.

    Args:
        text: The text to generate embeddings for
        model: The embedding model to use
        api_key: OpenAI API key (defaults to environment variable)

    Returns:
        A list of floats representing the embedding vector

    Raises:
        ValueError: If the API key is not provided or the API call fails
    """
    api_key = api_key or OPENAI_API_KEY
    if not api_key:
        raise ValueError("OpenAI API key is required to generate embeddings")

    # Prepare the text - truncate if needed
    if len(text) > 8000:
        logger.warning(f"Text too long ({len(text)} chars), truncating to 8000 chars")
        text = text[:8000]

    # Call OpenAI API
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "input": text,
                    "model": model,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise ValueError(f"Failed to generate embeddings: {str(e)}")


@lru_cache(maxsize=100)
def get_cached_embedding(text: str) -> List[float]:
    """
    Get embedding from cache or generate a new one (synchronous version for non-async contexts).
    Uses LRU cache to avoid regenerating embeddings for the same text.

    Args:
        text: The text to get embeddings for

    Returns:
        A list of floats representing the embedding vector
    """
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(generate_embedding(text))
    finally:
        loop.close()


async def update_article_embedding(
    session: AsyncSession,
    article: Article,
    use_cache: bool = True,
) -> Article:
    """
    Update the embedding for an article based on its content.

    Args:
        session: SQLAlchemy async session
        article: The article to update
        use_cache: Whether to use cached embeddings

    Returns:
        The updated article
    """
    # Combine title, summary, and content for embedding
    text_to_embed = (
        f"{article.title}\n\n{article.summary or ''}\n\n{article.content or ''}"
    )

    # Generate embedding
    if use_cache:
        # Use synchronous cached version
        embedding = get_cached_embedding(text_to_embed)
    else:
        # Generate fresh embedding
        embedding = await generate_embedding(text_to_embed)

    # Update article
    article.embedding = embedding

    return article


async def find_similar_articles(
    session: AsyncSession,
    query_text: str,
    limit: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
) -> List[Dict[str, Any]]:
    """
    Find articles similar to the query text using vector similarity search.

    Args:
        session: SQLAlchemy async session
        query_text: The text to find similar articles to
        limit: Maximum number of results to return
        filters: Optional filters to apply (e.g., {'status': 'published'})
        use_cache: Whether to use cached embeddings

    Returns:
        List of similar articles with similarity scores
    """
    # Generate embedding for query text
    if use_cache:
        query_embedding = get_cached_embedding(query_text)
    else:
        query_embedding = await generate_embedding(query_text)

    # Import pgvector's cosine_distance function
    from pgvector.sqlalchemy import cosine_distance

    # Build query
    stmt = (
        select(
            Article.id,
            Article.title,
            Article.slug,
            Article.summary,
            Article.published_at,
            # Calculate cosine distance (lower is more similar)
            cosine_distance(Article.embedding, query_embedding).label("distance"),
        )
        .where(Article.embedding.is_not(None))
        .order_by(cosine_distance(Article.embedding, query_embedding))
        .limit(limit)
    )

    # Apply filters if provided
    if filters:
        for k, v in filters.items():
            if hasattr(Article, k) and v is not None:
                stmt = stmt.where(getattr(Article, k) == v)

    # Execute query
    result = await session.execute(stmt)
    rows = result.all()

    # Format results
    return [
        {
            "id": row.id,
            "title": row.title,
            "slug": row.slug,
            "summary": row.summary,
            "published_at": row.published_at,
            "similarity": 1.0 - float(row.distance),
            # Convert distance to similarity score
        }
        for row in rows
    ]


async def update_all_article_embeddings(
    session: AsyncSession,
    batch_size: int = 10,
    use_cache: bool = True,
) -> int:
    """
    Update embeddings for all articles that don't have embeddings.

    Args:
        session: SQLAlchemy async session
        batch_size: Number of articles to process in each batch
        use_cache: Whether to use cached embeddings

    Returns:
        Number of articles updated
    """
    # Get articles without embeddings
    stmt = select(Article).where(Article.embedding.is_(None)).order_by(Article.id)

    result = await session.execute(stmt)
    articles = result.scalars().all()

    count = 0
    # Process in batches
    for i in range(0, len(articles), batch_size):
        batch = articles[i : i + batch_size]  # noqa: B023 E203
        for article in batch:
            await update_article_embedding(session, article, use_cache=use_cache)
            count += 1

        # Commit after each batch
        await session.commit()

    return count
