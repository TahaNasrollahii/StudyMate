"""
CRUD operations for study results.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_result import StudyResult


async def create_study_result(
    db: AsyncSession, topic: str, mode: str, result: str, user_id: int
) -> StudyResult:
    """Create a new study result."""
    db_result = StudyResult(topic=topic, mode=mode, result=result, user_id=user_id)
    db.add(db_result)
    await db.flush()
    await db.refresh(db_result)
    return db_result


async def get_study_results(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[StudyResult]:
    """Get all study results for a user with pagination."""
    query = (
        select(StudyResult)
        .where(StudyResult.user_id == user_id)
        .order_by(StudyResult.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_study_results_by_topic(
    db: AsyncSession, topic: str, user_id: int, skip: int = 0, limit: int = 100
) -> List[StudyResult]:
    """Get study results for a user filtered by topic."""
    query = (
        select(StudyResult)
        .where(StudyResult.topic == topic)
        .where(StudyResult.user_id == user_id)
        .order_by(StudyResult.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_study_result_by_id(
    db: AsyncSession, result_id: int, user_id: int
) -> Optional[StudyResult]:
    """Get a single study result by ID for a specific user."""
    query = select(StudyResult).where(StudyResult.id == result_id).where(StudyResult.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()
