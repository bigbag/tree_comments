"""Create comment_tree table

Revision ID: f474b0c76cfc
Revises: e3341fbc15fc
Create Date: 2016-07-03 11:15:32.809085

"""

# revision identifiers, used by Alembic.
revision = 'f474b0c76cfc'
down_revision = 'e3341fbc15fc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'comment_tree',
        sa.Column('id_parent', sa.Integer(), nullable=False),
        sa.Column('id_child', sa.Integer(), nullable=False),
        sa.Column('id_nearest_parent', sa.Integer(), nullable=False),
        sa.Column('depth', sa.Integer(), nullable=False),
        sa.Column('has_children', sa.Boolean(False), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id_parent', 'id_child')
    )

    op.create_index('key_comment_treet_id_child', 'comment_tree', ['id_child'])
    op.create_index('key_comment_treet_has_children', 'comment_tree', ['has_children'])
    op.create_index('key_comment_treet_id_nearest_parent', 'comment_tree', ['id_nearest_parent'])
    op.create_index('key_comment_treet_main', 'comment_tree', ['id_parent', 'id_child', 'id_nearest_parent', 'depth'])

    op.create_foreign_key(
        'fk_comment_tree_entity',
        'comment_tree', 'entity',
        ['entity_id'], ['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        'fk_comment_tree_comment_parent',
        'comment_tree', 'comment',
        ['id_parent'], ['id_comment'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        'fk_comment_tree_comment_child',
        'comment_tree', 'comment',
        ['id_child'], ['id_comment'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_table('comment_tree')
