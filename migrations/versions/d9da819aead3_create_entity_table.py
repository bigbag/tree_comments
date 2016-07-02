"""Create entity table

Revision ID: d9da819aead3
Revises: 954c8dfb878e
Create Date: 2016-07-02 11:48:00.742587

"""

# revision identifiers, used by Alembic.
revision = 'd9da819aead3'
down_revision = '954c8dfb878e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'entity',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_unique_constraint("unique_name_type", "entity", ["name", "type"])


def downgrade():
    op.drop_table('entity')
