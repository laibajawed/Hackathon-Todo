"""Initial migration: Add conversation and message tables for AI chatbot

Revision ID: 001_add_conversations
Revises:
Create Date: 2026-01-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_add_conversations"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("message_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_user_active", "conversations", ["user_id", "is_active"])
    op.create_index(
        op.f("ix_conversations_user_id"), "conversations", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_conversations_is_active"), "conversations", ["is_active"], unique=False
    )

    # Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_conversation_sequence",
        "messages",
        ["conversation_id", "sequence_number"],
        unique=False,
    )
    op.create_index(
        "idx_conversation_created",
        "messages",
        ["conversation_id", "created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_messages_conversation_id"),
        "messages",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(op.f("ix_messages_role"), "messages", ["role"], unique=False)


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("conversations")
