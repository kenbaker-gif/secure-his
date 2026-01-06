"""create user_flags and password_reset_tokens tables

Revision ID: 0001_create_user_flags_and_password_reset_tokens
Revises: 
Create Date: 2026-01-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_user_flags_and_password_reset_tokens'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_flags',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, unique=True),
        sa.Column('must_change_password', sa.Boolean(), nullable=True, server_default=sa.text('false')),
    )

    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token_hash', sa.String(), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('password_reset_tokens')
    op.drop_table('user_flags')
