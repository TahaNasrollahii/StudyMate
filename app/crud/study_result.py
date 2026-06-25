"""
CRUD operations for study results.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_result import StudyResult


async def create_study_result(
    db: AsyncSession,
    topic: str,
    mode: str,
    result: str
) -> StudyResult:
    """Create a new study result."""
    db_result = StudyResult(
        topic=topic,
        mode=mode,
        result=result
    )
    db.add(db_result)
    await db.flush()
    await db.refresh(db_result)
    return db_result


async def get_study_results(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[StudyResult]:
    """Get all study results with pagination."""
    query = select(StudyResult).order_by(StudyResult.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_study_results_by_topic(
    db: AsyncSession,
    topic: str,
    skip: int = 0,
    limit: int = 100
) -> List[StudyResult]:
    """Get study results filtered by topic."""
    query = (
        select(StudyResult)
        .where(StudyResult.topic == topic)
        .order_by(StudyResult.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_study_result_by_id(db: AsyncSession, result_id: int) -> Optional[StudyResult]:
    """Get a single study result by ID."""
    query = select(StudyResult).where(StudyResult.id == result_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()
