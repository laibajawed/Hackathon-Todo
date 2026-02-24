"""add_priority_and_tag_to_tasks

Revision ID: abb5172a1eb3
Revises: 001_add_conversations
Create Date: 2026-02-24 18:24:09.789154+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abb5172a1eb3'
down_revision = '001_add_conversations'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for task priority
    priority_enum = sa.Enum('low', 'medium', 'high', name='taskpriority')
    priority_enum.create(op.get_bind(), checkfirst=True)

    # Add priority column with default value 'medium'
    op.add_column('task', sa.Column('priority', priority_enum, nullable=False, server_default='medium'))

    # Add tag column (nullable)
    op.add_column('task', sa.Column('tag', sa.String(length=50), nullable=True))

    # Update description max length from 2000 to 1000
    op.alter_column('task', 'description',
                    existing_type=sa.String(length=2000),
                    type_=sa.String(length=1000),
                    existing_nullable=True)


def downgrade() -> None:
    # Remove tag column
    op.drop_column('task', 'tag')

    # Remove priority column
    op.drop_column('task', 'priority')

    # Drop enum type
    priority_enum = sa.Enum('low', 'medium', 'high', name='taskpriority')
    priority_enum.drop(op.get_bind(), checkfirst=True)

    # Revert description max length from 1000 to 2000
    op.alter_column('task', 'description',
                    existing_type=sa.String(length=1000),
                    type_=sa.String(length=2000),
                    existing_nullable=True)

