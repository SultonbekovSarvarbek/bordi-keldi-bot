from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from bot.config import settings
from bot.handlers import setup_routers
from bot.middlewares import DbSessionMiddleware, UserMiddleware
from bot.scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("bordi-keldi")


async def main() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    redis = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    # Сессия БД — на уровне апдейта (доступна всем). Один commit/rollback на апдейт.
    dp.update.outer_middleware(DbSessionMiddleware())
    # Пользователь/бан/язык — на наблюдателях, где уже известен event_from_user.
    for observer in (dp.message, dp.callback_query):
        observer.outer_middleware(UserMiddleware())

    setup_routers(dp)

    scheduler = setup_scheduler()
    scheduler.start()

    log.info("Бот запускается (polling)…")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()
        await redis.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Остановлено.")
