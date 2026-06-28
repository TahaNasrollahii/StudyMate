"""
Import all models here so Alembic can find them in one place.
"""

from app.models.study_result import StudyResult
from app.models.user import User

__all__ = ["StudyResult", "User"]
