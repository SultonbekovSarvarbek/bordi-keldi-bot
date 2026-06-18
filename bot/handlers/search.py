from __future__ import annotations

from datetime import date, timedelta

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_calendar.schemas import SimpleCalAct, SimpleCalendarCallback
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db import repo
from bot.db.models import Direction
from bot.i18n import t
from bot.keyboards import inline, reply
from bot.states import Search
from bot.utils.calendar import make_calendar
from bot.utils.cards import render_trip
from bot.utils.dates import parse_date, today

router = Router(name="search")
router.message.filter(F.chat.type == "private")


async def search_entry(message: Message, state: FSMContext, lang: str) -> None:
    """Точка входа в поиск (вызывается из nav-роутера)."""
    await state.clear()
    await state.set_state(Search.direction)
    await message.answer(t("search_direction", lang), reply_markup=inline.directions(lang, "sdir"))


@router.callback_query(Search.direction, F.data.startswith("sdir:"))
async def search_direction(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    direction = Direction(call.data.split(":", 1)[1])
    await state.update_data(direction=direction.value)
    await state.set_state(Search.date)
    # Текстовая подсказка + кнопка «Все», затем инлайн-календарь.
    await call.message.edit_text(t("search_date", lang), reply_markup=inline.search_all(lang))
    now = today()
    await call.message.answer(
        t("post_date_pick", lang),
        reply_markup=await make_calendar(lang).start_calendar(now.year, now.month),
    )
    await call.answer()


def _window(d: date) -> tuple[date, date]:
    w = timedelta(days=settings.search_date_window)
    return d - w, d + w


async def _run_search(
    message: Message,
    session: AsyncSession,
    lang: str,
    direction: Direction,
    date_from: date | None,
    date_to: date | None,
) -> None:
    trips = await repo.search_trips(
        session, direction, date_from, date_to, today(), settings.search_limit
    )
    if not trips:
        await message.answer(
            t("search_empty", lang), reply_markup=inline.subscribe_offer(direction, lang)
        )
        return
    await message.answer(t("search_results", lang, count=len(trips)))
    for trip in trips:
        uname = trip.user.username if trip.user else None
        await message.answer(
            render_trip(trip, lang, uname),
            reply_markup=inline.contact_button(trip.contact, lang, uname),
        )


# --- Поиск по дате/слову, введённым текстом ---
@router.message(Search.date, F.text)
async def search_date_text(
    message: Message, state: FSMContext, session: AsyncSession, lang: str
) -> None:
    data = await state.get_data()
    direction = Direction(data["direction"])
    raw = message.text.strip().casefold()

    all_word = t("search_all_word", lang).casefold()
    if raw in {all_word, "все", "hammasi", "all"}:
        date_from = date_to = None
    else:
        parsed = parse_date(message.text)
        if parsed is None:
            await message.answer(t("post_date_invalid", lang))
            return
        date_from, date_to = _window(parsed)

    await state.clear()
    await _run_search(message, session, lang, direction, date_from, date_to)


# --- Кнопка «Все» ---
@router.callback_query(Search.date, F.data == "search_all")
async def search_all_btn(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, lang: str
) -> None:
    data = await state.get_data()
    direction = Direction(data["direction"])
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await _run_search(call.message, session, lang, direction, None, None)
    await call.answer()


# --- Выбор даты в календаре ---
@router.callback_query(Search.date, SimpleCalendarCallback.filter())
async def search_date_calendar(
    call: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
    session: AsyncSession,
    lang: str,
) -> None:
    if callback_data.act == SimpleCalAct.cancel:
        await state.clear()
        await call.message.delete_reply_markup()
        await call.message.answer(t("cancelled", lang), reply_markup=reply.main_menu(lang))
        await call.answer()
        return

    selected, picked = await make_calendar(lang).process_selection(call, callback_data)
    if not selected:
        try:
            await call.answer()
        except TelegramBadRequest:
            pass
        return

    data = await state.get_data()
    direction = Direction(data["direction"])
    await state.clear()
    date_from, date_to = _window(picked.date())
    await _run_search(call.message, session, lang, direction, date_from, date_to)
    await call.answer()
