from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot import messages

router = Router(name="commands")


@router.message(Command("start", "help"))
async def cmd_start(message: Message) -> None:
    await message.answer(messages.welcome())
