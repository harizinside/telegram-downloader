from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import aiohttp

logger = logging.getLogger(__name__)

_GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


class TranscriptionError(Exception):
    pass


class NotConfiguredError(TranscriptionError):
    pass


class TranscriptionTimeoutError(TranscriptionError):
    pass


class RateLimitedError(TranscriptionError):
    pass


class UnsupportedAudioError(TranscriptionError):
    pass


class GroqAPIError(TranscriptionError):
    pass


async def _call_groq(path: Path, api_key: str, model: str) -> str:
    audio_bytes = await asyncio.to_thread(path.read_bytes)
    form = aiohttp.FormData()
    form.add_field("model", model)
    form.add_field("file", audio_bytes, filename=path.name)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            _GROQ_TRANSCRIPTION_URL,
            data=form,
            headers={"Authorization": f"Bearer {api_key}"},
        ) as resp:
            if resp.status == 429:
                raise RateLimitedError()
            if resp.status == 400:
                raise UnsupportedAudioError(await resp.text())
            if resp.status >= 400:
                raise GroqAPIError(f"{resp.status}: {await resp.text()}")
            data = await resp.json()
            return (data.get("text") or "").strip()


async def transcribe(path: Path, api_key: str, model: str, timeout: float) -> str:
    if not api_key:
        raise NotConfiguredError()
    try:
        return await asyncio.wait_for(_call_groq(path, api_key, model), timeout=timeout)
    except asyncio.TimeoutError as exc:
        raise TranscriptionTimeoutError() from exc
    except aiohttp.ClientError as exc:
        raise GroqAPIError(str(exc)) from exc
