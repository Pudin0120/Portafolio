"""add_dimensional_calculation_to_composite_products

Revision ID: f6a58088e6b0
Revises: f9da9f3c2118
Create Date: 2026-04-08 03:13:15.579422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a58088e6b0'
down_revision: Union[str, None] = 'f9da9f3c2118'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to product_components for dimensional relationships
    op.add_column('product_components', sa.Column('base_quantity', sa.Integer(), nullable=True))
    op.add_column('product_components', sa.Column('relationship_config', sa.JSON(), nullable=True))
    op.add_column('product_components', sa.Column('snapshot_quantity', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('product_components', sa.Column('snapshot_dimensions', sa.JSON(), nullable=True))
    op.add_column('product_components', sa.Column('snapshot_purchase_price', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('product_components', sa.Column('snapshot_sale_price', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('product_components', sa.Column('snapshot_created_at', sa.DateTime(), nullable=True))
    op.add_column('product_components', sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True))
    
    # Migrate existing data: copy 'quantity' to 'base_quantity'
    op.execute("UPDATE product_components SET base_quantity = quantity WHERE base_quantity IS NULL")
    
    # Make base_quantity NOT NULL after migration
    op.alter_column('product_components', 'base_quantity', nullable=False)
    op.alter_column('product_components', 'updated_at', nullable=False)
    
    # Add new column to products for composition snapshot metadata
    op.add_column('products', sa.Column('composition_snapshot_created_at', sa.DateTime(), nullable=True))
    
    # Rename composite_product_id to match ORM (if needed)
    # The table already uses parent_product_id, so no change needed


def downgrade() -> None:
    # Remove columns from products
    op.drop_column('products', 'composition_snapshot_created_at')
    
    # Remove columns from product_components
    op.drop_column('product_components', 'updated_at')
    op.drop_column('product_components', 'snapshot_created_at')
    op.drop_column('product_components', 'snapshot_sale_price')
    op.drop_column('product_components', 'snapshot_purchase_price')
    op.drop_column('product_components', 'snapshot_dimensions')
    op.drop_column('product_components', 'snapshot_quantity')
    op.drop_column('product_components', 'relationship_config')
    op.drop_column('product_components', 'base_quantity')
