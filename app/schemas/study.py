"""
Pydantic schemas for study-related API endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class StudyMode(str, Enum):
    """Enum for study modes."""
    SUMMARY = "summary"
    QUIZ = "quiz"
    PLAN = "plan"


class StudyRequest(BaseModel):
    """Request schema for generating study content."""
    topic: str = Field(..., min_length=1, max_length=200, description="Topic to study")
    mode: StudyMode = Field(..., description="Study mode: summary, quiz, or plan")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "topic": "Python decorators",
                    "mode": "summary"
                }
            ]
        }
    }


class StudyResponse(BaseModel):
    """Response schema for generated study content."""
    id: int = Field(..., description="Unique identifier")
    topic: str = Field(..., description="Study topic")
    mode: StudyMode = Field(..., description="Study mode")
    result: str = Field(..., description="Generated study content")
    created_at: datetime = Field(..., description="Timestamp of creation")


class StudyHistoryResponse(BaseModel):
    """Response schema for study history."""
    results: List[StudyResponse] = Field(..., description="List of study results")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Health status")


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str = Field(..., description="Error message")
