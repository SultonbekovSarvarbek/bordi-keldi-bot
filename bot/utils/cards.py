from __future__ import annotations

from bot.db.models import Trip
from bot.i18n import t
from bot.utils.cities import city_label
from bot.utils.constants import (
    BAGGAGE_NEGOTIABLE,
    CARGO_CUSTOM_PREFIX,
    CARGO_LABEL,
    CARGO_SEP,
)
from bot.utils.dates import fmt_date


def _baggage_label(baggage: str, lang: str) -> str:
    if baggage == BAGGAGE_NEGOTIABLE:
        return t("baggage_negotiable", lang)
    return baggage


def _cargo_label(cargo: str, lang: str) -> str:
    # cargo может содержать несколько пунктов через CARGO_SEP, каждый — либо
    # каноничный ключ (локализуется), либо "custom:<текст>" (показываем как есть).
    out: list[str] = []
    for token in cargo.split(CARGO_SEP):
        if not token:
            continue
        if token.startswith(CARGO_CUSTOM_PREFIX):
            out.append(token[len(CARGO_CUSTOM_PREFIX):])
        else:
            key = CARGO_LABEL.get(token)
            out.append(t(key, lang) if key else token)
    return ", ".join(out) if out else cargo


def render_trip(trip: Trip, lang: str, author_username: str | None = None) -> str:
    """Сформировать текст карточки объявления.

    author_username — @username автора (если есть), показывается отдельной строкой.
    """
    lines = [
        t(
            "card_title",
            lang,
            from_city=city_label(trip.from_city, lang),
            to_city=city_label(trip.to_city, lang),
        ),
        t("card_date", lang, date=fmt_date(trip.depart_date)),
        t("card_baggage", lang, baggage=_baggage_label(trip.baggage, lang)),
        t("card_cargo", lang, cargo=_cargo_label(trip.cargo, lang)),
    ]
    if trip.comment:
        lines.append(t("card_comment", lang, comment=trip.comment))
    if trip.contact:
        lines.append(t("card_contact", lang, contact=trip.contact))
    if author_username:
        lines.append(t("card_username", lang, username=author_username))
    return "\n".join(lines)
