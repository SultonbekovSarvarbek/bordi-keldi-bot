from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_calendar.schemas import SimpleCalAct, SimpleCalendarCallback
from sqlalchemy.ext.asyncio import AsyncSession

from bot import services
from bot.db import repo
from bot.db.models import Direction, Trip, User
from bot.i18n import t
from bot.keyboards import inline, reply
from bot.states import PostTrip
from bot.utils import cities
from bot.utils.calendar import make_calendar
from bot.utils.cards import render_trip
from bot.utils.constants import CARGO_CUSTOM_PREFIX, CARGO_SEP, CITY_MANUAL
from bot.utils.dates import is_past, parse_date, today

router = Router(name="post")
router.message.filter(F.chat.type == "private")


async def _begin(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await state.set_state(PostTrip.direction)
    await message.answer(t("post_direction", lang), reply_markup=inline.directions(lang, "pdir"))


async def post_entry(message: Message, state: FSMContext, user: User, lang: str) -> None:
    """Точка входа в мастер подачи (вызывается из nav-роутера)."""
    # Перед первой публикацией показываем дисклеймер.
    if not user.seen_disclaimer:
        await state.clear()
        await message.answer(t("disclaimer", lang), reply_markup=inline.disclaimer(lang))
        return
    await _begin(message, state, lang)


@router.callback_query(F.data == "disc:ok")
async def accept_disclaimer(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, lang: str
) -> None:
    await repo.mark_disclaimer_seen(session, call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=None)
    await _begin(call.message, state, lang)
    await call.answer()


# --- Шаг 1: направление ---
@router.callback_query(PostTrip.direction, F.data.startswith("pdir:"))
async def step_direction(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    direction = Direction(call.data.split(":", 1)[1])
    await state.update_data(direction=direction.value)
    await state.set_state(PostTrip.from_city)
    await call.message.edit_text(
        t("post_from_city", lang),
        reply_markup=inline.cities(cities.from_cities(direction), lang, "pfrom"),
    )
    await call.answer()


# --- Шаг 2: город вылета ---
@router.callback_query(PostTrip.from_city, F.data.startswith("pfrom:"))
async def step_from_city(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    value = call.data.split(":", 1)[1]
    if value == CITY_MANUAL:
        await state.set_state(PostTrip.from_city_manual)
        await call.message.edit_text(t("post_city_manual_prompt", lang))
        await call.answer()
        return
    await _save_from_city(call.message, state, lang, value, edit=True)
    await call.answer()


@router.message(PostTrip.from_city_manual, F.text)
async def step_from_city_manual(message: Message, state: FSMContext, lang: str) -> None:
    await _save_from_city(message, state, lang, message.text.strip(), edit=False)


async def _save_from_city(
    message: Message, state: FSMContext, lang: str, city: str, *, edit: bool
) -> None:
    data = await state.update_data(from_city=city)
    direction = Direction(data["direction"])
    await state.set_state(PostTrip.to_city)
    kb = inline.cities(cities.to_cities(direction), lang, "pto")
    if edit:
        await message.edit_text(t("post_to_city", lang), reply_markup=kb)
    else:
        await message.answer(t("post_to_city", lang), reply_markup=kb)


# --- Шаг 3: город прилёта ---
@router.callback_query(PostTrip.to_city, F.data.startswith("pto:"))
async def step_to_city(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    value = call.data.split(":", 1)[1]
    if value == CITY_MANUAL:
        await state.set_state(PostTrip.to_city_manual)
        await call.message.edit_text(t("post_city_manual_prompt", lang))
        await call.answer()
        return
    await _save_to_city(call.message, state, lang, value, edit=True)
    await call.answer()


@router.message(PostTrip.to_city_manual, F.text)
async def step_to_city_manual(message: Message, state: FSMContext, lang: str) -> None:
    await _save_to_city(message, state, lang, message.text.strip(), edit=False)


async def _save_to_city(
    message: Message, state: FSMContext, lang: str, city: str, *, edit: bool
) -> None:
    await state.update_data(to_city=city)
    await state.set_state(PostTrip.depart_date)
    # Подсказка с форматом ручного ввода…
    if edit:
        await message.edit_text(t("post_date", lang))
    else:
        await message.answer(t("post_date", lang))
    # …и инлайн-календарь (можно выбрать дату или ввести текстом).
    await _send_calendar(message, lang)


async def _send_calendar(message: Message, lang: str) -> None:
    now = today()
    await message.answer(
        t("post_date_pick", lang),
        reply_markup=await make_calendar(lang).start_calendar(now.year, now.month),
    )


async def _save_date_and_continue(message: Message, state: FSMContext, lang: str, d) -> None:
    await state.update_data(depart_date=d.isoformat())
    await state.set_state(PostTrip.baggage)
    await message.answer(t("post_baggage", lang), reply_markup=inline.baggage(lang))


# --- Шаг 4: дата (ручной ввод текстом) ---
@router.message(PostTrip.depart_date, F.text)
async def step_date(message: Message, state: FSMContext, lang: str) -> None:
    parsed = parse_date(message.text)
    if parsed is None:
        await message.answer(t("post_date_invalid", lang))
        return
    if is_past(parsed):
        await message.answer(t("post_date_past", lang))
        return
    await _save_date_and_continue(message, state, lang, parsed)


# --- Шаг 4: дата (выбор в календаре) ---
@router.callback_query(PostTrip.depart_date, SimpleCalendarCallback.filter())
async def step_date_calendar(
    call: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
    lang: str,
) -> None:
    # Кнопку «Отмена» календаря трактуем как отмену всего мастера.
    if callback_data.act == SimpleCalAct.cancel:
        await state.clear()
        await call.message.delete_reply_markup()
        await call.message.answer(t("cancelled", lang), reply_markup=reply.main_menu(lang))
        await call.answer()
        return

    selected, picked = await make_calendar(lang).process_selection(call, callback_data)
    if not selected:
        # Навигация по месяцам/годам или служебные кнопки. process_selection часть
        # из них уже «закрыла», поэтому повторный answer защищаем от ошибки.
        try:
            await call.answer()
        except TelegramBadRequest:
            pass
        return

    if is_past(picked.date()):
        await call.answer()
        await call.message.answer(t("post_date_past", lang))
        await _send_calendar(call.message, lang)
        return

    await _save_date_and_continue(call.message, state, lang, picked.date())
    await call.answer()


# --- Шаг 5: багаж (кнопка или свободный ввод) ---
async def _goto_cargo(message: Message, state: FSMContext, lang: str, *, edit: bool) -> None:
    await state.set_state(PostTrip.cargo)
    await state.update_data(cargo_sel=[])  # выбранные пункты груза (мультивыбор)
    kb = inline.cargo(lang, [])
    if edit:
        await message.edit_text(t("post_cargo", lang), reply_markup=kb)
    else:
        await message.answer(t("post_cargo", lang), reply_markup=kb)


@router.callback_query(PostTrip.baggage, F.data.startswith("pbag:"))
async def step_baggage_btn(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.update_data(baggage=call.data.split(":", 1)[1])
    await _goto_cargo(call.message, state, lang, edit=True)
    await call.answer()


@router.message(PostTrip.baggage, F.text)
async def step_baggage_text(message: Message, state: FSMContext, lang: str) -> None:
    await state.update_data(baggage=message.text.strip())
    await _goto_cargo(message, state, lang, edit=False)


# --- Шаг 6: что готов взять (мультивыбор + свой вариант) ---
@router.callback_query(PostTrip.cargo, F.data.startswith("pcargo:"))
async def cargo_toggle(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    key = call.data.split(":", 1)[1]
    data = await state.get_data()
    sel = list(data.get("cargo_sel", []))
    if key in sel:
        sel.remove(key)
    else:
        sel.append(key)
    await state.update_data(cargo_sel=sel)
    await call.message.edit_reply_markup(reply_markup=inline.cargo(lang, sel))
    await call.answer()


@router.callback_query(PostTrip.cargo, F.data.startswith("pcargodel:"))
async def cargo_del_custom(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    i = int(call.data.split(":", 1)[1])
    data = await state.get_data()
    sel = list(data.get("cargo_sel", []))
    customs = [s for s in sel if s.startswith(CARGO_CUSTOM_PREFIX)]
    if 0 <= i < len(customs):
        sel.remove(customs[i])
        await state.update_data(cargo_sel=sel)
        await call.message.edit_reply_markup(reply_markup=inline.cargo(lang, sel))
    await call.answer()


@router.callback_query(PostTrip.cargo, F.data == "pcargo_add")
async def cargo_add_custom(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(PostTrip.cargo_custom)
    # Убираем клавиатуру у текущего сообщения и просим текст.
    await call.message.edit_text(t("cargo_custom_prompt", lang))
    await call.answer()


@router.message(PostTrip.cargo_custom, F.text)
async def cargo_custom_text(message: Message, state: FSMContext, lang: str) -> None:
    text = message.text.strip()[:40]
    data = await state.get_data()
    sel = list(data.get("cargo_sel", []))
    token = CARGO_CUSTOM_PREFIX + text
    if text and token not in sel:
        sel.append(token)
    await state.update_data(cargo_sel=sel)
    await state.set_state(PostTrip.cargo)
    await message.answer(t("post_cargo", lang), reply_markup=inline.cargo(lang, sel))


@router.callback_query(PostTrip.cargo, F.data == "pcargo_done")
async def cargo_done(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    sel = list(data.get("cargo_sel", []))
    if not sel:
        await call.answer(t("cargo_empty", lang), show_alert=True)
        return
    await state.update_data(cargo=CARGO_SEP.join(sel))
    await state.set_state(PostTrip.contact)
    # Контакт необязателен: inline-кнопка «Пропустить» + reply-кнопка «отправить номер».
    await call.message.edit_text(t("post_contact", lang), reply_markup=inline.contact_skip(lang))
    await call.message.answer(
        t("post_contact_share", lang), reply_markup=reply.share_contact(lang)
    )
    await call.answer()


# --- Шаг 7: контакт (необязательный) ---
@router.message(PostTrip.contact, F.contact)
async def step_contact_shared(message: Message, state: FSMContext, lang: str) -> None:
    await _save_contact(message, state, lang, message.contact.phone_number)


@router.message(PostTrip.contact, F.text)
async def step_contact_text(message: Message, state: FSMContext, lang: str) -> None:
    await _save_contact(message, state, lang, message.text.strip())


@router.callback_query(PostTrip.contact, F.data == "contact_skip")
async def step_contact_skip(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await call.message.edit_reply_markup(reply_markup=None)
    await _save_contact(call.message, state, lang, "")
    await call.answer()


async def _save_contact(message: Message, state: FSMContext, lang: str, contact: str) -> None:
    await state.update_data(contact=contact)
    await state.set_state(PostTrip.comment)
    # Клавиатура «отправить номер» — одноразовая (one_time), сворачивается сама.
    # Сразу показываем запрос комментария с inline-кнопкой «Пропустить».
    await message.answer(t("post_comment", lang), reply_markup=inline.comment_skip(lang))


# --- Шаг 8: комментарий (опционально) ---
@router.callback_query(PostTrip.comment, F.data == "pskip")
async def step_comment_skip(
    call: CallbackQuery, state: FSMContext, user: User, lang: str
) -> None:
    await state.update_data(comment=None)
    await _show_confirm(call.message, state, lang, user.username)
    await call.answer()


@router.message(PostTrip.comment, F.text)
async def step_comment_text(
    message: Message, state: FSMContext, user: User, lang: str
) -> None:
    await state.update_data(comment=message.text.strip())
    await _show_confirm(message, state, lang, user.username)


async def _build_preview_trip(data: dict, user_id: int) -> Trip:
    from datetime import date

    return Trip(
        user_id=user_id,
        direction=Direction(data["direction"]),
        from_city=data["from_city"],
        to_city=data["to_city"],
        depart_date=date.fromisoformat(data["depart_date"]),
        baggage=data["baggage"],
        cargo=data["cargo"],
        comment=data.get("comment"),
        contact=data["contact"],
    )


async def _show_confirm(
    message: Message, state: FSMContext, lang: str, author_username: str | None
) -> None:
    data = await state.get_data()
    preview = await _build_preview_trip(data, message.chat.id)
    text = render_trip(preview, lang, author_username) + "\n\n" + t("post_confirm", lang)
    await state.set_state(PostTrip.confirm)
    await message.answer(text, reply_markup=inline.confirm(lang))


# --- Подтверждение ---
@router.callback_query(PostTrip.confirm, F.data == "pconfirm:no")
async def confirm_cancel(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t("cancelled", lang), reply_markup=reply.main_menu(lang))
    await call.answer()


@router.callback_query(PostTrip.confirm, F.data == "pconfirm:yes")
async def confirm_save(
    call: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
    user: User,
    lang: str,
) -> None:
    from datetime import date

    data = await state.get_data()
    trip = await repo.create_trip(
        session,
        user_id=user.id,
        direction=Direction(data["direction"]),
        from_city=data["from_city"],
        to_city=data["to_city"],
        depart_date=date.fromisoformat(data["depart_date"]),
        baggage=data["baggage"],
        cargo=data["cargo"],
        comment=data.get("comment"),
        contact=data["contact"],
    )
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t("post_saved", lang), reply_markup=reply.main_menu(lang))
    await call.answer()

    # Мгновенная рассылка подписчикам и дубль в группу.
    await services.notify_subscribers(bot, session, trip, user.username)
    await services.post_to_group(bot, trip, user.username)
