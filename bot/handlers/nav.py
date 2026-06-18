from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User
from bot.filters import MenuButton
from bot.handlers.my_trips import my_trips_entry
from bot.handlers.post import post_entry
from bot.handlers.search import search_entry
from bot.handlers.subscribe import subscribe_entry
from bot.i18n import t
from bot.keyboards import inline, reply

# Навигационный роутер включается ПЕРВЫМ: кнопки меню и «Отмена» перехватывают
# ввод раньше, чем его успеют поглотить текстовые шаги активного FSM.
router = Router(name="nav")
# Весь интерактив — только в личке, чтобы бот не реагировал в группах.
router.message.filter(F.chat.type == "private")


@router.message(MenuButton("cancel"))
async def cancel(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await message.answer(t("cancelled", lang), reply_markup=reply.main_menu(lang))


@router.message(MenuButton("btn_post"))
async def nav_post(message: Message, state: FSMContext, user: User, lang: str) -> None:
    await post_entry(message, state, user, lang)


@router.message(MenuButton("btn_search"))
async def nav_search(message: Message, state: FSMContext, lang: str) -> None:
    await search_entry(message, state, lang)


@router.message(MenuButton("btn_subscribe"))
async def nav_subscribe(
    message: Message, state: FSMContext, session: AsyncSession, lang: str
) -> None:
    await subscribe_entry(message, state, session, lang)


@router.message(MenuButton("btn_my_trips"))
async def nav_my_trips(
    message: Message, state: FSMContext, session: AsyncSession, lang: str
) -> None:
    await state.clear()
    await my_trips_entry(message, session, lang)


@router.message(MenuButton("btn_lang"))
async def nav_lang(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await message.answer(t("choose_lang", lang), reply_markup=inline.lang_choice())
