"""Class with user actions"""

import logging as log
from aiohttp import web

from helpers import json
from models.user import UserModel


class UserView:

    def __init__(self):
        pass

    async def get_all(self, request):
        """Returns information about all users"""

        users = await UserModel().get_all(request.app['db'])
        if not users:
            log.debug('Not found users')
            raise web.HTTPNotFound()

        return web.Response(
            body=json.dumps(users).encode('utf-8'),
            content_type='application/json')

    async def get(self, request):
        """Returns information about user by user_id"""

        user_id = request.match_info.get('user_id')
        user = await UserModel().get(request.app['db'], user_id)
        if not user:
            log.debug('Not found user for user_id {}'.format(user_id))
            raise web.HTTPNotFound()

        return web.Response(
            body=json.dumps(user).encode('utf-8'),
            content_type='application/json')

    async def create(self, request):
        """Create user with given name"""

        data = await request.post()
        user_name = data.get('name')
        if not user_name:
            log.debug('Not found user name in request')
            raise web.HTTPBadRequest()

        user_id = await UserModel().create(request.app['db'], user_name)
        if not user_id:
            log.debug('Not unique user name {}'.format(user_name))
            raise web.HTTPBadRequest()

        url = request.app.router['user_details'].url(parts={'user_id': user_id})
        return web.HTTPCreated(
            body=json.dumps({'url': url}).encode('utf-8'),
            content_type='application/json')

    async def delete(self, request):
        """Removes user by user_id"""

        user_id = request.match_info.get('user_id')
        result = await UserModel().delete(request.app['db'], user_id)

        if not result:
            log.debug('Not found user for user_id {}'.format(user_id))
            raise web.HTTPNotFound()

        return web.HTTPOk()
