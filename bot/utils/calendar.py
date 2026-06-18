from __future__ import annotations

from aiogram_calendar import SimpleCalendar
from aiogram_calendar.schemas import CalendarLabels

# Локализованные подписи календаря. Передаём их напрямую (locale=None), чтобы не
# зависеть от системных локалей ОС — в slim-образах Linux они обычно отсутствуют,
# а узбекской локали практически нигде нет. Недели — с понедельника (Пн..Вс).
_LABELS: dict[str, CalendarLabels] = {
    "ru": CalendarLabels(
        days_of_week=["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        months=["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
        cancel_caption="❌ Отмена",
        today_caption="Сегодня",
    ),
    "uz": CalendarLabels(
        days_of_week=["Du", "Se", "Cho", "Pa", "Ju", "Sh", "Ya"],
        months=["Yan", "Fev", "Mar", "Apr", "May", "Iyn",
                "Iyl", "Avg", "Sen", "Okt", "Noy", "Dek"],
        cancel_caption="❌ Bekor",
        today_caption="Bugun",
    ),
}


def make_calendar(lang: str) -> SimpleCalendar:
    """SimpleCalendar с подписями на нужном языке (по умолчанию узбекский)."""
    cal = SimpleCalendar(show_alerts=True)
    # _labels — внутреннее поле библиотеки; подменяем его, т.к. публичный API
    # принимает только строку locale (зависящую от системных локалей).
    cal._labels = _LABELS.get(lang, _LABELS["uz"])
    return cal
