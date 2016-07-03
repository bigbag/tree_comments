"""Added start fixtures

Revision ID: 707b82c5f595
Revises: d9da819aead3
Create Date: 2016-07-02 13:18:10.089362

"""

# revision identifiers, used by Alembic.
revision = '707b82c5f595'
down_revision = 'd9da819aead3'
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
