"""
Utility functions for vector similarity search using pgvector.
"""

from typing import List, Optional, Dict, Any, Tuple
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import cosine_distance, l2_distance, max_inner_product

from app.db.models.article import Article

# Configure logging
logger = logging.getLogger(__name__)


async def search_by_embedding(
    session: AsyncSession,
    query_vec: List[float],
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    distance_metric: str = "cosine",  # Must match the operator class used in the index
) -> List[Tuple[Article, float]]:
    """
    Search for articles by vector similarity using pgvector.

    Args:
        session: SQLAlchemy async session
        query_vec: The query vector to search with
        limit: Maximum number of results to return
        filters: Optional filters to apply (e.g., {'status': 'published'})
        distance_metric: The distance metric to use ('cosine', 'l2', or 'ip'). Must match the operator class used in the index (vector_cosine_ops, vector_l2_ops, or vector_ip_ops)

    Returns:
        List of tuples containing (Article, distance)
    """
    # Select the appropriate distance function
    if distance_metric == "cosine":
        distance_fn = cosine_distance
    elif distance_metric == "l2":
        distance_fn = l2_distance
    elif distance_metric == "ip":
        # For inner product, smaller is worse (opposite of cosine/l2)
        distance_fn = max_inner_product
        # We'll negate it later to keep consistent ordering
    else:
        raise ValueError(f"Unsupported distance metric: {distance_metric}")

    # Build the query
    distance_expr = distance_fn(Article.embedding, query_vec)

    # For inner product, we want to maximize (not minimize)
    if distance_metric == "ip":
        order_expr = func.negative(distance_expr)
    else:
        order_expr = distance_expr

    stmt = (
        select(Article, distance_expr.label("distance"))
        .where(Article.embedding.is_not(None))
        .order_by(order_expr)
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

    return rows  # [(Article, distance), ...]


async def hybrid_search(
    session: AsyncSession,
    text_query: str,
    embedding_vector: List[float],
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    semantic_weight: float = 0.5,
    recency_boost: bool = True,
    featured_boost: bool = True,
) -> List[Dict[str, Any]]:
    """
    Perform hybrid search combining full-text search and vector similarity.

    Args:
        session: SQLAlchemy async session
        text_query: The text query for full-text search
        embedding_vector: The embedding vector for semantic search
        limit: Maximum number of results to return
        filters: Optional filters to apply (e.g., {'status': 'published'})
        semantic_weight: Weight to give semantic search vs full-text (0.0-1.0)
        recency_boost: Whether to boost more recent articles
        featured_boost: Whether to boost featured articles

    Returns:
        List of article dictionaries with combined scores
    """
    # Import here to avoid circular imports
    from app.db.utils.search import search_articles

    # Get text search results
    text_results = await search_articles(
        session=session,
        query=text_query,
        filters=filters,
        limit=limit * 2,  # Get more results to allow for better merging
        highlight=True,
    )

    # Get semantic search results
    semantic_results = await search_by_embedding(
        session=session,
        query_vec=embedding_vector,
        limit=limit * 2,  # Get more results to allow for better merging
        filters=filters,
    )

    # Find max distance for normalization
    max_distance = 1.0
    if semantic_results:
        max_distance = max(float(distance) for _, distance in semantic_results) or 1.0

    # Convert semantic results to dict format with normalized scores
    semantic_dicts = [
        {
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "published_at": article.published_at,
            "is_featured": article.is_featured,
            # Normalize semantic score to 0.0-1.0 range
            "semantic_score": 1.0 - (float(distance) / max_distance),
        }
        for article, distance in semantic_results
    ]

    # Find max text score for normalization
    max_text_score = 1.0
    if text_results:
        max_text_score = max(item.get("score", 0.0) for item in text_results) or 1.0

    # Create a mapping of article IDs to results
    results_by_id = {}

    # Get current time for recency boost
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    recent_threshold = now - timedelta(days=30)  # Articles within last 30 days

    # Process text search results
    for item in text_results:
        # Normalize text score to 0.0-1.0 range
        normalized_text_score = item.get("score", 0.0) / max_text_score

        # Start with base combined score
        combined_score = (1.0 - semantic_weight) * normalized_text_score

        # Store in results
        results_by_id[item["id"]] = {
            **item,
            "text_score": normalized_text_score,
            "combined_score": combined_score,
        }

    # Process semantic search results
    for item in semantic_dicts:
        if item["id"] in results_by_id:
            # Article already in results, update with semantic score
            results_by_id[item["id"]]["semantic_score"] = item["semantic_score"]
            results_by_id[item["id"]]["combined_score"] += (
                semantic_weight * item["semantic_score"]
            )
        else:
            # New article from semantic search
            results_by_id[item["id"]] = {
                **item,
                "text_score": 0.0,
                "combined_score": semantic_weight * item["semantic_score"],
            }

    # Apply recency and featured boosts
    for item_id, item in results_by_id.items():
        # Apply recency boost if enabled
        if recency_boost and item.get("published_at"):
            published_at = item["published_at"]
            if published_at and published_at > recent_threshold:
                # Boost recent articles by up to 15%
                days_old = (now - published_at).days
                recency_factor = max(0, (30 - days_old) / 30) * 0.15
                item["combined_score"] *= 1.0 + recency_factor
                item["recency_boost"] = recency_factor

        # Apply featured boost if enabled
        if featured_boost and item.get("is_featured"):
            # Boost featured articles by 10%
            item["combined_score"] *= 1.1
            item["featured_boost"] = 0.1

    # Convert to list and sort by combined score
    results = list(results_by_id.values())
    results.sort(key=lambda x: x["combined_score"], reverse=True)

    # Return top results
    return results[:limit]
