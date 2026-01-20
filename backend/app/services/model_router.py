
import httpx
from app.config import settings

ANTHROPIC = "https://api.anthropic.com/v1/messages"
OPENAI = "https://api.openai.com/v1/chat/completions"
GOOGLE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

async def _anthropic_call(prompt: dict) -> str:
    headers = {
        "x-api-key": settings.ANTHROPIC_API_KEY or "",
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4000,
        "system": prompt["system"],
        "messages": [{"role": "user", "content": prompt["user"]}],
        "temperature": 0.2,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(ANTHROPIC, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["content"][0]["text"]

async def _openai_call(prompt: dict) -> str:
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY or ''}"}
    payload = {
        "model": "gpt-5",
        "messages": [
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        "temperature": 0.2,
        "max_tokens": 4000,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(OPENAI, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

async def _gemini_call(prompt: dict) -> str:
    params = {"key": settings.GOOGLE_API_KEY or ""}
    payload = {
        "contents": [{"parts": [{"text": prompt["system"] + "\n\n" + prompt["user"]}]}]
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(GOOGLE, params=params, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

async def analyze_with_router(prompt: dict, meta: dict) -> str:
    size = meta.get("size", 0)
    try:
        if size > 800 and settings.GOOGLE_API_KEY:
            return await _gemini_call(prompt)
        if settings.ANTHROPIC_API_KEY:
            return await _anthropic_call(prompt)
        if settings.OPENAI_API_KEY:
            return await _openai_call(prompt)
        raise RuntimeError("No LLM provider configured")
    except Exception:
        if settings.OPENAI_API_KEY:
            return await _openai_call(prompt)
        if settings.GOOGLE_API_KEY:
            return await _gemini_call(prompt)
        raise
