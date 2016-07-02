"""Create comment table

Revision ID: 707b82c5f595
Revises: d9da819aead3
Create Date: 2016-07-02 13:18:10.089362

"""

# revision identifiers, used by Alembic.
revision = '707b82c5f595'
down_revision = 'd9da819aead3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'comment',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('text', sa.String(length=512), nullable=False),
        sa.Column('user_id', sa.BigInteger(), index=True, nullable=False),
        sa.Column('create_date', sa.Integer(), nullable=False),
        sa.Column('update_date', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_foreign_key(
        'fk_comment_user',
        'comment', 'user',
        ['user_id'], ['id'],
    )


def downgrade():
    op.drop_table('comment')
