from __future__ import annotations

from bot.db.models import Direction

# Города хранятся по каноническому КЛЮЧУ (язык-независимо), а показываются
# локализованной подписью. Это нужно, чтобы один и тот же город не сохранялся
# по-разному на разных языках (иначе ломаются совпадения и карточки).
CITY_LABELS: dict[str, dict[str, str]] = {
    # Узбекистан
    "tashkent": {"uz": "Toshkent", "ru": "Ташкент"},
    "samarkand": {"uz": "Samarqand", "ru": "Самарканд"},
    "bukhara": {"uz": "Buxoro", "ru": "Бухара"},
    "andijan": {"uz": "Andijon", "ru": "Андижан"},
    "fergana": {"uz": "Fargʻona", "ru": "Фергана"},
    "namangan": {"uz": "Namangan", "ru": "Наманган"},
    "qarshi": {"uz": "Qarshi", "ru": "Карши"},
    "nukus": {"uz": "Nukus", "ru": "Нукус"},
    "urgench": {"uz": "Urganch", "ru": "Ургенч"},
    # Корея
    "seoul_incheon": {"uz": "Seul (Incheon)", "ru": "Сеул (Инчхон)"},
    "seoul_gimpo": {"uz": "Seul (Gimpo)", "ru": "Сеул (Гимпо)"},
    "busan": {"uz": "Busan", "ru": "Пусан"},
    "daegu": {"uz": "Daegu", "ru": "Тэгу"},
}

UZ_CITY_KEYS = [
    "tashkent", "samarkand", "bukhara", "andijan",
    "fergana", "namangan", "qarshi", "nukus", "urgench",
]
KR_CITY_KEYS = ["seoul_incheon", "seoul_gimpo", "busan", "daegu"]


def from_cities(direction: Direction) -> list[str]:
    """Ключи городов вылета в зависимости от направления."""
    return UZ_CITY_KEYS if direction == Direction.UZ_KR else KR_CITY_KEYS


def to_cities(direction: Direction) -> list[str]:
    """Ключи городов прилёта в зависимости от направления."""
    return KR_CITY_KEYS if direction == Direction.UZ_KR else UZ_CITY_KEYS


def city_label(value: str, lang: str) -> str:
    """Локализованное имя города.

    value — либо канонический ключ (тогда берём подпись по языку),
    либо произвольный текст (город, введённый вручную) — показываем как есть.
    """
    entry = CITY_LABELS.get(value)
    if entry is None:
        return value  # ручной ввод — отдаём как есть
    return entry.get(lang) or entry.get("uz") or value
