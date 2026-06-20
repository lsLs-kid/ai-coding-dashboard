from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.events import MergeRequest, TokenUsage, ToolCall, UserIssue


class Pdu(Base):
    """PDU organisational unit (e.g. 无线PDU, 软件PDU)."""

    __tablename__ = "pdu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    lm_teams: Mapped[List["LmTeam"]] = relationship(
        "LmTeam", back_populates="pdu", lazy="selectin"
    )
    users: Mapped[List["User"]] = relationship(
        "User", back_populates="pdu", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Pdu(id={self.id}, name='{self.name}')>"


class LmTeam(Base):
    """LM team, belongs to a PDU (e.g. 架构与算法LM)."""

    __tablename__ = "lm_team"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    pdu_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pdu.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    pdu: Mapped["Pdu"] = relationship("Pdu", back_populates="lm_teams")
    users: Mapped[List["User"]] = relationship(
        "User", back_populates="lm_team", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<LmTeam(id={self.id}, name='{self.name}', pdu_id={self.pdu_id})>"


class User(Base, TimestampMixin):
    """Org mapping: external user_id → PDU → LM team.

    This is the central mapping table that ties lake-table user
    identifiers to the organisational hierarchy.  Attribute columns
    (terminal_type, client_version, ide_type) are captured here for
    query convenience.
    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_user_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pdu_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pdu.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    lm_team_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lm_team.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    terminal_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    client_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ide_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    pdu: Mapped["Pdu"] = relationship("Pdu", back_populates="users")
    lm_team: Mapped["LmTeam"] = relationship("LmTeam", back_populates="users")
    token_usages: Mapped[List["TokenUsage"]] = relationship(
        "TokenUsage", back_populates="user", lazy="selectin"
    )
    merge_requests: Mapped[List["MergeRequest"]] = relationship(
        "MergeRequest", back_populates="author", lazy="selectin"
    )
    tool_calls: Mapped[List["ToolCall"]] = relationship(
        "ToolCall", back_populates="user", lazy="selectin"
    )
    user_issues: Mapped[List["UserIssue"]] = relationship(
        "UserIssue", back_populates="user", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_user_pdu_lm_team", "pdu_id", "lm_team_id"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, external_id='{self.external_user_id}')>"
