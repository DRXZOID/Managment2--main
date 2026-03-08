"""Add gap_item_statuses table

Revision ID: a1b2c3d4e5f6
Revises: 095e10abb6f9
Create Date: 2026-03-08 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '095e10abb6f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'gap_item_statuses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('reference_category_id', sa.Integer(), nullable=False),
        sa.Column('target_product_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['reference_category_id'], ['categories.id'],
            name=op.f('fk_gap_item_statuses_reference_category_id_categories'),
        ),
        sa.ForeignKeyConstraint(
            ['target_product_id'], ['products.id'],
            name=op.f('fk_gap_item_statuses_target_product_id_products'),
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_gap_item_statuses')),
        sa.UniqueConstraint(
            'reference_category_id',
            'target_product_id',
            name='uq_gap_item_statuses_pair',
        ),
    )
    op.create_index(
        'ix_gap_item_statuses_reference_category_id',
        'gap_item_statuses',
        ['reference_category_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_gap_item_statuses_reference_category_id', table_name='gap_item_statuses')
    op.drop_table('gap_item_statuses')

