from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.i18n import t


def main_menu(lang: str) -> ReplyKeyboardMarkup:
    """Постоянное reply-меню."""
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text=t("btn_post", lang)))
    b.row(
        KeyboardButton(text=t("btn_search", lang)),
        KeyboardButton(text=t("btn_subscribe", lang)),
    )
    b.row(
        KeyboardButton(text=t("btn_my_trips", lang)),
        KeyboardButton(text=t("btn_lang", lang)),
    )
    return b.as_markup(resize_keyboard=True)


def share_contact(lang: str) -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой «поделиться номером»."""
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text=t("post_contact_share", lang), request_contact=True))
    b.row(KeyboardButton(text=t("cancel", lang)))
    return b.as_markup(resize_keyboard=True, one_time_keyboard=True)
