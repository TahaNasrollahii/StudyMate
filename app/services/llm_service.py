"""
LLM service for generating study content via OpenRouter API.
"""

import asyncio
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.3-70b-instruct:free"
MAX_RETRIES = 3
RETRY_DELAY = 5


def build_prompt(topic: str, mode: str) -> str:
    """Build a structured prompt based on the study mode."""
    prompts = {
        "summary": f"Give me a concise study summary of: {topic}",
        "quiz": f"Generate 5 multiple choice quiz questions about: {topic}",
        "plan": f"Create a structured 7-day study plan for learning: {topic}",
    }
    return prompts.get(mode, f"Provide information about: {topic}")


async def generate_study_content(topic: str, mode: str) -> str:
    """
    Generate study content using OpenRouter API.
    """
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not configured")

    prompt = build_prompt(topic, mode)
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://studymate-api.com",
        "X-Title": "StudyMate API",
    }
    payload = {
        "model": "google/gemma-4-26b-a4b-it:free",
        "messages": [
            {"role": "user", "content": f"You are an expert tutor. Provide clear, well-structured educational content.\n\n{prompt}"},
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENROUTER_API_URL, headers=headers, json=payload, timeout=15.0
        )
        
        # Try to parse JSON to get detailed error from OpenRouter if available
        data = {}
        try:
            data = response.json()
        except:
            pass

        if not response.is_success:
            logger.error(f"OpenRouter API error: {response.status_code} - {data}")
            raise ValueError(f"LLM API Error ({response.status_code}): {data.get('error', {}).get('message', 'Unknown error')}")
            
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0].get("message", {}).get("content", "")
            if content:
                return content.strip()
                
        logger.error(f"Invalid LLM response structure: {data}")
        raise ValueError(f"No content received from LLM API. Response: {data}")
