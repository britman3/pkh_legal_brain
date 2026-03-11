import httpx
from app.config import settings
from typing import Tuple, Dict

ANTHROPIC = "https://api.anthropic.com/v1/messages"
OPENAI_RESPONSES = "https://api.openai.com/v1/responses"
GOOGLE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

async def _anthropic_call(prompt: dict) -> Tuple[str, Dict]:
    headers = {
        "x-api-key": settings.ANTHROPIC_API_KEY or "",
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "system": prompt["system"],
        "messages": [{"role": "user", "content": prompt["user"]}],
        "temperature": 0.2,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(ANTHROPIC, headers=headers, json=payload)
        if r.status_code != 200:
            print(f"Anthropic error: {r.status_code} - {r.text}")
        r.raise_for_status()
        data = r.json()
        usage = data.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        print(f"✅ Anthropic usage - Input: {input_tokens} tokens, Output: {output_tokens} tokens, Total: {input_tokens + output_tokens} tokens")
        
        usage_stats = {
            "anthropic_input_tokens": input_tokens,
            "anthropic_output_tokens": output_tokens,
            "openai_input_tokens": 0,
            "openai_output_tokens": 0
        }
        return data["content"][0]["text"], usage_stats

async def _openai_call(prompt: dict) -> Tuple[str, Dict]:
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY or ''}"}
    payload = {
        "model": "gpt-5",
        "messages": [
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        "temperature": 0.2,
        "max_completion_tokens": 4000,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(OPENAI_RESPONSES, headers=headers, json=payload)
        if r.status_code != 200:
            print(f"OpenAI error: {r.status_code} - {r.text}")
        r.raise_for_status()
        data = r.json()
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        print(f"✅ OpenAI usage - Prompt: {prompt_tokens} tokens, Completion: {completion_tokens} tokens, Total: {total_tokens} tokens")
        
        usage_stats = {
            "anthropic_input_tokens": 0,
            "anthropic_output_tokens": 0,
            "openai_input_tokens": prompt_tokens,
            "openai_output_tokens": completion_tokens
        }
        return data["choices"][0]["message"]["content"], usage_stats

async def _gemini_call(prompt: dict) -> Tuple[str, Dict]:
    params = {"key": settings.GOOGLE_API_KEY or ""}
    payload = {
        "contents": [{"parts": [{"text": prompt["system"] + "\n\n" + prompt["user"]}]}]
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(GOOGLE, params=params, json=payload)
        if r.status_code != 200:
            print(f"Gemini error: {r.status_code} - {r.text}")
        r.raise_for_status()
        data = r.json()
        usage = data.get("usageMetadata", {})
        prompt_tokens = usage.get("promptTokenCount", 0)
        completion_tokens = usage.get("candidatesTokenCount", 0)
        total_tokens = usage.get("totalTokenCount", 0)
        print(f"✅ Gemini usage - Prompt: {prompt_tokens} tokens, Completion: {completion_tokens} tokens, Total: {total_tokens} tokens")
        
        usage_stats = {
            "anthropic_input_tokens": 0,
            "anthropic_output_tokens": 0,
            "openai_input_tokens": 0,
            "openai_output_tokens": 0
        }
        return data["candidates"][0]["content"]["parts"][0]["text"], usage_stats

async def analyze_with_router(prompt: dict, meta: dict) -> Tuple[str, Dict]:
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
