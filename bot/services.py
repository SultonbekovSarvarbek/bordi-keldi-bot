from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db import repo
from bot.db.models import Trip
from bot.i18n import t
from bot.keyboards.inline import contact_button
from bot.utils.cards import render_trip

log = logging.getLogger(__name__)


async def _safe_send(bot: Bot, chat_id: int, text: str, **kwargs: object) -> bool:
    """Отправка с обработкой ошибок: не роняем рассылку из-за одного получателя."""
    try:
        await bot.send_message(chat_id, text, **kwargs)
        return True
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        try:
            await bot.send_message(chat_id, text, **kwargs)
            return True
        except TelegramAPIError:
            return False
    except TelegramAPIError as e:
        # Пользователь заблокировал бота, чат не найден и т.п. — просто пропускаем.
        log.info("Не доставлено %s: %s", chat_id, e)
        return False


async def notify_subscribers(
    bot: Bot, session: AsyncSession, trip: Trip, author_username: str | None = None
) -> int:
    """Мгновенная рассылка нового объявления подходящим подписчикам."""
    subscribers = await repo.matching_subscribers(session, trip)
    delivered = 0
    for chat_id, lang in subscribers:
        text = t("new_match", lang) + "\n\n" + render_trip(trip, lang, author_username)
        ok = await _safe_send(
            bot,
            chat_id,
            text,
            reply_markup=contact_button(trip.contact, lang, author_username),
        )
        delivered += int(ok)
        await asyncio.sleep(0.05)  # мягкий троттлинг
    log.info("Объявление %s: доставлено %s/%s", trip.id, delivered, len(subscribers))
    return delivered


async def post_to_group(bot: Bot, trip: Trip, author_username: str | None = None) -> None:
    """Опциональный дубль объявления в основную группу (узбекский по умолчанию)."""
    if settings.group_id is None:
        return
    text = render_trip(trip, "uz", author_username)
    await _safe_send(
        bot,
        settings.group_id,
        text,
        reply_markup=contact_button(trip.contact, "uz", author_username),
    )
