from __future__ import annotations

import asyncio
import logging
import re
import shutil
import uuid

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from bot import downloader, messages
from bot.config import Settings
from bot.platforms import extract_url
from bot.states import DownloadFlow

logger = logging.getLogger(__name__)

router = Router(name="tldv")

_TLDV_URL_RE = re.compile(r"https?://(?:www\.)?tldv\.io/app/meetings/[a-f0-9]+", re.I)


@router.message(Command("tldv"))
async def cmd_tldv(message: Message, state: FSMContext) -> None:
    await state.set_state(DownloadFlow.awaiting_tldv_token)
    await message.answer(messages.tldv_ask_token())


@router.message(StateFilter(DownloadFlow.awaiting_tldv_token))
async def handle_tldv_token(message: Message, state: FSMContext) -> None:
    token = (message.text or "").strip()
    if not token:
        await message.answer(messages.tldv_ask_token())
        return
    await state.update_data(tldv_token=token)
    await state.set_state(DownloadFlow.awaiting_tldv_url)
    await message.answer(messages.tldv_ask_url())


@router.message(StateFilter(DownloadFlow.awaiting_tldv_url))
async def handle_tldv_url(
    message: Message,
    state: FSMContext,
    settings: Settings,
    semaphore: asyncio.Semaphore,
) -> None:
    url = extract_url(message.text or "")
    if url is None or not _TLDV_URL_RE.match(url):
        await message.answer(messages.tldv_invalid_url())
        return

    data = await state.get_data()
    token = data.get("tldv_token")
    if not token:
        await state.set_state(DownloadFlow.awaiting_tldv_token)
        await message.answer(messages.tldv_ask_token())
        return

    await state.set_state(DownloadFlow.downloading)
    status = await message.answer(messages.starting())

    out_dir = settings.download_dir / f"{message.from_user.id}-{uuid.uuid4().hex}"
    acquired = False
    try:
        if semaphore.locked():
            await status.edit_text(messages.queued())
        await semaphore.acquire()
        acquired = True

        await status.edit_text(messages.downloading("tl;dv"))
        path = await downloader.download(
            url,
            out_dir,
            timeout=settings.download_timeout_seconds,
            max_size_mb=settings.max_video_size_mb,
            extractor_args={"tldv": {"token": [token]}},
        )

        await status.edit_text(messages.uploading())
        await message.answer_video(FSInputFile(path), supports_streaming=True)
        await status.delete()
    except downloader.UnsupportedError:
        await status.edit_text(messages.error_unsupported())
    except downloader.UnavailableError:
        await status.edit_text(messages.error_unavailable())
    except downloader.DownloadTimeoutError:
        await status.edit_text(messages.error_timeout())
    except downloader.TooLargeError:
        await status.edit_text(messages.error_too_large())
    except Exception:
        logger.exception("Unexpected error while handling tldv for chat %s", message.chat.id)
        await status.edit_text(messages.error_generic())
    finally:
        if acquired:
            semaphore.release()
        await state.clear()
        await asyncio.to_thread(shutil.rmtree, out_dir, ignore_errors=True)
