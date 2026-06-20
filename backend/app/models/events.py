from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.organization import User
    from app.models.reference import AIModel, Repository


class TokenUsage(Base):
    """One row per token consumption event (from CodeAgent lake table)."""

    __tablename__ = "token_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ai_model.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    input_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="token_usages")
    model: Mapped["AIModel"] = relationship("AIModel", back_populates="token_usages")

    __table_args__ = (
        Index("ix_token_usage_date_user", "event_date", "user_id"),
        Index("ix_token_usage_date_model", "event_date", "model_id"),
        Index("ix_token_usage_date_user_model", "event_date", "user_id", "model_id"),
    )

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def __repr__(self) -> str:
        return (
            f"<TokenUsage(id={self.id}, date={self.event_date}, "
            f"user_id={self.user_id})>"
        )


class MergeRequest(Base):
    """One row per MR (from CodeHub MR data)."""

    __tablename__ = "merge_request"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mr_external_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    repository_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("repository.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    merged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    total_lines: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ai_lines: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    author: Mapped["User"] = relationship("User", back_populates="merge_requests")
    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="merge_requests"
    )

    __table_args__ = (
        Index("ix_merge_request_date", "merged_at"),
        Index("ix_merge_request_date_author", "merged_at", "author_id"),
        Index("ix_merge_request_date_repo", "merged_at", "repository_id"),
    )

    @property
    def ai_mr_ratio(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return round(self.ai_lines / self.total_lines * 100, 2)

    def __repr__(self) -> str:
        return (
            f"<MergeRequest(id={self.id}, "
            f"mr_external_id='{self.mr_external_id}')>"
        )


class ToolCall(Base):
    """One row per tool invocation (from CodeAgent lake table)."""

    __tablename__ = "tool_call"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tool_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tool_calls")

    __table_args__ = (
        Index("ix_tool_call_date_user", "event_date", "user_id"),
        Index("ix_tool_call_date_tool", "event_date", "tool_name"),
    )

    def __repr__(self) -> str:
        return f"<ToolCall(id={self.id}, tool='{self.tool_name}')>"


class UserIssue(Base):
    """One row per user support issue."""

    __tablename__ = "user_issue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    issue_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_issues")

    __table_args__ = (
        Index("ix_user_issue_date_user", "event_date", "user_id"),
        Index("ix_user_issue_date_type", "event_date", "issue_type"),
    )

    def __repr__(self) -> str:
        return f"<UserIssue(id={self.id}, type='{self.issue_type}')>"
