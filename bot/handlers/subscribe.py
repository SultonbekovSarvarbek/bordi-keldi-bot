from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.db.models import Direction
from bot.i18n import t
from bot.keyboards import inline
from bot.states import Subscribe

router = Router(name="subscribe")
router.message.filter(F.chat.type == "private")

_DIR_LABEL = {Direction.UZ_KR: "dir_uz_kr", Direction.KR_UZ: "dir_kr_uz"}


async def subscribe_entry(
    message: Message, state: FSMContext, session: AsyncSession, lang: str
) -> None:
    """Точка входа в подписки (вызывается из nav-роутера)."""
    await state.clear()
    subs = await repo.list_subscriptions(session, message.from_user.id)
    if subs:
        await message.answer(t("sub_list_title", lang))
        for sub in subs:
            label = t(_DIR_LABEL[sub.direction], lang)
            await message.answer(label, reply_markup=inline.subscription_item(sub.id, lang))
    await state.set_state(Subscribe.direction)
    await message.answer(t("sub_direction", lang), reply_markup=inline.directions(lang, "subdir"))


@router.callback_query(Subscribe.direction, F.data.startswith("subdir:"))
async def subscribe_direction(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, lang: str
) -> None:
    direction = Direction(call.data.split(":", 1)[1])
    await state.clear()
    sub = await repo.add_subscription(session, call.from_user.id, direction)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t("sub_added", lang) if sub else t("sub_exists", lang))
    await call.answer()


# Подписка из предложения при пустом поиске.
@router.callback_query(F.data.startswith("subadd:"))
async def subscribe_from_offer(
    call: CallbackQuery, session: AsyncSession, lang: str
) -> None:
    direction = Direction(call.data.split(":", 1)[1])
    sub = await repo.add_subscription(session, call.from_user.id, direction)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t("sub_added", lang) if sub else t("sub_exists", lang))
    await call.answer()


@router.callback_query(F.data.startswith("subdel:"))
async def unsubscribe(call: CallbackQuery, session: AsyncSession, lang: str) -> None:
    sub_id = int(call.data.split(":", 1)[1])
    await repo.remove_subscription(session, sub_id, call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(t("sub_removed", lang), show_alert=False)
