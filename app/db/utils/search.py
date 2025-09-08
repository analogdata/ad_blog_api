"""
Async search utilities for articles with advanced PostgreSQL full-text search capabilities.
"""

from sqlalchemy import select, func, desc, or_, literal_column
from typing import Optional, Dict, Any, List

from app.db.models.article import Article

FEATURED_BOOST = 0.2


def _rank(cls, tsq):
    """Calculate text search rank with length normalization (32)"""
    # 32 = length normalization
    return func.ts_rank_cd(cls.search_vector, tsq, 32)


async def search_articles(
    session,
    query: Optional[str],
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    offset: int = 0,
    highlight: bool = True,
    update_vectors: bool = False,
):
    """
    Advanced article search with full-text search, highlighting, and fuzzy fallback.

    Args:
        session: SQLAlchemy async session
        query: Search query string
        filters: Optional dictionary of filters (e.g., {'status': 'published'})
        limit: Maximum number of results to return
        offset: Number of results to skip
        highlight: Whether to highlight matching terms in results
        update_vectors: Whether to update search vectors before searching

    Returns:
        List of article dictionaries with search results
    """
    cls = Article

    # Update search vectors if requested
    if update_vectors:
        await cls.update_all_search_vectors(session)

    base = select(cls.id, cls.slug, cls.published_at, cls.is_featured)

    where = []
    tsq = None
    rank = literal_column("0.0")
    hl_title = cls.title
    hl_summary = cls.summary

    if query:
        tsq = func.websearch_to_tsquery("simple", func.unaccent(query))
        where.append(cls.search_vector.op("@@")(tsq))
        rank = _rank(cls, tsq)

        if highlight:
            hl_title = func.ts_headline(
                "simple",
                func.unaccent(cls.title),
                tsq,
                "StartSel=<b>,StopSel=</b>,MaxFragments=1,MinWords=2,MaxWords=12",
            )
            hl_summary = func.ts_headline(
                "simple",
                func.unaccent(func.coalesce(cls.summary, "")),
                tsq,
                "StartSel=<b>,StopSel=</b>,MaxFragments=2,MinWords=5,MaxWords=25",
            )

    # filters
    if filters:
        for k, v in filters.items():
            if hasattr(cls, k) and v is not None:
                where.append(getattr(cls, k) == v)
        if "published_from" in filters:
            where.append(cls.published_at >= filters["published_from"])
        if "published_to" in filters:
            where.append(cls.published_at < filters["published_to"])

    # scoring: rank + tiny boost for featured + recency (~0..0.15)
    recency_penalty = func.least(
        1.0,
        func.greatest(
            0.0,
            (
                func.extract(
                    "epoch", func.now() - func.coalesce(cls.published_at, func.now())
                )
                / 86400.0  # noqa:
            ),
        ),
    )
    recency_boost = (1.0 - recency_penalty) * 0.15
    featured_boost = func.case((cls.is_featured, FEATURED_BOOST), else_=0.0)

    score = (rank + recency_boost + featured_boost).label("score")

    q = (
        (
            base.add_columns(
                cls.title,
                hl_title.label("hl_title"),
                cls.summary,
                hl_summary.label("hl_summary"),
                score,
            ).where(*where)
            if where
            else base.add_columns(
                cls.title,
                hl_title.label("hl_title"),
                cls.summary,
                hl_summary.label("hl_summary"),
                score,
            )
        )
        .order_by(desc(score), cls.published_at.desc().nullslast())
        .limit(limit)
        .offset(offset)
    )

    rows = (await session.execute(q)).all()

    if rows or not query:
        return [
            {
                "id": r.id,
                "slug": r.slug,
                "title": r.hl_title if highlight else r.title,
                "summary": r.hl_summary if highlight else r.summary,
                "published_at": r.published_at,
                "is_featured": r.is_featured,
                "score": float(r.score or 0.0),
            }
            for r in rows
        ]

    # Fuzzy fallback (title/summary) if FTS got zero hits
    sim_title = func.similarity(cls.title, query)
    sim_summary = func.similarity(func.coalesce(cls.summary, ""), query)
    fuzzy_score = (sim_title * 0.7 + sim_summary * 0.3).label("fuzzy_score")

    q2 = (
        select(
            cls.id,
            cls.slug,
            cls.title,
            cls.summary,
            cls.published_at,
            cls.is_featured,
            fuzzy_score,
        )
        .where(or_(cls.title.ilike(f"%{query}%"), cls.summary.ilike(f"%{query}%")))
        .order_by(desc(fuzzy_score), cls.published_at.desc().nullslast())
        .limit(limit)
        .offset(offset)
    )
    rows2 = (await session.execute(q2)).all()

    return [
        {
            "id": r.id,
            "slug": r.slug,
            "title": r.title,
            "summary": r.summary,
            "published_at": r.published_at,
            "is_featured": r.is_featured,
            "score": float(r.fuzzy_score or 0.0),
        }
        for r in rows2
    ]


async def autocomplete_titles(session, prefix: str, limit: int = 10) -> List[dict]:
    """
    Fast title autocomplete using the lower(title) index.

    Args:
        session: SQLAlchemy async session
        prefix: Title prefix to search for
        limit: Maximum number of results to return

    Returns:
        List of article dictionaries with matching titles
    """
    cls = Article
    q = (
        select(cls.slug, cls.title)
        .where(func.lower(cls.title).startswith(prefix.lower()))
        .order_by(cls.published_at.desc().nullslast())
        .limit(limit)
    )
    rows = (await session.execute(q)).all()

    return [{"slug": row.slug, "title": row.title} for row in rows]
