"""Class with comment data model"""

import sqlalchemy as sa


class CommentModel(object):

    __name__ = 'comments'

    metadata = sa.MetaData()

    RECORD_ON_PAGE = 50

    table = sa.Table(
        'comments',
        metadata,
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('parent_id', sa.BigInteger, nullable=True),
        sa.Column('level', sa.Integer, nullable=False),
        sa.Column('path', sa.String(256), nullable=False),
        sa.Column('has_children', sa.Boolean(False), nullable=False),
        sa.Column('user_id', sa.BigInteger, nullable=False),
        sa.Column('entity_id', sa.BigInteger, nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('create_date', sa.TIMESTAMP, nullable=False),
        sa.Column('update_date', sa.TIMESTAMP, nullable=False),
    )

    async def get_all(self, engine, entity_id, page):
        """Request information about comments"""

        comments = []
        page = page if page > 0 else 1
        query = self.table.select().\
            where(self.table.c.entity_id == entity_id).\
            where(self.table.c.level == 1).\
            where(self.table.c.id > (page - 1) * self.RECORD_ON_PAGE).\
            limit(self.RECORD_ON_PAGE).\
            order_by('create_date')

        async with engine.acquire() as conn:
            async for row in conn.execute(query):
                comments.append(
                    {
                        'id': row.id,
                        'user_id': row.user_id,
                        'create_date': row.create_datetime.isoformat(),
                        'text': row.text,
                    }
                )

        return comments

    async def create(self, engine, user_id, entity_id, text, parent_id=None):
        """Request to create comment"""

        async with engine.acquire() as conn:
            data = {
                'level': 1,
                'user_id': user_id,
                'entity_id': entity_id,
                'has_children': False,
                'text': text,
            }
            if parent_id:
                query = self.table.select(self.table.c.id == parent_id)
                parent_comment = await(await conn.execute(query)).first()
                if parent_comment:
                    path = parent_comment.id if not parent_comment.path else \
                        '{}.{}'.format(parent_comment.path, parent_comment.id)

                    data.update(
                        {
                            'parent_id': parent_comment.id,
                            'level': parent_comment.level + 1,
                            'path': path,
                        }
                    )

            trans = await conn.begin()
            try:
                result = await conn.execute(self.table.insert().values(data))
                query = self.table.update(self.table.c.id == parent_id).\
                    values(has_children=True)
                await conn.execute(query)
            except Exception:
                await trans.rollback()
                return False
            else:
                await trans.commit()

            return result.lastrowid

    async def delete(self, engine, comment_id):
        async with engine.acquire() as conn:
            query = self.table.delete().where(self.table.c.id == comment_id).\
                where(self.table.c.has_children.is_(False))
            result = await conn.execute(query)
            return result.rowcount
