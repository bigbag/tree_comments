"""Class with entity actions"""

import json
import logging as log

from aiohttp import web

from models.entity import EntityModel


class EntityView:

    def __init__(self):
        pass

    async def list(self, request):
        """Returns information about all entities"""

        entities = await EntityModel().get_all(request.app['db'])
        if not entities:
            log.debug('Not found entities')
            raise web.HTTPNotFound()

        return web.Response(
            body=json.dumps(entities).encode('utf-8'),
            content_type='application/json')

    async def get(self, request):
        """Returns information about entity by entity_id"""

        entity_id = request.match_info.get('entity_id')
        entity = await EntityModel().get(request.app['db'], entity_id)
        if not entity:
            log.debug('Not found entity for entity_id {}'.format(entity_id))
            raise web.HTTPNotFound()

        return web.Response(
            body=json.dumps(entity).encode('utf-8'),
            content_type='application/json')

    async def create(self, request):
        """Create a entity with given name, type"""

        data = await request.post()
        entity_name = data.get('name')
        entity_type = data.get('type')
        if not entity_name or not entity_type:
            log.debug('Not found entity_name or entity_type in request')
            raise web.HTTPBadRequest()

        entity_id = await EntityModel().create(
            request.app['db'],
            entity_name,
            entity_type
        )
        if not entity_id:
            raise web.HTTPBadRequest()

        url = request.app.router['entity_details'].url(parts={'entity_id': entity_id})
        return web.HTTPCreated(
            body=json.dumps({'url': url}).encode('utf-8'),
            content_type='application/json')

    async def delete(self, request):
        """Removes entity by entity_id"""

        entity_id = request.match_info.get('entity_id')
        result = await EntityModel().delete(request.app['db'], entity_id)

        if not result:
            log.debug('Not found entity for entity_id {}'.format(entity_id))
            raise web.HTTPNotFound()

        return web.HTTPOk()
