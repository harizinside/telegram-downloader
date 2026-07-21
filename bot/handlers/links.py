from __future__ import annotations

import asyncio
import logging
import shutil
import uuid
from pathlib import Path
from typing import Optional

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from bot import downloader, messages
from bot.config import Settings
from bot.platforms import display_label, extract_url
from bot.states import DownloadFlow

logger = logging.getLogger(__name__)

router = Router(name="links")


@router.message(StateFilter(DownloadFlow.downloading))
async def handle_busy(message: Message) -> None:
    await message.answer(messages.busy_downloading())


@router.message(StateFilter(DownloadFlow.awaiting_cookies))
async def handle_cookies(
    message: Message,
    state: FSMContext,
    settings: Settings,
    semaphore: asyncio.Semaphore,
) -> None:
    data = await state.get_data()
    url = data.get("pending_url")
    label = data.get("pending_label", "link")
    if not url:
        await state.clear()
        await message.answer(messages.error_generic())
        return

    settings.download_dir.mkdir(parents=True, exist_ok=True)
    cookie_path = settings.download_dir / f"cookies-{uuid.uuid4().hex}.txt"
    try:
        if message.document is not None:
            await message.bot.download(message.document, destination=cookie_path)
        elif message.text:
            cookie_path.write_text(message.text, encoding="utf-8")
        else:
            await message.answer(messages.invalid_cookies())
            return
        cookie_path.chmod(0o600)

        status = await message.answer(messages.starting())
        await _run_download(message, state, settings, semaphore, url, label, status, cookiefile=cookie_path)
    finally:
        cookie_path.unlink(missing_ok=True)


@router.message()
async def handle_link(
    message: Message,
    state: FSMContext,
    settings: Settings,
    semaphore: asyncio.Semaphore,
) -> None:
    url = extract_url(message.text or "")
    if url is None:
        await message.answer(messages.not_a_link())
        return

    label = display_label(url)
    status = await message.answer(messages.starting())
    await _run_download(message, state, settings, semaphore, url, label, status)


async def _run_download(
    message: Message,
    state: FSMContext,
    settings: Settings,
    semaphore: asyncio.Semaphore,
    url: str,
    label: str,
    status: Message,
    cookiefile: Optional[Path] = None,
) -> None:
    await state.set_state(DownloadFlow.downloading)
    out_dir = settings.download_dir / f"{message.from_user.id}-{uuid.uuid4().hex}"
    acquired = False
    needs_cookies = False
    try:
        if semaphore.locked():
            await status.edit_text(messages.queued())
        await semaphore.acquire()
        acquired = True

        await status.edit_text(messages.downloading(label))
        path = await downloader.download(
            url,
            out_dir,
            timeout=settings.download_timeout_seconds,
            max_size_mb=settings.max_video_size_mb,
            cookiefile=cookiefile,
        )

        await status.edit_text(messages.uploading())
        await message.answer_video(FSInputFile(path), supports_streaming=True)
        await status.delete()
    except downloader.AuthRequiredError:
        if cookiefile is not None:
            await status.edit_text(messages.error_cookies_failed())
        else:
            needs_cookies = True
            await state.update_data(pending_url=url, pending_label=label)
            await state.set_state(DownloadFlow.awaiting_cookies)
            await status.edit_text(messages.ask_for_cookies())
    except downloader.UnsupportedError:
        await status.edit_text(messages.error_unsupported())
    except downloader.UnavailableError:
        await status.edit_text(messages.error_unavailable())
    except downloader.DownloadTimeoutError:
        await status.edit_text(messages.error_timeout())
    except downloader.TooLargeError:
        await status.edit_text(messages.error_too_large())
    except Exception:
        logger.exception("Unexpected error while handling link for chat %s", message.chat.id)
        await status.edit_text(messages.error_generic())
    finally:
        if acquired:
            semaphore.release()
        if not needs_cookies:
            await state.clear()
        await asyncio.to_thread(shutil.rmtree, out_dir, ignore_errors=True)
