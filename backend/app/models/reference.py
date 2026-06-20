from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.events import MergeRequest, TokenUsage


class AIModel(Base):
    """AI model reference (e.g. MiniMax-M2.7, DeepSeek-V3).

    Named AIModel rather than Model to avoid shadowing the SQLAlchemy
    and Pydantic concepts of "model".
    """

    __tablename__ = "ai_model"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    token_usages: Mapped[List["TokenUsage"]] = relationship(
        "TokenUsage", back_populates="model", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<AIModel(id={self.id}, name='{self.name}')>"


class Repository(Base):
    """Code repository reference (e.g. wireless/baseband)."""

    __tablename__ = "repository"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    merge_requests: Mapped[List["MergeRequest"]] = relationship(
        "MergeRequest", back_populates="repository", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Repository(id={self.id}, name='{self.name}')>"
