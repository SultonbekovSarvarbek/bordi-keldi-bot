from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

# Служебный роутер: работает в ЛЮБОМ чате (вкл. группы/каналы),
# поэтому подключается раньше остальных, у которых стоит фильтр «только личка».
router = Router(name="misc")


@router.message(Command("id"))
async def cmd_id(message: Message) -> None:
    """Показать chat_id текущего чата — для настройки GROUP_ID."""
    chat = message.chat
    title = chat.title or getattr(chat, "full_name", None) or "—"
    await message.reply(
        f"🆔 <b>chat_id:</b> <code>{chat.id}</code>\n"
        f"тип: {chat.type}\n"
        f"название: {title}"
    )
