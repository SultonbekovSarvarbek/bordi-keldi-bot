from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.base import Base


class Direction(str, enum.Enum):
    """Направление рейса."""

    UZ_KR = "UZ_KR"  # Узбекистан → Корея
    KR_UZ = "KR_UZ"  # Корея → Узбекистан


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram ID
    username: Mapped[str | None] = mapped_column(String(64))
    full_name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32))
    lang: Mapped[str] = mapped_column(String(2), default="uz", server_default="uz")
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    seen_disclaimer: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trips: Mapped[list["Trip"]] = relationship(back_populates="user")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    direction: Mapped[Direction] = mapped_column(SAEnum(Direction), index=True)
    from_city: Mapped[str] = mapped_column(String(64))
    to_city: Mapped[str] = mapped_column(String(64))
    depart_date: Mapped[date] = mapped_column(Date, index=True)
    baggage: Mapped[str] = mapped_column(String(64))
    cargo: Mapped[str] = mapped_column(String(64))
    comment: Mapped[str | None] = mapped_column(String(512))
    contact: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="trips")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    direction: Mapped[Direction] = mapped_column(SAEnum(Direction), index=True)
    from_city: Mapped[str | None] = mapped_column(String(64))  # null = любой
    to_city: Mapped[str | None] = mapped_column(String(64))  # null = любой
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="subscriptions")
