from __future__ import annotations

from aiogram import Dispatcher

from bot.handlers import admin, common, misc, my_trips, nav, post, search, subscribe


def setup_routers(dp: Dispatcher) -> None:
    # Порядок важен:
    # 0) misc — служебные команды (/id), работают в любом чате;
    # 1) nav — кнопки меню/«Отмена» перехватывают ввод раньше шагов FSM;
    # 2) admin — команды администратора;
    # 3) FSM-роутеры (post/search/subscribe) и my_trips;
    # 4) common — обработка языка, контакта и общий fallback.
    dp.include_router(misc.router)
    dp.include_router(nav.router)
    dp.include_router(admin.router)
    dp.include_router(post.router)
    dp.include_router(search.router)
    dp.include_router(subscribe.router)
    dp.include_router(my_trips.router)
    dp.include_router(common.router)
