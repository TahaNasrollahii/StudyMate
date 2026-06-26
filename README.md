# StudyMate API

An AI-powered study assistant backend that generates summaries, quizzes, and study plans using LLM technology.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://docker.com)

## Overview

StudyMate API is a REST API that lets users submit a topic and receive AI-generated study content powered by an LLM via OpenRouter. Results are persisted in PostgreSQL and cached with Redis for optimal performance.

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - async ORM with asyncpg driver
- **Redis** - Caching layer for repeated topic requests
- **OpenRouter API** - LLM integration (Mistral 7B free tier)
- **Pydantic v2** - Data validation and settings management
- **pytest** - Async testing framework
- **Docker** - Containerized deployment

## Project Structure

```
studymate/
├── app/
│   ├── main.py          # FastAPI application setup
│   ├── config.py        # Settings management
│   ├── database.py      # Database connection
│   ├── redis_client.py  # Redis connection
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   └── crud/            # Database operations
├── tests/               # Test suite
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/TahaNasrollahii/StudyMate.git
   cd StudyMate
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start services**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose up -d db redis
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

1. **Build and start all services**
   ```bash
   docker-compose up -d
   ```

2. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check

```
GET /api/v1/study/health
```

**Response:**
```json
{
  "status": "ok"
}
```

### Generate Study Content

```
POST /api/v1/study/generate
```

**Request Body:**
```json
{
  "topic": "Python decorators",
  "mode": "summary"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `topic` | string | Yes | The subject you want to study (e.g., "Python decorators", "machine learning basics", "SQL joins"). Min 1, max 200 characters. |
| `mode` | string | Yes | The type of study content to generate (see modes below). |

**Modes:**

| Mode | Description | Example Output |
|------|-------------|----------------|
| `summary` | Concise study summary covering key concepts, principles, and quick reference | Overview with bullet points, tables, and key takeaways |
| `quiz` | 5 multiple choice questions with answers | Q&A format with 4 options each and correct answer |
| `plan` | Structured 7-day study plan with daily goals | Day-by-day schedule with activities and deliverables |

**Response (201 Created):**
```json
{
  "id": 1,
  "topic": "Python decorators",
  "mode": "summary",
  "result": "Python decorators are a powerful feature...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Study History

```
GET /api/v1/study/history
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100) - Maximum records to return

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "topic": "Python decorators",
      "mode": "summary",
      "result": "...",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get History by Topic

```
GET /api/v1/study/history/{topic}
```

**Response:** Same as study history, filtered by topic.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:password@localhost:5432/studymate` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `OPENROUTER_API_KEY` | OpenRouter API key | - |
| `APP_NAME` | Application name | `StudyMate API` |
| `APP_VERSION` | Application version | `1.0.0` |

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_study.py::test_health_check
```

## Development

### Adding New Endpoints

1. Define Pydantic schemas in `app/schemas/`
2. Add CRUD operations in `app/crud/`
3. Create service functions in `app/services/`
4. Add router endpoints in `app/routers/`
5. Write tests in `tests/`

### Code Quality

- All endpoints are async
- Use dependency injection for DB and Redis
- Pydantic v2 for data validation
- Proper HTTP status codes
- Comprehensive error handling
- Business logic in services, not routers

## License

MIT License
