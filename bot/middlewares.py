from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User as TgUser

from bot.db.base import session_factory
from bot.db import repo
from bot.i18n import t


class DbSessionMiddleware(BaseMiddleware):
    """Открывает сессию БД на каждый апдейт и коммитит при успехе."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with session_factory() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise


class UserMiddleware(BaseMiddleware):
    """Гарантирует наличие пользователя в БД, прокидывает user/lang, блокирует забаненных.

    Регистрируется на наблюдателях message/callback_query, где уже доступны
    event_from_user (его проставляет встроенный UserContextMiddleware) и сессия БД.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        if tg_user is None or tg_user.is_bot:
            return await handler(event, data)

        session = data["session"]
        user = await repo.get_or_create_user(
            session, tg_user.id, tg_user.username, tg_user.full_name
        )
        data["user"] = user
        data["lang"] = user.lang

        if user.is_banned:
            await self._notify_banned(event, user.lang)
            return None  # обрываем обработку забаненного

        return await handler(event, data)

    @staticmethod
    async def _notify_banned(event: TelegramObject, lang: str) -> None:
        if isinstance(event, Message):
            await event.answer(t("banned", lang))
        elif isinstance(event, CallbackQuery):
            await event.answer(t("banned", lang), show_alert=True)
