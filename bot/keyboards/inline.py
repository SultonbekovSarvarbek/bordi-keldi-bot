from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.db.models import Direction
from bot.i18n import t
from bot.utils.cities import city_label
from bot.utils.constants import (
    BAGGAGE_PRESETS,
    CARGO_CUSTOM_PREFIX,
    CARGO_KEYS,
    CARGO_LABEL,
    CITY_MANUAL,
)


def lang_choice() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="🇺🇿 Oʻzbekcha", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
    )
    return b.as_markup()


def disclaimer(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("disclaimer_accept", lang), callback_data="disc:ok"))
    return b.as_markup()


def directions(lang: str, prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора направления. prefix задаёт сценарий (pdir/sdir/subdir)."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("dir_uz_kr", lang), callback_data=f"{prefix}:UZ_KR"))
    b.row(InlineKeyboardButton(text=t("dir_kr_uz", lang), callback_data=f"{prefix}:KR_UZ"))
    return b.as_markup()


def cities(city_keys: list[str], lang: str, prefix: str) -> InlineKeyboardMarkup:
    """Кнопки-подсказки городов + «ввести вручную». prefix = pfrom / pto.

    На кнопке — локализованное имя, в callback — канонический ключ города.
    """
    b = InlineKeyboardBuilder()
    for key in city_keys:
        b.button(text=city_label(key, lang), callback_data=f"{prefix}:{key}")
    b.button(text=t("post_city_manual", lang), callback_data=f"{prefix}:{CITY_MANUAL}")
    b.adjust(2)
    return b.as_markup()


def baggage(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for preset in BAGGAGE_PRESETS:
        b.button(text=preset, callback_data=f"pbag:{preset}")
    b.button(text=t("baggage_custom_btn", lang), callback_data="pbag_custom")
    b.adjust(3, 1)
    return b.as_markup()


def cargo(lang: str, selected: list[str]) -> InlineKeyboardMarkup:
    """Мультивыбор груза: каноничные пункты-тогглы + свои пункты + «Готово»."""
    b = InlineKeyboardBuilder()
    for key in CARGO_KEYS:
        mark = "✅ " if key in selected else ""
        b.button(text=mark + t(CARGO_LABEL[key], lang), callback_data=f"pcargo:{key}")
    b.adjust(2)
    # Пользовательские пункты — каждый отдельной строкой, тап удаляет.
    customs = [s for s in selected if s.startswith(CARGO_CUSTOM_PREFIX)]
    for i, c in enumerate(customs):
        label = "✅ " + c[len(CARGO_CUSTOM_PREFIX):] + " ✖️"
        b.row(InlineKeyboardButton(text=label, callback_data=f"pcargodel:{i}"))
    b.row(InlineKeyboardButton(text=t("cargo_add_custom", lang), callback_data="pcargo_add"))
    b.row(InlineKeyboardButton(text=t("cargo_done", lang), callback_data="pcargo_done"))
    return b.as_markup()


def comment_skip(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("skip", lang), callback_data="pskip"))
    return b.as_markup()


def contact_skip(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("skip", lang), callback_data="contact_skip"))
    return b.as_markup()


def confirm(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text=t("confirm_yes", lang), callback_data="pconfirm:yes"),
        InlineKeyboardButton(text=t("cancel", lang), callback_data="pconfirm:no"),
    )
    return b.as_markup()


def contact_button(
    contact: str, lang: str, author_username: str | None = None
) -> InlineKeyboardMarkup:
    """Кнопка «Связаться».

    Приоритет ссылки: @username автора → введённый им @username → иначе показ
    контакта алертом (телефон ссылкой в инлайн-кнопке Telegram не сделать).
    """
    b = InlineKeyboardBuilder()
    handle = contact.strip()
    url = None
    if author_username:
        url = f"https://t.me/{author_username}"
    elif handle.startswith("@"):
        url = f"https://t.me/{handle[1:]}"

    if url:
        b.row(InlineKeyboardButton(text=t("btn_contact", lang), url=url))
    else:
        b.row(InlineKeyboardButton(text=t("btn_contact", lang), callback_data="show_contact"))
    return b.as_markup()


def search_all(lang: str) -> InlineKeyboardMarkup:
    """Кнопка «показать все объявления» рядом с календарём в поиске."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("search_all_btn", lang), callback_data="search_all"))
    return b.as_markup()


def subscribe_offer(direction: Direction, lang: str) -> InlineKeyboardMarkup:
    """Предложение подписаться (показывается при пустом поиске)."""
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(
            text=t("search_subscribe_offer", lang),
            callback_data=f"subadd:{direction.value}",
        )
    )
    return b.as_markup()


def subscription_item(sub_id: int, lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("sub_remove", lang), callback_data=f"subdel:{sub_id}"))
    return b.as_markup()


def my_trip_item(trip_id: int, lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("my_delete", lang), callback_data=f"tripdel:{trip_id}"))
    return b.as_markup()
