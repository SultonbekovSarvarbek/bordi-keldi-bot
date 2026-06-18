from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import settings
from bot.db.base import session_factory
from bot.db import repo
from bot.utils.dates import today

log = logging.getLogger(__name__)


async def deactivate_past_job() -> None:
    """Ночная деактивация объявлений с прошедшей датой."""
    async with session_factory() as session:
        count = await repo.deactivate_past_trips(session, today())
        await session.commit()
    if count:
        log.info("Деактивировано просроченных объявлений: %s", count)


def setup_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.tz)
    scheduler.add_job(
        deactivate_past_job,
        trigger="cron",
        hour=settings.deactivate_hour,
        minute=0,
        id="deactivate_past_trips",
        replace_existing=True,
    )
    return scheduler
