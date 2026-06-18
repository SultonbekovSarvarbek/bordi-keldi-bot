from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.filters import IsAdmin
from bot.i18n import t

router = Router(name="admin")
# Все хендлеры этого роутера — только для админов и только в личке.
router.message.filter(IsAdmin(), F.chat.type == "private")


def _arg_int(command: CommandObject) -> int | None:
    if not command.args:
        return None
    try:
        return int(command.args.strip().split()[0])
    except ValueError:
        return None


@router.message(Command("admin"))
async def admin_help(message: Message, lang: str) -> None:
    await message.answer(t("admin_usage", lang))


@router.message(Command("ban"))
async def ban(message: Message, command: CommandObject, session: AsyncSession, lang: str) -> None:
    uid = _arg_int(command)
    if uid is None:
        await message.answer(t("admin_usage", lang))
        return
    user = await repo.set_banned(session, uid, True)
    await message.answer(
        t("admin_banned", lang, uid=uid) if user else t("admin_not_found", lang)
    )


@router.message(Command("unban"))
async def unban(message: Message, command: CommandObject, session: AsyncSession, lang: str) -> None:
    uid = _arg_int(command)
    if uid is None:
        await message.answer(t("admin_usage", lang))
        return
    user = await repo.set_banned(session, uid, False)
    await message.answer(
        t("admin_unbanned", lang, uid=uid) if user else t("admin_not_found", lang)
    )


@router.message(Command("del"))
async def delete(message: Message, command: CommandObject, session: AsyncSession, lang: str) -> None:
    tid = _arg_int(command)
    if tid is None:
        await message.answer(t("admin_usage", lang))
        return
    ok = await repo.deactivate_trip(session, tid)
    await message.answer(
        t("admin_trip_deleted", lang, tid=tid) if ok else t("admin_not_found", lang)
    )


@router.message(Command("stats"))
async def show_stats(message: Message, session: AsyncSession, lang: str) -> None:
    s = await repo.stats(session)
    await message.answer(t("admin_stats", lang, **s))
