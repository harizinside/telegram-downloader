from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import messages
from bot.keyboards import platform_keyboard
from bot.platforms import PLATFORMS, Platform
from bot.states import DownloadFlow

router = Router(name="commands")


async def _start_awaiting_link(
    target: Message | CallbackQuery, state: FSMContext, platform: Platform
) -> None:
    await state.set_state(DownloadFlow.awaiting_link)
    await state.update_data(platform=platform.command)
    text = messages.ask_for_link(platform)
    if isinstance(target, CallbackQuery):
        await target.answer()
        await target.message.edit_text(text)
    else:
        await target.answer(text)


@router.message(Command("start", "help"))
async def cmd_start(message: Message) -> None:
    await message.answer(messages.welcome(), reply_markup=platform_keyboard())


@router.message(StateFilter(DownloadFlow.downloading), Command("fb", "x", "ig", "tk"))
async def cmd_blocked_while_downloading(message: Message) -> None:
    await message.answer(messages.busy_downloading())


@router.callback_query(StateFilter(DownloadFlow.downloading), F.data.startswith("platform:"))
async def callback_blocked_while_downloading(callback: CallbackQuery) -> None:
    await callback.answer(messages.busy_downloading(), show_alert=True)


@router.message(Command("fb", "x", "ig", "tk"))
async def cmd_platform(message: Message, state: FSMContext) -> None:
    command = message.text.lstrip("/").split()[0].split("@")[0]
    platform = PLATFORMS.get(command)
    if platform is None:
        return
    await _start_awaiting_link(message, state, platform)


@router.callback_query(F.data.startswith("platform:"))
async def callback_platform(callback: CallbackQuery, state: FSMContext) -> None:
    command = callback.data.split(":", 1)[1]
    platform = PLATFORMS.get(command)
    if platform is None:
        await callback.answer()
        return
    await _start_awaiting_link(callback, state, platform)
