import asyncio
from aiohttp import web
from tsdb import TSDBClient
# from tsdb import TSDBStatus
import timeseries as ts
import json

async def hello(request):
    print(request)
    return web.Response(body=b"Hello, world")

# access by port 8080
app = web.Application()
app.router.add_route('GET', '/', hello)
# app.router.add_route('GET', '/tsdb/test', handler.test_upserts_handler)
# app.router.add_route('GET','/tsbd/select',handler.select_handler)
web.run_app(app)