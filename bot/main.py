from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import Settings
from bot.handlers import commands, links

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = Settings()
    settings.download_dir.mkdir(parents=True, exist_ok=True)

    api_server = TelegramAPIServer.from_base(settings.telegram_api_base_url)
    session = AiohttpSession(api=api_server)
    bot = Bot(token=settings.bot_token, session=session)

    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(commands.router)
    dispatcher.include_router(links.router)

    semaphore = asyncio.Semaphore(settings.max_concurrent_downloads)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(
        bot,
        settings=settings,
        semaphore=semaphore,
    )


if __name__ == "__main__":
    asyncio.run(main())
