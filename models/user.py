"""Class with user data model"""

import sqlalchemy as sa


class UserModel(object):

    __name__ = 'user'

    metadata = sa.MetaData()

    table = sa.Table(
        'user',
        metadata,
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('create_date', sa.TIMESTAMP, nullable=False),
    )

    async def check_name_unique(self, engine, user_name):
        """Check the user name for uniqueness"""

        is_valid = False
        async with engine.acquire() as conn:
            query = self.table.select(self.table.c.name == user_name)
            result = await(await conn.execute(query)).scalar()
            if not result:
                is_valid = True

        return is_valid

    async def get_all(self, engine):
        """Request information about all users"""

        users = []
        async with engine.acquire() as conn:
            async for row in conn.execute(self.table.select()):
                users.append({'id': row.id, 'name': row.name})

        return users

    async def get(self, engine, user_id):
        """Request information about user by user_id"""

        user = None
        async with engine.acquire() as conn:
            query = self.table.select(self.table.c.id == user_id)
            result = await(await conn.execute(query)).first()
            if result:
                user = {'id': result.id, 'name': result.name}

        return user

    async def create(self, engine, user_name):
        """Request to create user"""

        is_valid = await self.check_name_unique(engine, user_name)
        if not is_valid:
            return False

        async with engine.acquire() as conn:
            trans = await conn.begin()
            try:
                result = await conn.execute(self.table.insert().
                                            values(name=user_name))
            except Exception:
                await trans.rollback()
                return
            else:
                await trans.commit()

            return result.lastrowid

    async def delete(self, engine, user_id):
        """Request to delete user by user_id"""

        async with engine.acquire() as conn:
            query = self.table.delete().where(self.table.c.id == user_id)
            result = await conn.execute(query)
            return result.rowcount
