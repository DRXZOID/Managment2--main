"""Migrate price-like fields from Float to Numeric(12,4)

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-12 00:00:00.000000

Rationale
---------
Floating-point representation causes silent rounding errors for monetary
values.  Numeric(12, 4) provides exact decimal storage on both SQLite
(TEXT round-trip) and PostgreSQL (NUMERIC native type).

Fields migrated
---------------
- products.price          Float  -> Numeric(12, 4)
- product_price_history.price  Float  -> Numeric(12, 4)

Fields intentionally kept as Float
-----------------------------------
- category_mappings.confidence   — similarity score, not monetary
- product_mappings.confidence    — similarity score, not monetary
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None

_NUMERIC = sa.Numeric(precision=12, scale=4, asdecimal=True)


def upgrade() -> None:
    with op.batch_alter_table('products') as batch_op:
        batch_op.alter_column(
            'price',
            existing_type=sa.Float(),
            type_=_NUMERIC,
            existing_nullable=True,
        )

    with op.batch_alter_table('product_price_history') as batch_op:
        batch_op.alter_column(
            'price',
            existing_type=sa.Float(),
            type_=_NUMERIC,
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table('product_price_history') as batch_op:
        batch_op.alter_column(
            'price',
            existing_type=_NUMERIC,
            type_=sa.Float(),
            existing_nullable=True,
        )

    with op.batch_alter_table('products') as batch_op:
        batch_op.alter_column(
            'price',
            existing_type=_NUMERIC,
            type_=sa.Float(),
            existing_nullable=True,
        )

