"""
LLM service for generating study content via OpenRouter API.
"""

import asyncio
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemma-4-26b-a4b-it:free"
MAX_RETRIES = 3
RETRY_DELAY = 5


def build_prompt(topic: str, mode: str) -> str:
    """Build a structured prompt based on the study mode."""
    prompts = {
        "summary": f"Give me a concise study summary of: {topic}",
        "quiz": f"Generate 5 multiple choice quiz questions about: {topic}",
        "plan": f"Create a structured 7-day study plan for learning: {topic}"
    }
    return prompts.get(mode, f"Provide information about: {topic}")


async def generate_study_content(topic: str, mode: str) -> str:
    """
    Generate study content using OpenRouter API.
    
    Args:
        topic: The topic to generate content for
        mode: The study mode (summary, quiz, or plan)
        
    Returns:
        Generated text content from the LLM
        
    Raises:
        ValueError: If API key is not configured or all retries exhausted
        httpx.HTTPError: If API request fails
    """
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not configured")

    prompt = build_prompt(topic, mode)
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://studymate-api.com",
        "X-Title": "StudyMate API"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert tutor. Provide clear, well-structured educational content."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    async with httpx.AsyncClient() as client:
        for attempt in range(MAX_RETRIES):
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", RETRY_DELAY * (attempt + 1)))
                logger.warning(f"Rate limited, retrying in {retry_after}s (attempt {attempt + 1}/{MAX_RETRIES})")
                await asyncio.sleep(retry_after)
                continue

            response.raise_for_status()
            break
        else:
            raise ValueError(f"Rate limited after {MAX_RETRIES} retries. Try again later.")
        
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0].get("message", {}).get("content", "")
            if content:
                return content.strip()
        
        raise ValueError("No content received from LLM API")
