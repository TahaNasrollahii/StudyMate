"""
SQLAlchemy model for study results.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class StudyResult(Base):
    """Study result model for storing generated content."""

    __tablename__ = "study_results"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(200), nullable=False, index=True)
    mode = Column(String(20), nullable=False)
    result = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<StudyResult(id={self.id}, topic='{self.topic}', mode='{self.mode}')>"
