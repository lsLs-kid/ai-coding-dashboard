"""initial: org hierarchy, reference tables, and event fact tables

Revision ID: 9f643031f6bb
Revises:
Create Date: 2026-06-20 20:10:38.105934

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f643031f6bb"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Dimension tables ──────────────────────────────────────────────

    op.create_table(
        "pdu",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lm_team",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("pdu_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["pdu_id"], ["pdu.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lm_team_pdu_id", "lm_team", ["pdu_id"])

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "external_user_id", sa.String(100), unique=True, nullable=False
        ),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("pdu_id", sa.Integer(), nullable=False),
        sa.Column("lm_team_id", sa.Integer(), nullable=False),
        sa.Column("terminal_type", sa.String(50), nullable=True),
        sa.Column("client_version", sa.String(50), nullable=True),
        sa.Column("ide_type", sa.String(50), nullable=True),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            onupdate=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["pdu_id"], ["pdu.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["lm_team_id"], ["lm_team.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_external_user_id", "user", ["external_user_id"])
    op.create_index("ix_user_pdu_id", "user", ["pdu_id"])
    op.create_index("ix_user_lm_team_id", "user", ["lm_team_id"])
    op.create_index("ix_user_pdu_lm_team", "user", ["pdu_id", "lm_team_id"])

    op.create_table(
        "ai_model",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "repository",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── Fact tables ───────────────────────────────────────────────────

    op.create_table(
        "token_usage",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("input_tokens", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("trace_id", sa.String(100), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["model_id"], ["ai_model.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_token_usage_event_date", "token_usage", ["event_date"])
    op.create_index("ix_token_usage_user_id", "token_usage", ["user_id"])
    op.create_index("ix_token_usage_model_id", "token_usage", ["model_id"])
    op.create_index(
        "ix_token_usage_date_user", "token_usage", ["event_date", "user_id"]
    )
    op.create_index(
        "ix_token_usage_date_model", "token_usage", ["event_date", "model_id"]
    )
    op.create_index(
        "ix_token_usage_date_user_model",
        "token_usage",
        ["event_date", "user_id", "model_id"],
    )

    op.create_table(
        "merge_request",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("mr_external_id", sa.String(100), unique=True, nullable=False),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_lines", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ai_lines", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"], ["repository.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["author_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_merge_request_mr_external_id", "merge_request", ["mr_external_id"]
    )
    op.create_index("ix_merge_request_repository_id", "merge_request", ["repository_id"])
    op.create_index("ix_merge_request_author_id", "merge_request", ["author_id"])
    op.create_index("ix_merge_request_merged_at", "merge_request", ["merged_at"])
    op.create_index("ix_merge_request_date", "merge_request", ["merged_at"])
    op.create_index(
        "ix_merge_request_date_author",
        "merge_request",
        ["merged_at", "author_id"],
    )
    op.create_index(
        "ix_merge_request_date_repo",
        "merge_request",
        ["merged_at", "repository_id"],
    )

    op.create_table(
        "tool_call",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tool_name", sa.String(200), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tool_call_event_date", "tool_call", ["event_date"])
    op.create_index("ix_tool_call_user_id", "tool_call", ["user_id"])
    op.create_index("ix_tool_call_tool_name", "tool_call", ["tool_name"])
    op.create_index(
        "ix_tool_call_date_user", "tool_call", ["event_date", "user_id"]
    )
    op.create_index(
        "ix_tool_call_date_tool", "tool_call", ["event_date", "tool_name"]
    )

    op.create_table(
        "user_issue",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("issue_type", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_issue_event_date", "user_issue", ["event_date"])
    op.create_index("ix_user_issue_user_id", "user_issue", ["user_id"])
    op.create_index(
        "ix_user_issue_date_user", "user_issue", ["event_date", "user_id"]
    )
    op.create_index(
        "ix_user_issue_date_type", "user_issue", ["event_date", "issue_type"]
    )


def downgrade() -> None:
    op.drop_table("user_issue")
    op.drop_table("tool_call")
    op.drop_table("merge_request")
    op.drop_table("token_usage")
    op.drop_table("repository")
    op.drop_table("ai_model")
    op.drop_table("user")
    op.drop_table("lm_team")
    op.drop_table("pdu")
