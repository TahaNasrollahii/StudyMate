import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_llm_response():
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a mock LLM response about the topic."
                }
            }
        ]
    }


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.mark.anyio
async def test_health_check(client):
    response = await client.get("/api/v1/study/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.anyio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


@pytest.mark.anyio
@patch("app.routers.study.generate_study_content")
@patch("app.routers.study.get_cached_result")
@patch("app.routers.study.set_cached_result")
@patch("app.routers.study.create_study_result")
async def test_generate_summary(
    mock_create,
    mock_set_cache,
    mock_get_cache,
    mock_llm,
    client
):
    mock_get_cache.return_value = None
    mock_llm.return_value = "This is a summary of Python decorators."
    
    mock_db_result = AsyncMock()
    mock_db_result.id = 1
    mock_db_result.topic = "Python decorators"
    mock_db_result.mode = "summary"
    mock_db_result.result = "This is a summary of Python decorators."
    mock_db_result.created_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_create.return_value = mock_db_result
    
    mock_set_cache.return_value = None
    
    response = await client.post(
        "/api/v1/study/generate",
        json={"topic": "Python decorators", "mode": "summary"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["topic"] == "Python decorators"
    assert data["mode"] == "summary"
    assert "result" in data


@pytest.mark.anyio
@patch("app.routers.study.generate_study_content")
@patch("app.routers.study.get_cached_result")
@patch("app.routers.study.set_cached_result")
@patch("app.routers.study.create_study_result")
async def test_generate_quiz(
    mock_create,
    mock_set_cache,
    mock_get_cache,
    mock_llm,
    client
):
    mock_get_cache.return_value = None
    mock_llm.return_value = "1. What is X?\nA) ...\nB) ...\nC) ...\nD) ..."
    
    mock_db_result = AsyncMock()
    mock_db_result.id = 2
    mock_db_result.topic = "Python basics"
    mock_db_result.mode = "quiz"
    mock_db_result.result = "1. What is X?\nA) ...\nB) ...\nC) ...\nD) ..."
    mock_db_result.created_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_create.return_value = mock_db_result
    
    mock_set_cache.return_value = None
    
    response = await client.post(
        "/api/v1/study/generate",
        json={"topic": "Python basics", "mode": "quiz"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["mode"] == "quiz"


@pytest.mark.anyio
@patch("app.routers.study.generate_study_content")
@patch("app.routers.study.get_cached_result")
@patch("app.routers.study.set_cached_result")
@patch("app.routers.study.create_study_result")
async def test_generate_plan(
    mock_create,
    mock_set_cache,
    mock_get_cache,
    mock_llm,
    client
):
    mock_get_cache.return_value = None
    mock_llm.return_value = "Day 1: Introduction\nDay 2: Basics\n..."
    
    mock_db_result = AsyncMock()
    mock_db_result.id = 3
    mock_db_result.topic = "Machine Learning"
    mock_db_result.mode = "plan"
    mock_db_result.result = "Day 1: Introduction\nDay 2: Basics\n..."
    mock_db_result.created_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_create.return_value = mock_db_result
    
    mock_set_cache.return_value = None
    
    response = await client.post(
        "/api/v1/study/generate",
        json={"topic": "Machine Learning", "mode": "plan"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["mode"] == "plan"


@pytest.mark.anyio
@patch("app.routers.study.get_study_results")
async def test_get_history(mock_get_results, client):
    mock_result = AsyncMock()
    mock_result.id = 1
    mock_result.topic = "Test Topic"
    mock_result.mode = "summary"
    mock_result.result = "Test result"
    mock_result.created_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_get_results.return_value = [mock_result]
    
    response = await client.get("/api/v1/study/history")
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1


@pytest.mark.anyio
@patch("app.routers.study.get_study_results_by_topic")
async def test_get_history_by_topic(mock_get_results, client):
    mock_result = AsyncMock()
    mock_result.id = 1
    mock_result.topic = "Python"
    mock_result.mode = "summary"
    mock_result.result = "Python content"
    mock_result.created_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_get_results.return_value = [mock_result]
    
    response = await client.get("/api/v1/study/history/Python")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["topic"] == "Python"


@pytest.mark.anyio
@patch("app.routers.study.get_study_results_by_topic")
async def test_get_history_by_topic_not_found(mock_get_results, client):
    mock_get_results.return_value = []
    
    response = await client.get("/api/v1/study/history/NonexistentTopic")
    
    assert response.status_code == 404


@pytest.mark.anyio
async def test_generate_invalid_mode(client):
    response = await client.post(
        "/api/v1/study/generate",
        json={"topic": "Test", "mode": "invalid"}
    )
    
    assert response.status_code == 422


@pytest.mark.anyio
async def test_generate_empty_topic(client):
    response = await client.post(
        "/api/v1/study/generate",
        json={"topic": "", "mode": "summary"}
    )
    
    assert response.status_code == 422
