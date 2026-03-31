"""add producers and ref tables

Revision ID: c3d4e5f6a7b8
Revises: 48f0725a7c6c
Create Date: 2026-03-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = '48f0725a7c6c'  # chains after the initial migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ----------------------------------------------------------
    # ref_commodity — must be created before producers (FK dep)
    # Laravel: php artisan make:migration create_ref_commodity_table
    # ----------------------------------------------------------
    op.create_table(
        'ref_commodity',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ref_commodity_id'), 'ref_commodity', ['id'], unique=False)

    # ----------------------------------------------------------
    # ref_region — must be created before producers (FK dep)
    # ----------------------------------------------------------
    op.create_table(
        'ref_region',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('country_code', sa.String(length=10), nullable=False),
        sa.Column('country_name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ref_region_id'), 'ref_region', ['id'], unique=False)

    # ----------------------------------------------------------
    # producers — depends on ref_commodity and ref_region
    # ----------------------------------------------------------
    op.create_table(
        'producers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('external_id', sa.String(length=100), nullable=True),

        # gender: 'm' | 'f' | '0'
        sa.Column('gender', sa.String(length=1), nullable=True),

        sa.Column('date_of_birth', sa.Date(), nullable=True),

        # Foreign keys — like $table->foreignId() constrained()
        sa.Column('commodity_id', sa.Integer(), nullable=True),
        sa.Column('region_id', sa.Integer(), nullable=True),

        sa.Column('total_plot', sa.Integer(), nullable=True),

        # SmallInteger: 1 = active, 0 = inactive
        sa.Column('is_active', sa.SmallInteger(), nullable=False, server_default='1'),

        # Timestamps + audit
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),

        sa.ForeignKeyConstraint(['commodity_id'], ['ref_commodity.id']),
        sa.ForeignKeyConstraint(['region_id'], ['ref_region.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_producers_id'), 'producers', ['id'], unique=False)


def downgrade() -> None:
    # Drop in reverse order — child table first, then parents
    # Laravel: php artisan migrate:rollback
    op.drop_index(op.f('ix_producers_id'), table_name='producers')
    op.drop_table('producers')

    op.drop_index(op.f('ix_ref_region_id'), table_name='ref_region')
    op.drop_table('ref_region')

    op.drop_index(op.f('ix_ref_commodity_id'), table_name='ref_commodity')
    op.drop_table('ref_commodity')
