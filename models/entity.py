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
        sa.Column('create_date', sa.TIMESTAMP, nullable=False),
    )

    async def check_name_unique(self, engine, entity_name, entity_type):
        """Check the entity_name and entity_type for uniqueness"""

        is_valid = False
        async with engine.acquire() as conn:
            query = self.table.select().\
                where(self.table.c.name == entity_name).\
                where(self.table.c.type == entity_type)
            result = await(await conn.execute(query)).scalar()
            if not result:
                is_valid = True

        return is_valid

    async def get_all(self, engine):
        """Request information about all entities"""

        entities = []
        async with engine.acquire() as conn:
            async for row in conn.execute(self.table.select()):
                entities.append(
                    {
                        'id': row.id,
                        'name': row.name,
                        'type': row.type
                    }
                )

        return entities

    async def get(self, engine, entity_id):
        """Request information about entity by entity_id"""

        entity = None
        async with engine.acquire() as conn:
            query = self.table.select(self.table.c.id == entity_id)
            result = await(await conn.execute(query)).first()
            if result:
                return {
                    'id': result.id,
                    'name': result.name,
                    'type': result.type
                }

        return entity

    async def create(self, engine, entity_name, entity_type):
        """Request to create entity"""

        is_valid = await self.check_name_unique(engine, entity_name, entity_type)
        if not is_valid:
            return False

        async with engine.acquire() as conn:
            trans = await conn.begin()
            try:
                data = {'name': entity_name, 'type': entity_type}
                result = await conn.execute(self.table.insert().values(data))
            except Exception:
                await trans.rollback()
                return False
            else:
                await trans.commit()

            return result.lastrowid

    async def delete(self, engine, entity_id):
        """Request to delete entity by entity_id"""

        async with engine.acquire() as conn:
            trans = await conn.begin()
            try:
                query = self.table.delete(self.table.c.id == entity_id)
                result = await conn.execute(query)
            except Exception:
                await trans.rollback()
                return False
            else:
                await trans.commit()

            return result.rowcount
