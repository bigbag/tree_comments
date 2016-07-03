"""Class with comment data model"""

import logging as log
import sqlalchemy as sa


class CommentModel(object):

    __name__ = 'comment'

    metadata = sa.MetaData()

    RECORD_ON_PAGE = 50

    table = sa.Table(
        'comment',
        metadata,
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('date_create', sa.TIMESTAMP(), default=sa.func.now()),
        sa.Column('date_update', sa.TIMESTAMP(), onupdate=sa.func.utc_timestamp()),
    )

    @staticmethod
    def format_date(date):
        return '' if not date else date.isoformat()

    @staticmethod
    def format_comment(comment):
        return {
            'comment_id': comment.comment_id,
            'user_id': comment.user_id,
            'date_create': CommentModel.format_date(comment.date_create),
            'date_update': CommentModel.format_date(comment.date_update),
            'text': comment.text,
        }

    async def get(self, engine, comment_id):
        """Request information about comment by comment_id"""

        async with engine.acquire() as conn:
            query = self.table.select(self.table.c.comment_id == comment_id)
            return await(await conn.execute(query)).first()

    async def create(self, engine, user_id, text):
        """Request to create comment"""

        result = None
        async with engine.acquire() as conn:
            trans = await conn.begin()
            try:
                result = await conn.execute(self.table.insert().values(
                    {'user_id': user_id, 'text': text}
                ))
            except Exception as e:
                await trans.rollback()
                log.debug('Error on create comment: {}'.format(e))
                return
            else:
                await trans.commit()

        if result:
            return result.lastrowid

    async def update(self, engine, comment_id, text):
        """Request to create comment"""

        result = None
        async with engine.acquire() as conn:
            trans = await conn.begin()
            try:
                query = self.table.update().\
                    where(self.table.c.comment_id == comment_id).\
                    values({'text': text})
                result = await conn.execute(query)
            except Exception as e:
                await trans.rollback()
                log.debug('Error on create comment: {}'.format(e))
                return
            else:
                await trans.commit()

        if result:
            return result.rowcount

    async def delete(self, engine, comment_id):
        """Request to delete comment by comment_id"""

        async with engine.acquire() as conn:
            trans = await conn.begin()
            try:
                query = self.table.delete(self.table.c.id == comment_id)
                result = await conn.execute(query)
            except Exception as e:
                log.debug('Error on delete comment: {}'.format(e))
                await trans.rollback()
                return
            else:
                await trans.commit()

            return result.rowcount


class CommentTreeModel(object):

    __name__ = 'comment_tree'

    metadata = sa.MetaData()

    RECORD_ON_PAGE = 50

    table = sa.Table(
        'comment_tree',
        metadata,
        sa.Column('ancestor_id', sa.Integer(), sa.ForeignKey("comment.comment_id"), nullable=False),
        sa.Column('descendant_id', sa.Integer(), sa.ForeignKey("comment.comment_id"), nullable=False),
        sa.Column('nearest_ancestor_id', sa.Integer(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), sa.ForeignKey("entity.id"), nullable=False),
    )

    async def get_all(self, engine, entity_id, page):
        """Request information about comments first level"""

        comments = []
        page = page if page > 0 else 1
        offset = (page - 1) * self.RECORD_ON_PAGE

        j = sa.join(self.table, CommentModel.table,
                    self.table.c.ancestor_id == CommentModel.table.c.comment_id)
        query = sa.select([CommentModel.table]).select_from(j).\
            where(self.table.c.entity_id == entity_id).\
            where(self.table.c.level == 0).\
            offset(offset).\
            limit(self.RECORD_ON_PAGE)

        async with engine.acquire() as conn:
            async for row in conn.execute(query):
                comments.append(CommentModel.format_comment(row))

        return comments

    async def get_once(self, engine, comment_id):
        """Request for getting information about comment_tree for once comment"""

        async with engine.acquire() as conn:
            query = self.table.select().\
                where(self.table.c.ancestor_id == self.table.c.descendant_id).\
                where(self.table.c.ancestor_id == comment_id)
            return await(await conn.execute(query)).first()

    async def has_descendant(self, engine, comment_id):
        """Request to check for descendants"""

        async with engine.acquire() as conn:
            query = self.table.select().\
                where(self.table.c.ancestor_id != self.table.c.descendant_id).\
                where(self.table.c.ancestor_id == comment_id)
            return await(await conn.execute(query)).first()

    async def create(self, engine, user_id, entity_id, text, ancestor_id=None):
        """Request to create comment"""

        result = None
        ancestor = None
        if ancestor_id:
            ancestor = await self.get_once(engine, ancestor_id)
            if not ancestor:
                log.debug('Not found ancestor for id: {}'.format(ancestor_id))
                return result

            if ancestor.entity_id != entity_id:
                log.debug('Not equal request entity_id and ancestor entity_id')
                return result

        async with engine.acquire() as conn:
            trans = await conn.begin()
            try:
                new_comment = await conn.execute(CommentModel.table.insert().values(
                    {'user_id': user_id, 'text': text}
                ))
                if not new_comment:
                    return

                data = {
                    'new_comment_id': new_comment.lastrowid,
                    'ancestor_id': ancestor_id if ancestor_id else 0,
                    'entity_id': entity_id,
                    'level': 0 if not ancestor else ancestor.level + 1
                }

                query = '''INSERT INTO comment_tree (ancestor_id, descendant_id, nearest_ancestor_id, entity_id, level)
                            SELECT ancestor_id, {new_comment_id}, {ancestor_id}, {entity_id}, {level}
                                FROM comment_tree
                                WHERE descendant_id = {ancestor_id}
                           UNION ALL SELECT {new_comment_id}, {new_comment_id}, {ancestor_id}, {entity_id}, {level}'''
                result = await conn.execute(query.format(**data))
            except Exception as e:
                await trans.rollback()
                log.debug('Error on create comment_tree: {}'.format(e))
                return
            else:
                await trans.commit()

        if result:
            return result.lastrowid

    async def delete(self, engine, comment_id):
        """Request to delete comment_tree and comment by comment_id"""

        result = None
        async with engine.acquire() as conn:
            trans = await conn.begin()
            try:
                query = self.table.delete().\
                    where(self.table.c.descendant_id == comment_id)
                if await conn.execute(query):
                    query = CommentModel.table.delete().\
                        where(CommentModel.table.c.comment_id == comment_id)
                    result = await conn.execute(query)
            except Exception as e:
                await trans.rollback()
                log.debug('Error on delete comment: {}'.format(e))
                return
            else:
                await trans.commit()

        if result:
            return result.rowcount
