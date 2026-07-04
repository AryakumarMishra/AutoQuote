"""
Wrapper around Qwen Cloud's OpenAI-compatible endpoint.

Qwen Cloud exposes an OpenAI-compatible chat completions API, so we reuse
the official `openai` SDK and just point it at Alibaba's base URL. Every
call in this file is JSON-mode: we ask the model to return a single JSON
object and nothing else, which keeps the rest of the pipeline simple and
avoids brittle regex-parsing of free-text LLM output.

Verify exact model IDs (qwen-turbo / qwen-plus / qwen-max, or newer
versioned names) against the current Qwen Cloud / Model Studio docs before
the hackathon deadline -- provider model names shift over time and the
config.py defaults may need a bump.
"""

import json
from openai import OpenAI
from app.config import settings

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.qwen_base_url,
        )
    return _client


def call_qwen_json(model: str, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> dict:
    """Call Qwen Cloud and parse the response as JSON.

    Raises if the model doesn't return valid JSON -- callers should catch
    and route to human review rather than silently guessing.
    """
    client = get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content
    return json.loads(content)