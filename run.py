"""Main script"""

import asyncio
import logging as log

from aiohttp import web
from aiomysql.sa import create_engine

from routes import routes
try:
    from settings_local import Config
except:
    from settings import Config


async def db_handler(app, handler):
    """Create database connectionn"""

    async def middleware(request):
        db = app.get('db')
        if not db:
            app['db'] = db = await create_engine(**Config.DB_CONFIG)
        request.app['db'] = db
        return (await handler(request))
    return middleware

async def init(loop):
    """Application Initialization"""

    app = web.Application(loop=loop, middlewares=[db_handler])
    app['config'] = Config
    handler = app.make_handler()

    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])

    srv = loop.create_server(handler, Config.APP_HOST, Config.APP_PORT)
    return srv, handler, app

async def shutdown(server, app, handler):
    """Properly stop the application and close the database connection"""

    db = app.get('db')
    if db:
        db.close()
        await db.wait_closed()

    server.close()
    await app.shutdown()
    await handler.finish_connections(10.0)
    await app.cleanup()


loop = asyncio.get_event_loop()
serv_generator, handler, app = loop.run_until_complete(init(loop))
serv = loop.run_until_complete(serv_generator)

log.debug('Start server {}:{}'.format(Config.APP_HOST, Config.APP_PORT))
try:
    loop.run_forever()
except KeyboardInterrupt:
    log.debug('Stop server begin')
finally:
    loop.run_until_complete(shutdown(serv, app, handler))
    loop.close()
log.debug('Stop server end')
