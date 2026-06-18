from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.config import settings
from bot.i18n import TRANSLATIONS


class MenuButton(BaseFilter):
    """Совпадение текста сообщения с локализованной кнопкой меню (в любом языке)."""

    def __init__(self, key: str) -> None:
        self.variants = {TRANSLATIONS[lang].get(key) for lang in TRANSLATIONS}

    async def __call__(self, message: Message) -> bool:
        return message.text in self.variants


class IsAdmin(BaseFilter):
    """Пользователь входит в список администраторов из конфига."""

    async def __call__(self, message: Message) -> bool:
        return message.from_user is not None and message.from_user.id in settings.admin_ids
