"""Create comment table

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
        'comment',
        sa.Column('id_entry', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('date_create', sa.TIMESTAMP(), nullable=True),
        sa.Column('date_update', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id_entry')
    )

    op.create_index('key_comment_user_id', 'comment', ['user_id'])

    op.create_foreign_key(
        'fk_comment_user',
        'comment', 'user',
        ['user_id'], ['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_table('comment')
