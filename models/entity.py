"""Class with entity data model"""

import sqlalchemy as sa


class EntityModel(object):

    __name__ = 'entity'

    metadata = sa.MetaData()

    TYPE_POST = 'post'
    TYPE_PAGE = 'page'
    TYPE_COMMENT = 'comment'

    table = sa.Table(
        'entity',
        metadata,
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
    )
