"""Create comment_tree table

Revision ID: e3341fbc15fc
Revises: 707b82c5f595
Create Date: 2016-07-02 13:23:47.753380

"""

# revision identifiers, used by Alembic.
revision = 'e3341fbc15fc'
down_revision = '707b82c5f595'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'comment_tree',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('lft', sa.BigInteger(), nullable=False),
        sa.Column('rgt', sa.BigInteger(), index=True, nullable=False),
        sa.Column('depth', sa.BigInteger(), nullable=False),
        sa.Column('has_children', sa.Boolean(False), nullable=False),
        sa.Column('entity_id', sa.BigInteger(), nullable=False),
        sa.Column('comment_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('key_lft_rgt', 'comment_tree', ['lft', 'rgt'])

    op.create_index('key_has_children', 'comment_tree', ['has_children'])

    op.create_foreign_key(
        'fk_comment_tree_comment',
        'comment_tree', 'comment',
        ['comment_id'], ['id'],
        ondelete='CASCADE')

    op.create_foreign_key(
        'fk_comment_tree_entity',
        'comment_tree', 'entity',
        ['entity_id'], ['id'])


def downgrade():
    op.drop_table('comment_tree')
