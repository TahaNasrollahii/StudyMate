"""
Study router endpoints.
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.study_result import (
    create_study_result,
    get_study_results,
    get_study_results_by_topic,
)
from app.database import get_db
from app.redis_client import get_cached_result, set_cached_result
from app.schemas.study import (
    ErrorResponse,
    HealthResponse,
    StudyHistoryResponse,
    StudyMode,
    StudyRequest,
    StudyResponse,
)
from app.services.llm_service import generate_study_content

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/study", tags=["study"])


@router.post(
    "/generate",
    response_model=StudyResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Generate study content",
    description="Generate AI-powered study content for a given topic and mode.",
)
async def generate_study(
    request: StudyRequest, db: AsyncSession = Depends(get_db)
) -> StudyResponse:
    """
    Generate study content for a topic.

    - **topic**: The topic to generate content for
    - **mode**: The study mode (summary, quiz, or plan)
    """
    cache_key = f"topic:{request.topic}:{request.mode.value}"

    try:
        cached_result = await get_cached_result(cache_key)
        if cached_result:
            cached_data = json.loads(cached_result)
            return StudyResponse(**cached_data)

        llm_result = await generate_study_content(request.topic, request.mode.value)

        db_result = await create_study_result(
            db=db, topic=request.topic, mode=request.mode.value, result=llm_result
        )

        response_data = {
            "id": db_result.id,
            "topic": db_result.topic,
            "mode": db_result.mode,
            "result": db_result.result,
            "created_at": db_result.created_at.isoformat(),
        }
        await set_cached_result(cache_key, json.dumps(response_data), ttl=3600)

        return StudyResponse(
            id=db_result.id,
            topic=db_result.topic,
            mode=StudyMode(db_result.mode),
            result=db_result.result,
            created_at=db_result.created_at,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating study content: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate study content: {str(e)}",
        )


@router.get(
    "/history",
    response_model=StudyHistoryResponse,
    summary="Get study history",
    description="Retrieve all previously generated study results.",
)
async def get_history(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> StudyHistoryResponse:
    """Get all study results ordered by creation date."""
    results = await get_study_results(db, skip=skip, limit=limit)

    study_responses = [
        StudyResponse(
            id=r.id,
            topic=r.topic,
            mode=StudyMode(r.mode),
            result=r.result,
            created_at=r.created_at,
        )
        for r in results
    ]

    return StudyHistoryResponse(results=study_responses)


@router.get(
    "/history/{topic}",
    response_model=StudyHistoryResponse,
    responses={
        404: {"model": ErrorResponse, "description": "No results found for topic"}
    },
    summary="Get study history by topic",
    description="Retrieve all study results for a specific topic.",
)
async def get_history_by_topic(
    topic: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> StudyHistoryResponse:
    """Get study results filtered by topic."""
    results = await get_study_results_by_topic(db, topic, skip=skip, limit=limit)

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No study results found for topic: {topic}",
        )

    study_responses = [
        StudyResponse(
            id=r.id,
            topic=r.topic,
            mode=StudyMode(r.mode),
            result=r.result,
            created_at=r.created_at,
        )
        for r in results
    ]

    return StudyHistoryResponse(results=study_responses)


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
    description="Check if the API is running.",
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")
