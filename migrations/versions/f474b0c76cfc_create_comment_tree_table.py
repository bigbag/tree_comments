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
        sa.Column('ancestor_id', sa.Integer(), nullable=False),
        sa.Column('descendant_id', sa.Integer(), nullable=False),
        sa.Column('nearest_ancestor_id', sa.Integer(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('has_children', sa.Boolean(False), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('ancestor_id', 'descendant_id')
    )

    op.create_index('key_comment_treet_descendant_id', 'comment_tree', ['descendant_id'])
    op.create_index('key_comment_treet_has_children', 'comment_tree', ['has_children'])
    op.create_index('key_comment_treet_nearest_ancestor_id', 'comment_tree', ['nearest_ancestor_id'])
    op.create_index('key_comment_treet_main', 'comment_tree', ['ancestor_id', 'descendant_id', 'nearest_ancestor_id', 'level'])

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
        ['ancestor_id'], ['comment_id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        'fk_comment_tree_comment_child',
        'comment_tree', 'comment',
        ['descendant_id'], ['comment_id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_table('comment_tree')
