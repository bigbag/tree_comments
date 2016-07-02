"""Added start fixtures

Revision ID: 328298d1d379
Revises: e3341fbc15fc
Create Date: 2016-07-02 14:33:52.880157

"""

# revision identifiers, used by Alembic.
revision = '328298d1d379'
down_revision = 'e3341fbc15fc'
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
