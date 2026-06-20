from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base for all ORM models."""
    pass


class TimestampMixin:
    """Mixin that adds created_at / updated_at columns.

    Use on tables where row-level audit timestamps are valuable.
    Dimension tables get created_at only; User gets both since org
    mappings change over time.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
