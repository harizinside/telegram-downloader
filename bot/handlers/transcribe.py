from __future__ import annotations

import asyncio
import logging
import shutil
import uuid
from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from bot import messages, transcriber
from bot.config import Settings
from bot.states import DownloadFlow

logger = logging.getLogger(__name__)

router = Router(name="transcribe")

_MAX_TELEGRAM_TEXT_LEN = 3500  # safety margin under Telegram's 4096-char message cap

_ACCEPTED_EXTS = {"flac", "mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "wav", "webm"}

_EXT_BY_MIME = {
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/mp4": "m4a",
    "audio/x-m4a": "m4a",
    "audio/aac": "m4a",
    "audio/ogg": "ogg",
    "audio/opus": "ogg",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/wave": "wav",
    "audio/webm": "webm",
    "audio/flac": "flac",
    "audio/x-flac": "flac",
}


def _resolve_extension(message: Message) -> str | None:
    if message.voice is not None:
        return "ogg"
    if message.audio is not None:
        mime = (message.audio.mime_type or "").split(";")[0].strip().lower()
        ext = _EXT_BY_MIME.get(mime)
        if ext is None and message.audio.file_name:
            ext = Path(message.audio.file_name).suffix.lstrip(".").lower() or None
        return ext
    if message.document is not None:
        mime = (message.document.mime_type or "").split(";")[0].strip().lower()
        if not mime.startswith("audio/"):
            return None
        ext = _EXT_BY_MIME.get(mime)
        if ext is None and message.document.file_name:
            ext = Path(message.document.file_name).suffix.lstrip(".").lower() or None
        return ext
    return None


@router.message(Command("transcribe"))
async def cmd_transcribe(message: Message, state: FSMContext, settings: Settings) -> None:
    if not settings.groq_api_key:
        await message.answer(messages.error_transcription_not_configured())
        return
    await state.set_state(DownloadFlow.awaiting_voice_note)
    await message.answer(messages.transcribe_ask_audio())


@router.message(StateFilter(DownloadFlow.awaiting_voice_note), F.voice | F.audio | F.document)
async def handle_audio(
    message: Message,
    state: FSMContext,
    settings: Settings,
    bot: Bot,
    transcribe_semaphore: asyncio.Semaphore,
) -> None:
    media = message.voice or message.audio or message.document

    if message.document is not None:
        mime = (message.document.mime_type or "").split(";")[0].strip().lower()
        if not mime.startswith("audio/"):
            await message.answer(messages.error_not_audio())
            return

    ext = _resolve_extension(message)
    if ext is None or ext not in _ACCEPTED_EXTS:
        await message.answer(messages.error_unsupported_audio_format())
        return

    max_mb = settings.effective_max_audio_mb
    file_size = media.file_size or 0
    if file_size and file_size > max_mb * 1024 * 1024:
        await message.answer(messages.error_audio_too_large(max_mb))
        return

    await state.set_state(DownloadFlow.downloading)
    status = await message.answer(messages.transcribing())

    out_dir = settings.download_dir / f"{message.from_user.id}-{uuid.uuid4().hex}"
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"audio.{ext}"
    acquired = False
    try:
        if transcribe_semaphore.locked():
            await status.edit_text(messages.queued())
        await transcribe_semaphore.acquire()
        acquired = True

        await bot.download(media, destination=dest)

        text = await transcriber.transcribe(
            dest,
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            timeout=settings.transcription_timeout_seconds,
        )

        if not text:
            await status.edit_text(messages.error_no_speech_detected())
        elif len(text) <= _MAX_TELEGRAM_TEXT_LEN:
            await status.delete()
            await message.answer(text)
        else:
            await status.delete()
            await message.answer_document(
                BufferedInputFile(text.encode("utf-8"), filename="transcript.txt"),
                caption=messages.transcript_too_long_caption(),
            )
    except transcriber.NotConfiguredError:
        await status.edit_text(messages.error_transcription_not_configured())
    except transcriber.RateLimitedError:
        await status.edit_text(messages.error_transcription_busy())
    except transcriber.UnsupportedAudioError:
        await status.edit_text(messages.error_unsupported_audio_format())
    except transcriber.TranscriptionTimeoutError:
        await status.edit_text(messages.error_transcription_timeout())
    except transcriber.GroqAPIError:
        logger.exception("Groq API error while transcribing for chat %s", message.chat.id)
        await status.edit_text(messages.error_transcription_failed())
    except Exception:
        logger.exception("Unexpected error while transcribing for chat %s", message.chat.id)
        await status.edit_text(messages.error_generic())
    finally:
        if acquired:
            transcribe_semaphore.release()
        await state.clear()
        await asyncio.to_thread(shutil.rmtree, out_dir, ignore_errors=True)


@router.message(StateFilter(DownloadFlow.awaiting_voice_note))
async def handle_awaiting_voice_note_wrong_type(message: Message) -> None:
    await message.answer(messages.error_not_audio())
