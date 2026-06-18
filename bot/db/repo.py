from __future__ import annotations

from datetime import date

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.db.models import Direction, Subscription, Trip, User


# ---------- Users ----------
async def get_or_create_user(
    session: AsyncSession,
    user_id: int,
    username: str | None,
    full_name: str | None,
) -> User:
    user = await session.get(User, user_id)
    if user is None:
        user = User(id=user_id, username=username, full_name=full_name)
        session.add(user)
        await session.flush()
    else:
        # Поддерживаем username/имя в актуальном состоянии.
        if user.username != username or user.full_name != full_name:
            user.username = username
            user.full_name = full_name
    return user


async def set_lang(session: AsyncSession, user_id: int, lang: str) -> None:
    await session.execute(update(User).where(User.id == user_id).values(lang=lang))


async def mark_disclaimer_seen(session: AsyncSession, user_id: int) -> None:
    await session.execute(
        update(User).where(User.id == user_id).values(seen_disclaimer=True)
    )


async def set_banned(session: AsyncSession, user_id: int, banned: bool) -> User | None:
    user = await session.get(User, user_id)
    if user is None:
        return None
    user.is_banned = banned
    return user


# ---------- Trips ----------
async def create_trip(session: AsyncSession, **fields: object) -> Trip:
    trip = Trip(**fields)
    session.add(trip)
    await session.flush()
    return trip


async def get_trip(session: AsyncSession, trip_id: int) -> Trip | None:
    return await session.get(Trip, trip_id)


async def my_active_trips(session: AsyncSession, user_id: int) -> list[Trip]:
    stmt = (
        select(Trip)
        .where(Trip.user_id == user_id, Trip.is_active.is_(True))
        .options(selectinload(Trip.user))
        .order_by(Trip.depart_date)
    )
    return list((await session.scalars(stmt)).all())


async def deactivate_trip(session: AsyncSession, trip_id: int, user_id: int | None = None) -> bool:
    """Деактивировать объявление. Если user_id задан — только своё."""
    trip = await session.get(Trip, trip_id)
    if trip is None or not trip.is_active:
        return False
    if user_id is not None and trip.user_id != user_id:
        return False
    trip.is_active = False
    return True


async def search_trips(
    session: AsyncSession,
    direction: Direction,
    date_from: date | None,
    date_to: date | None,
    today_: date,
    limit: int,
) -> list[Trip]:
    """Поиск активных объявлений по направлению.

    Если задан диапазон дат — фильтруем по нему, иначе все будущие (>= сегодня).
    """
    stmt = (
        select(Trip)
        .where(Trip.direction == direction, Trip.is_active.is_(True))
        .options(selectinload(Trip.user))
    )
    if date_from is not None and date_to is not None:
        stmt = stmt.where(Trip.depart_date >= date_from, Trip.depart_date <= date_to)
    else:
        stmt = stmt.where(Trip.depart_date >= today_)
    stmt = stmt.order_by(Trip.depart_date).limit(limit)
    return list((await session.scalars(stmt)).all())


async def deactivate_past_trips(session: AsyncSession, today_: date) -> int:
    """Ночная задача: деактивировать объявления с прошедшей датой."""
    result = await session.execute(
        update(Trip)
        .where(Trip.is_active.is_(True), Trip.depart_date < today_)
        .values(is_active=False)
    )
    return result.rowcount or 0


# ---------- Subscriptions ----------
async def add_subscription(
    session: AsyncSession,
    user_id: int,
    direction: Direction,
    from_city: str | None = None,
    to_city: str | None = None,
) -> Subscription | None:
    """Создать подписку. Возвращает None, если такая уже есть."""
    stmt = select(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.direction == direction,
        Subscription.from_city.is_(from_city) if from_city is None else Subscription.from_city == from_city,
        Subscription.to_city.is_(to_city) if to_city is None else Subscription.to_city == to_city,
    )
    existing = await session.scalar(stmt)
    if existing is not None:
        return None
    sub = Subscription(
        user_id=user_id, direction=direction, from_city=from_city, to_city=to_city
    )
    session.add(sub)
    await session.flush()
    return sub


async def list_subscriptions(session: AsyncSession, user_id: int) -> list[Subscription]:
    stmt = select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.id)
    return list((await session.scalars(stmt)).all())


async def remove_subscription(session: AsyncSession, sub_id: int, user_id: int) -> bool:
    sub = await session.get(Subscription, sub_id)
    if sub is None or sub.user_id != user_id:
        return False
    await session.delete(sub)
    return True


async def matching_subscribers(session: AsyncSession, trip: Trip) -> list[tuple[int, str]]:
    """Подписчики (telegram_id, lang), которым подходит объявление.

    Правило: совпадение направления + (город не задан в подписке ИЛИ совпадает).
    Автор объявления и забаненные исключаются.
    """
    stmt = (
        select(Subscription.user_id, User.lang)
        .join(User, User.id == Subscription.user_id)
        .where(
            Subscription.direction == trip.direction,
            (Subscription.from_city.is_(None)) | (Subscription.from_city == trip.from_city),
            (Subscription.to_city.is_(None)) | (Subscription.to_city == trip.to_city),
            Subscription.user_id != trip.user_id,
            User.is_banned.is_(False),
        )
        .distinct()
    )
    return [(uid, lang) for uid, lang in (await session.execute(stmt)).all()]


# ---------- Stats ----------
async def stats(session: AsyncSession) -> dict[str, int]:
    users = await session.scalar(select(func.count()).select_from(User)) or 0
    active = (
        await session.scalar(
            select(func.count()).select_from(Trip).where(Trip.is_active.is_(True))
        )
        or 0
    )
    total = await session.scalar(select(func.count()).select_from(Trip)) or 0
    subs = await session.scalar(select(func.count()).select_from(Subscription)) or 0
    return {"users": users, "active_trips": active, "total_trips": total, "subs": subs}
