from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.i18n import t
from bot.keyboards import inline, reply

router = Router(name="common")
# Текстовые хендлеры (включая общий fallback) — только в личке, не в группах.
router.message.filter(F.chat.type == "private")


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str) -> None:
    await message.answer(t("choose_lang", lang), reply_markup=inline.lang_choice())


@router.callback_query(F.data.startswith("lang:"))
async def set_lang(call: CallbackQuery, session: AsyncSession) -> None:
    lang = call.data.split(":", 1)[1]
    await repo.set_lang(session, call.from_user.id, lang)
    await call.message.edit_text(t("lang_set", lang))
    await call.message.answer(t("start", lang), reply_markup=reply.main_menu(lang))
    await call.answer()


# Контакт-кнопка для объявлений с телефоном (не username)
@router.callback_query(F.data == "show_contact")
async def show_contact(call: CallbackQuery) -> None:
    # Контакт уже виден в тексте карточки — просто закрываем "часики".
    await call.answer()


# Fallback: только вне активного FSM-состояния, чтобы не перехватывать шаги мастера.
@router.message(StateFilter(None))
async def fallback(message: Message, lang: str) -> None:
    await message.answer(t("unknown", lang), reply_markup=reply.main_menu(lang))
