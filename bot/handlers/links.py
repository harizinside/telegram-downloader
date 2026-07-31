from __future__ import annotations

import asyncio
import logging
import shutil
import uuid

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import downloader, messages
from bot.config import Settings
from bot.platforms import display_label, extract_url, is_youtube
from bot.states import DownloadFlow

logger = logging.getLogger(__name__)

router = Router(name="links")


def _format_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Video", callback_data="dl_video"),
                InlineKeyboardButton(text="Audio (MP3)", callback_data="dl_audio"),
            ]
        ]
    )


async def _do_download(
    message: Message,
    state: FSMContext,
    settings: Settings,
    semaphore: asyncio.Semaphore,
    url: str,
    audio_only: bool,
) -> None:
    label = display_label(url)

    await state.set_state(DownloadFlow.downloading)
    status = await message.answer(messages.starting())

    out_dir = settings.download_dir / f"{message.from_user.id}-{uuid.uuid4().hex}"
    acquired = False
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
            audio_only=audio_only,
        )

        await status.edit_text(messages.uploading())
        if audio_only:
            await message.answer_audio(FSInputFile(path), title=path.stem)
        else:
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
        logger.exception("Unexpected error while handling link for chat %s", message.chat.id)
        await status.edit_text(messages.error_generic())
    finally:
        if acquired:
            semaphore.release()
        await state.clear()
        await asyncio.to_thread(shutil.rmtree, out_dir, ignore_errors=True)


@router.message(StateFilter(DownloadFlow.downloading))
async def handle_busy(message: Message) -> None:
    await message.answer(messages.busy_downloading())


@router.message(StateFilter(DownloadFlow.choosing_format))
async def handle_link_while_choosing(
    message: Message,
    state: FSMContext,
    settings: Settings,
    semaphore: asyncio.Semaphore,
) -> None:
    url = extract_url(message.text or "")
    if url is None:
        await message.answer(messages.not_a_link())
        return

    if is_youtube(url):
        await state.update_data(url=url)
        await message.answer(messages.choose_format(), reply_markup=_format_keyboard())
    else:
        await _do_download(message, state, settings, semaphore, url, audio_only=False)


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

    if is_youtube(url):
        await state.set_state(DownloadFlow.choosing_format)
        await state.update_data(url=url)
        await message.answer(messages.choose_format(), reply_markup=_format_keyboard())
    else:
        await _do_download(message, state, settings, semaphore, url, audio_only=False)


@router.callback_query(F.data == "dl_video", StateFilter(DownloadFlow.choosing_format))
async def cb_download_video(
    query: CallbackQuery,
    state: FSMContext,
    settings: Settings,
    semaphore: asyncio.Semaphore,
) -> None:
    await query.answer()
    data = await state.get_data()
    url = data.get("url")
    if not url or not query.message:
        await state.clear()
        return
    await query.message.delete()
    await _do_download(query.message, state, settings, semaphore, url, audio_only=False)


@router.callback_query(F.data == "dl_audio", StateFilter(DownloadFlow.choosing_format))
async def cb_download_audio(
    query: CallbackQuery,
    state: FSMContext,
    settings: Settings,
    semaphore: asyncio.Semaphore,
) -> None:
    await query.answer()
    data = await state.get_data()
    url = data.get("url")
    if not url or not query.message:
        await state.clear()
        return
    await query.message.delete()
    await _do_download(query.message, state, settings, semaphore, url, audio_only=True)
