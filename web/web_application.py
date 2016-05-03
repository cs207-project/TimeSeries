import asyncio
from aiohttp import web
from tsdb import TSDBClient
# from tsdb import TSDBStatus
import timeseries as ts
import json

# =======================
# Set Router in Web Application
# =======================
class WebApplication(object):
    """
    for REST API part (final project requirement)

    Attributes
    ----------
    app : aiohttp web.Application() object
        web application that deal with REST API
    handler : Handler object
        access server and do required work based on RESTful manner
    """
    def __init__(self):
        # ================
        # set Router here
        # ================
        self.app = web.Application()
        self.handler = Handler()
        self.app.router.add_route('GET', '/', self.handler.tsdb_root)
        self.app.router.add_route('GET', '/tsdb', self.handler.tsdb_root)
        self.app.router.add_route('GET', '/tsdb/select', self.handler.tsdb_select)
        self.app.router.add_route('GET', '/tsdb/augmented_select', self.handler.tsdb_augmented_select)
        # self.app.router.add_route('POST', '/tsdb/add/ts', self.handler.add_ts_handler)
        # self.app.router.add_route('POST', '/tsdb/add/trigger', self.handler.add_trigger_handler)
        # self.app.router.add_route('POST', '/tsdb/remove/trigger', self.handler.remove_trigger_handler)
        # self.app.router.add_route('POST', '/tsdb/add/metadata', self.handler.add_metadata_handler)

    def run(self):
        # run web Application()
        web.run_app(self.app)

# ===========================
# Handlers to work with TSDB
# ===========================
class Handler(object):
    """
    Event handlers to deal with TSDB based on RESTful manner

    Attributes
    ----------
    client : TSDBClient object

    Methods
    -------
    tsdb_root
    tsdb_select
    tsdb_augment_select
    """
    def __init__(self):
        self.client = TSDBClient()

    async def tsdb_root(self, request):
        root_view = """\
# =================================
# CS 207 Final Project
# TSDB RESTful API Implementation
# =================================

# Followings are the rule for router

localhost:8080/tsdb                     root page
localhost:8080/tsdb/select              select
localhost:8080/tsdb/augmented_select    augmented select
/tsdb/add/ts --> insert timeseries
/tsdb/add/trigger --> add trigger
/tsdb/remove/trigger --> remove trigger
/tsdb/add/metadata --> insert metadata
"""
        return web.Response(body=root_view.encode('utf-8'))

    async def tsdb_select(self, request):
        if 'query' not in request.GET:
            # request.GET is multidict() in aiohttp
            # When parameters are not passed through URL
            # ex) localhost:8080/tsdb/select
            select_view = """\
# =================================
# CS 207 Final Project
# TSDB RESTful API Implementation
# =================================

# SELECT router rule example

localhost:8080/tsdb/select?query={}
localhost:8080/tsdb/select?query={"md":{"order": 1}, "fields":["ts"], "additional":{"sort_by":"-order"}}

!!! NOTE !!!
Every string should be wrapped with ", not '
because ' is automatically encoded to %27 in utf-8,
then json.loads decode it not into dictionary, but string.

metadata_dict(md), fields, additional are all optional.
"""
            return web.Response(body=select_view.encode('utf-8'))
        else: # if there is query parameter in URL
            try:
                query = json.loads(request.GET['query'])
                if 'md' in query:
                    metadata_dict = query['md']
                else:
                    metadata_dict = {}
                if 'fields' in query:
                    fields = query['fields']
                else:
                    fields = None
                if 'additional' in query:
                    additional = query['additional']
                else:
                    additional = None

                status, payload = await self.client.select(metadata_dict, fields, additional)
                return web.Response(body=json.dumps(payload).encode('utf-8'))

            except Exception as error:
                error_dict = {"msg": "Cannot parse the Request"}
                error_dict["type"] = str(type(error))
                error_dict["args"] = str(error.args)
                return web.Response(body=json.dumps(error_dict).encode('utf-8'))

    async def tsdb_augmented_select(self, request):
        if 'query' not in request.GET:
            view = """\
# =================================
# CS 207 Final Project
# TSDB RESTful API Implementation
# =================================

# SELECT router rule example

localhost:8080/tsdb/augment_select?query={"proc":"corr", "target":"d"}
localhost:8080/tsdb/augment_select?query={"proc":"corr", "target":"d", "md":{"order": 1}, "fields":["ts"]}

!!! NOTE !!!
Every string should be wrapped with ", not '
because ' is automatically encoded to %27 in utf-8,
then json.loads decode it not into dictionary, but string.

proc, target -> required
metadata_dict(md), fields, arg -> optional.
"""
            return web.Response(body=view.encode('utf-8'))
        else: # if there is query parameter in URL
            try:
                query = json.loads(request.GET['query'])
                proc = query['proc']
                target = query['target']

                if 'md' in query:
                    metadata_dict = query['md']
                else:
                    metadata_dict = {}
                if 'additional' in query:
                    additional = query['additional']
                else:
                    additional = None
                if 'arg' in query:
                    arg = query['arg']
                else:
                    arg = None

                status, payload = await self.client.augmented_select(proc, target, arg, metadata_dict, additional)
                return web.Response(body=json.dumps(payload).encode('utf-8'))

            except Exception as error:
                error_dict = {"msg": "Cannot parse the Request"}
                error_dict["type"] = str(type(error))
                error_dict["args"] = str(error.args)
                return web.Response(body=json.dumps(error_dict).encode('utf-8'))


if __name__=='__main__':
    webapp = WebApplication()
    webapp.run()