from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.i18n import t
from bot.keyboards import inline
from bot.utils.cards import render_trip

router = Router(name="my_trips")
router.message.filter(F.chat.type == "private")


async def my_trips_entry(message: Message, session: AsyncSession, lang: str) -> None:
    """Точка входа «Мои объявления» (вызывается из nav-роутера)."""
    trips = await repo.my_active_trips(session, message.from_user.id)
    if not trips:
        await message.answer(t("my_empty", lang))
        return
    await message.answer(t("my_title", lang))
    for trip in trips:
        uname = trip.user.username if trip.user else None
        await message.answer(
            render_trip(trip, lang, uname), reply_markup=inline.my_trip_item(trip.id, lang)
        )


@router.callback_query(F.data.startswith("tripdel:"))
async def delete_trip(call: CallbackQuery, session: AsyncSession, lang: str) -> None:
    trip_id = int(call.data.split(":", 1)[1])
    ok = await repo.deactivate_trip(session, trip_id, user_id=call.from_user.id)
    if ok:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.answer(t("my_deleted", lang))
    else:
        await call.answer(t("admin_not_found", lang), show_alert=True)
