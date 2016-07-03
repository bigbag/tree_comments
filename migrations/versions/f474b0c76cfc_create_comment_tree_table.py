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
        sa.Column('id_ancestor', sa.Integer(), nullable=False),
        sa.Column('id_descendant', sa.Integer(), nullable=False),
        sa.Column('id_nearest_ancestor', sa.Integer(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('has_children', sa.Boolean(False), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id_ancestor', 'id_descendant')
    )

    op.create_index('key_comment_treet_id_descendant', 'comment_tree', ['id_descendant'])
    op.create_index('key_comment_treet_has_children', 'comment_tree', ['has_children'])
    op.create_index('key_comment_treet_id_nearest_ancestor', 'comment_tree', ['id_nearest_ancestor'])
    op.create_index('key_comment_treet_main', 'comment_tree', ['id_ancestor', 'id_descendant', 'id_nearest_ancestor', 'level'])

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
        ['id_ancestor'], ['id_entry'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        'fk_comment_tree_comment_child',
        'comment_tree', 'comment',
        ['id_descendant'], ['id_entry'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_table('comment_tree')
