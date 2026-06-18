from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class PostTrip(StatesGroup):
    """Мастер подачи объявления."""

    direction = State()
    from_city = State()
    from_city_manual = State()
    to_city = State()
    to_city_manual = State()
    depart_date = State()
    baggage = State()
    cargo = State()
    cargo_custom = State()
    contact = State()
    comment = State()
    confirm = State()


class Search(StatesGroup):
    direction = State()
    date = State()


class Subscribe(StatesGroup):
    direction = State()
