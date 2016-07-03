"""Create user table

Revision ID: 954c8dfb878e
Revises: 
Create Date: 2016-07-02 11:45:09.611147

"""

# revision identifiers, used by Alembic.
revision = '954c8dfb878e'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('user')
