from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.config import Settings
from bot.handlers import commands, links, tldv, transcribe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_COMMANDS = [
    BotCommand(command="start", description="Mulai / cara pakai"),
    BotCommand(command="tldv", description="Download recording tl;dv (butuh bearer token)"),
    BotCommand(command="transcribe", description="Transcribe voice note/audio jadi teks"),
    BotCommand(command="help", description="Bantuan cara pakai bot"),
]


async def main() -> None:
    settings = Settings()
    settings.download_dir.mkdir(parents=True, exist_ok=True)

    api_server = TelegramAPIServer.from_base(settings.telegram_api_base_url)
    session = AiohttpSession(api=api_server)
    bot = Bot(token=settings.bot_token, session=session)

    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(commands.router)
    dispatcher.include_router(tldv.router)
    dispatcher.include_router(transcribe.router)
    dispatcher.include_router(links.router)

    semaphore = asyncio.Semaphore(settings.max_concurrent_downloads)
    transcribe_semaphore = asyncio.Semaphore(settings.max_concurrent_transcriptions)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(BOT_COMMANDS)
    await dispatcher.start_polling(
        bot,
        settings=settings,
        semaphore=semaphore,
        transcribe_semaphore=transcribe_semaphore,
    )


if __name__ == "__main__":
    asyncio.run(main())
