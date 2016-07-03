"""Class with comment actions"""

import json
import logging as log

from aiohttp import web

from models.comment import CommentTreeModel, CommentModel
from models.entity import EntityModel
from models.user import UserModel


class CommentView:

    def __init__(self):
        pass

    @staticmethod
    def _get_descendant_id(data):
        try:
            return int(data.get('descendant_id'))
        except (TypeError, ValueError):
            return

    async def _create_request_validation(self, request):
        """Checking data to create comment"""

        data = await request.post()
        entity_id = data.get('entity_id')
        user_id = data.get('user_id')
        text = data.get('text')
        if not user_id or not entity_id or not text:
            log.debug('CREATE: Not found user_id or entity_id or text in request')
            raise web.HTTPBadRequest()

        try:
            user_id = int(user_id)
            entity_id = int(entity_id)
        except ValueError:
            log.debug('CREATE: Not valid format user_id or entity_id')
            raise web.HTTPBadRequest()

        if not await EntityModel().get(request.app['db'], entity_id):
            log.debug('CREATE: Not found entity_id {}'.format(entity_id))
            raise web.HTTPBadRequest()

        if not await UserModel().get(request.app['db'], user_id):
            log.debug('CREATE: Not found user_id {}'.format(user_id))
            raise web.HTTPBadRequest()

        return {
            'entity_id': entity_id,
            'user_id': user_id,
            'descendant_id': self._get_descendant_id(data),
            'text': text
        }

    async def create(self, request):
        """Create comment"""

        data = await self._create_request_validation(request)
        data['engine'] = request.app['db']
        comment_id = await CommentTreeModel().create(**data)
        if not comment_id:
            raise web.HTTPBadRequest()

        url = request.app.router['comment_details'].url(parts={'comment_id': comment_id})
        return web.HTTPCreated(
            body=json.dumps({'url': url}).encode('utf-8'),
            content_type='application/json')

    async def update(self, request):
        """Update comment"""

        comment_id = request.match_info.get('comment_id')
        data = await request.post()
        text = data.get('text')
        if not text:
            log.debug('UPDATE: Not found text in request')
            raise web.HTTPBadRequest()

        result = await CommentModel().update(request.app['db'], comment_id, text)
        if result:
            return web.HTTPOk()

        log.debug('UPDATE: Not found comment with comment_id {}'.format(comment_id))
        raise web.HTTPBadRequest()

    async def delete(self, request):
        comment_id = request.match_info.get('comment_id')
        result = await CommentTreeModel().delete(request.app['db'], comment_id)

        if not result:
            raise web.HTTPBadRequest()

        return web.HTTPOk()
