"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-18
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

direction_enum = sa.Enum("UZ_KR", "KR_UZ", name="direction")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("lang", sa.String(length=2), server_default="uz", nullable=False),
        sa.Column("is_banned", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("seen_disclaimer", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "trips",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("direction", direction_enum, nullable=False),
        sa.Column("from_city", sa.String(length=64), nullable=False),
        sa.Column("to_city", sa.String(length=64), nullable=False),
        sa.Column("depart_date", sa.Date(), nullable=False),
        sa.Column("baggage", sa.String(length=64), nullable=False),
        sa.Column("cargo", sa.String(length=64), nullable=False),
        sa.Column("comment", sa.String(length=512), nullable=True),
        sa.Column("contact", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_trips_user_id", "trips", ["user_id"])
    op.create_index("ix_trips_direction", "trips", ["direction"])
    op.create_index("ix_trips_depart_date", "trips", ["depart_date"])
    op.create_index("ix_trips_is_active", "trips", ["is_active"])

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("direction", direction_enum, nullable=False),
        sa.Column("from_city", sa.String(length=64), nullable=True),
        sa.Column("to_city", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_direction", "subscriptions", ["direction"])


def downgrade() -> None:
    op.drop_table("subscriptions")
    op.drop_table("trips")
    op.drop_table("users")
    direction_enum.drop(op.get_bind(), checkfirst=True)
