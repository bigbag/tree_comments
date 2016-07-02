"""Added start fixtures

Revision ID: e3341fbc15fc
Revises: 707b82c5f595
Create Date: 2016-07-02 13:23:47.753380

"""

# revision identifiers, used by Alembic.
revision = 'e3341fbc15fc'
down_revision = '707b82c5f595'
branch_labels = None
depends_on = None
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import table


def upgrade():
    users_data = [{"name": "user_{}".format(x)} for x in range(1, 100)]
    users_table = table(
        'user',
        sa.Column('id', sa.BigInteger()),
        sa.Column('name', sa.String(100)),
    )

    op.bulk_insert(users_table, users_data)

    entities_data = [{"name": "entity_{}".format(x), "type": "type_{}".format(x)} for x in range(1, 100)]
    entities_table = table(
        'entity',
        sa.Column('id', sa.BigInteger()),
        sa.Column('name', sa.String(100)),
        sa.Column('type', sa.String(100)),
    )

    op.bulk_insert(entities_table, entities_data)


def downgrade():
    pass
