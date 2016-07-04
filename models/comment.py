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

    async def get(self, engine, comment_id):
        """Request information about comment by comment_id"""

        j = sa.join(self.table, CommentModel.table,
                    self.table.c.descendant_id == CommentModel.table.c.comment_id)
        query = sa.select([self.table, CommentModel.table]).select_from(j)
        query = query.where(self.table.c.ancestor_id == comment_id).\
            where(self.table.c.ancestor_id == self.table.c.descendant_id)

        async with engine.acquire() as conn:
            comment = await(await conn.execute(query)).first()
            return dict((key, value) for key, value in comment.items())

    async def get_raw_tree(self, engine, entity_id=None, comment_id=None):
        """Request information about all descendants"""

        j = sa.join(self.table, CommentModel.table,
                    self.table.c.descendant_id == CommentModel.table.c.comment_id)
        query = sa.select([self.table, CommentModel.table]).select_from(j)

        if comment_id:
            ancestor = await self.get_ancestor(engine, comment_id)
            if entity_id and entity_id != ancestor.entity_id:
                return []

            if not entity_id:
                entity_id = ancestor.entity_id
            query = query.where(self.table.c.ancestor_id == comment_id)

        if entity_id:
            query = query.where(self.table.c.entity_id == entity_id)

        async with engine.acquire() as conn:
            return await conn.execute(query)

    async def get_tree(self, engine, entity_id=None, comment_id=None):
        """Format information about all descendants"""

        result = []
        async for row in await self.get_raw_tree(engine, entity_id, comment_id):
            result.append(dict((key, value) for key, value in row.items()))
        return result

    async def get_all_first(self, engine, entity_id, page):
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
                data = dict((key, value) for key, value in row.items())
                data['entity_id'] = int(entity_id)
                comments.append(data)

        return comments

    async def get_ancestor(self, engine, comment_id):
        """Request for getting information about ancestor"""

        async with engine.acquire() as conn:
            query = self.table.select().\
                where(self.table.c.ancestor_id == self.table.c.descendant_id).\
                where(self.table.c.descendant_id == comment_id)
            return await(await conn.execute(query)).first()

    async def has_descendant(self, engine, comment_id):
        """Request to check for descendants"""

        result = False
        async with engine.acquire() as conn:
            query = self.table.select().\
                where(self.table.c.ancestor_id != self.table.c.descendant_id).\
                where(self.table.c.ancestor_id == comment_id)
            comment = await(await conn.execute(query)).first()
            if comment:
                result = True

        return result

    async def create(self, engine, user_id, entity_id, text, ancestor_id=None):
        """Request to create comment"""

        result = None
        ancestor = None
        async with engine.acquire() as conn:
            trans = await conn.begin()

            if ancestor_id:
                ancestor = await self.get_ancestor(engine, ancestor_id)
                if not ancestor:
                    log.debug('Not found ancestor for id: {}'.format(ancestor_id))
                    return result

                if ancestor.entity_id != entity_id:
                    log.debug('Not equal request entity_id and ancestor entity_id')
                    return result

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
