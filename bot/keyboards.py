from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.platforms import FACEBOOK, INSTAGRAM, TIKTOK, X


def platform_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🐦 Twitter (X)", callback_data=f"platform:{X.command}")],
            [InlineKeyboardButton(text="📘 Facebook", callback_data=f"platform:{FACEBOOK.command}")],
            [InlineKeyboardButton(text="🎵 TikTok", callback_data=f"platform:{TIKTOK.command}")],
            [InlineKeyboardButton(text="📸 Instagram", callback_data=f"platform:{INSTAGRAM.command}")],
        ]
    )
