"""
StudyMate API - AI-powered study assistant backend.

This module creates and configures the FastAPI application.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_db, init_db
from app.redis_client import close_redis
from app.routers import study

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    logger.info("Starting StudyMate API...")
    await init_db()
    logger.info("Database initialized")

    yield

    logger.info("Shutting down StudyMate API...")
    await close_redis()
    await close_db()
    logger.info("Cleanup complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="An AI-powered study assistant API that generates summaries, quizzes, and study plans.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(study.router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint with API information."""
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "docs": "/docs"}
