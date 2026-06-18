from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from bot.config import settings

TZ = ZoneInfo(settings.tz)

# Поддерживаемые форматы ввода даты.
_FORMATS = ("%d.%m.%Y", "%d.%m.%y", "%d.%m")


def today() -> date:
    """Сегодняшняя дата в часовом поясе сервиса (Asia/Tashkent)."""
    return datetime.now(TZ).date()


def parse_date(raw: str) -> date | None:
    """Распарсить дату из строки. Возвращает None при неверном формате.

    Для формата без года (ДД.ММ) подставляется ближайший будущий год:
    если в текущем году дата уже прошла — берётся следующий год.
    """
    raw = raw.strip()
    for fmt in _FORMATS:
        try:
            parsed = datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
        if fmt == "%d.%m":
            cur = today()
            parsed = parsed.replace(year=cur.year)
            if parsed < cur:
                parsed = parsed.replace(year=cur.year + 1)
        return parsed
    return None


def is_past(d: date) -> bool:
    return d < today()


def fmt_date(d: date) -> str:
    return d.strftime("%d.%m.%Y")
