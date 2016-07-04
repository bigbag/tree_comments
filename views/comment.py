"""Class with comment actions"""

import logging as log
from aiohttp import web

from helpers import json
from models.comment import CommentTreeModel, CommentModel
from models.entity import EntityModel
from models.user import UserModel


class CommentView:

    def __init__(self):
        pass

    async def get_all(self, request):
        """Returns information about comments"""

        entity_id = request.GET.get('entity_id')
        if not entity_id:
            log.debug('Not found entity_id in request')
            raise web.HTTPBadRequest()

        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            log.debug('Not valid format page')
            raise web.HTTPBadRequest()

        comments = await CommentTreeModel().get_all_first(
            request.app['db'], entity_id, page)
        if not comments:
            log.debug('Not found comment for entity_id: {}, on page: {}'.format(
                entity_id, page))
            raise web.HTTPNotFound()

        return web.Response(
            body=json.dumps(comments).encode('utf-8'),
            content_type='application/json')

    async def get(self, request):
        """Returns information about comment by comment_id"""

        comment_id = request.match_info.get('comment_id')
        comment = await CommentTreeModel().get(request.app['db'],
                                               comment_id=comment_id)
        if not comment:
            log.debug('Not found comment for comment_id: {}'.format(comment_id))
            raise web.HTTPNotFound()

        return web.Response(
            body=json.dumps(comment).encode('utf-8'),
            content_type='application/json')

    async def search(self, request):
        """Returns information about coments node by comment_id or entity_id"""

        entity_id = request.GET.get('entity_id')
        comment_id = request.GET.get('comment_id')
        try:
            entity_id = int(entity_id) if entity_id else None
            comment_id = int(comment_id) if comment_id else None
        except ValueError:
            log.debug('CREATE: Not valid format entity_id or comment_id')
            pass

        comment = await CommentTreeModel().get_tree(
            request.app['db'], entity_id=entity_id, comment_id=comment_id)
        if not comment:
            log.debug('Not found comments node')
            raise web.HTTPNotFound()

        return web.Response(
            body=json.dumps(comment).encode('utf-8'),
            content_type='application/json')

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
            log.debug('CREATE: Not found entity_id: {}'.format(entity_id))
            raise web.HTTPBadRequest()

        if not await UserModel().get(request.app['db'], user_id):
            log.debug('CREATE: Not found user_id: {}'.format(user_id))
            raise web.HTTPBadRequest()

        ancestor_id = None
        try:
            ancestor_id = int(data.get('ancestor_id'))
        except (TypeError, ValueError):
            pass

        return {
            'entity_id': entity_id,
            'user_id': user_id,
            'ancestor_id': ancestor_id,
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

        log.debug('UPDATE: Not found comment with comment_id: {}'.format(comment_id))
        raise web.HTTPBadRequest()

    async def delete(self, request):
        """Delete comment without descendants"""

        comment_id = request.match_info.get('comment_id')
        if await CommentTreeModel().has_descendant(request.app['db'], comment_id):
            log.debug('DELETE: Comment with comment_id: {} has descendant'.format(comment_id))
            raise web.HTTPBadRequest()

        result = await CommentTreeModel().delete(request.app['db'], comment_id)
        if not result:
            raise web.HTTPBadRequest()

        return web.HTTPOk()
