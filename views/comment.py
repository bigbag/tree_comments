"""Class with comment actions"""

import json
import logging as log

from aiohttp import web

from models.comment import CommentModel


class CommentView:

    def __init__(self):
        pass

    async def list(self, request):
        """Returns information about comments"""

        entity_id = request.GET.get('entity_id')
        if not entity_id:
            log.debug('Not found entity_id in request')
            raise web.HTTPBadRequest()

        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            log.debug('Page ')
            raise web.HTTPBadRequest()

        comments = await CommentModel().get_all(
            request.app['db'], entity_id, page)
        if not comments:
            log.debug('Not found comment for entity_id {}, on page {}'.format(
                entity_id, page))
            raise web.HTTPNotFound()

        return web.Response(
            body=json.dumps(comments).encode('utf-8'),
            content_type='application/json')

    async def create(self, request):
        """Create a user with given name"""

        data = await request.post()
        user_id = data.get('user_id')
        entity_id = data.get('entity_id')
        text = data.get('text')
        if not user_id or not entity_id or not text:
            log.debug('Not found user_id or entity_id or text in request')
            raise web.HTTPBadRequest()

        comment_id = await CommentModel().create(
            request.app['db'],
            user_id,
            entity_id,
            text,
            data.get('parent_id')
        )
        if not comment_id:
            raise web.HTTPBadRequest()

        url = request.app.router['comment_details'].url(parts={'comment_id': comment_id})
        return web.HTTPCreated(
            body=json.dumps({'url': url}).encode('utf-8'),
            content_type='application/json')

    async def delete(self, request):
        comment_id = request.match_info.get('comment_id')
        result = await CommentModel().delete(request.app['db'], comment_id)

        if not result:
            raise web.HTTPBadRequest()

        return web.HTTPOk()
