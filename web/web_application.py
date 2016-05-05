import asyncio
from aiohttp import web
from tsdb import TSDBClient
from tsdb.tsdb_error import TSDBStatus
import timeseries as ts
import json

# views to be rendered on web application pages

ROOT_VIEW = """\
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

SELECT_VIEW = """\
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
AUGMENTED_SELECT_VIEW = """\
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
FIND_SIMILAR_VIEW = """\
                # =================================
                # CS 207 Final Project
                # TSDB RESTful API Implementation
                # =================================

                # SELECT tsdb_find_similar example

                localhost:8080/tsdb/augment_select?query={"proc":"corr", "target":"d"}
                localhost:8080/tsdb/augment_select?query={"proc":"corr", "target":"d", "md":{"order": 1}, "fields":["ts"]}

                !!! NOTE !!!
                Every string should be wrapped with ", not '
                because ' is automatically encoded to %27 in utf-8,
                then json.loads decode it not into dictionary, but string.

                proc, target -> required
                metadata_dict(md), fields, arg -> optional.
                """

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
        self.app.router.add_route('POST', '/tsdb/add_ts', self.handler.tsdb_add_ts)
        self.app.router.add_route('POST', '/tsdb/add_trigger', self.handler.tsdb_add_trigger)
        self.app.router.add_route('POST', '/tsdb/remove_trigger', self.handler.tsdb_remove_trigger)
        self.app.router.add_route('POST', '/tsdb/add_metadata', self.handler.tsdb_add_metadata)

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
        root_view = ROOT_VIEW
        return web.Response(body=root_view.encode('utf-8'))

    async def tsdb_select(self, request):
        if 'query' not in request.GET:
            # request.GET is multidict() in aiohttp
            # When parameters are not passed through URL
            # ex) localhost:8080/tsdb/select
            select_view = SELECT_VIEW
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

                status, result = await self.client.select(metadata_dict, fields, additional)

                if status != TSDBStatus.OK:
                    result = "Augmented Selection failed"
                else:
                    raise Exception("Write Failed")

                # return web.Response(body=json.dumps(payload).encode('utf-8'))

            except Exception as error:
                result = {"msg": "Cannot parse the Request"}
                result["type"] = str(type(error))
                result["args"] = str(error.args)

            finally:
                return web.Response(body=json.dumps(result).encode('utf-8'))

    async def tsdb_augmented_select(self, request):
        if 'query' not in request.GET:
            view = AUGMENTED_SELECT_VIEW
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

                status, result = await self.client.augmented_select(proc, target, arg, metadata_dict, additional)
                # return web.Response(body=json.dumps(payload).encode('utf-8'))

                if status != TSDBStatus.OK:
                    result = "Augmented Selection failed"

            except Exception as error:
                result = {"msg": "Cannot parse the Request"}
                result["type"] = str(type(error))
                result["args"] = str(error.args)

            finally:
                return web.Response(body=json.dumps(result).encode('utf-8'))

    async def tsdb_find_similar(self,request):
        """Handler for Find Similar

        Parameters
        ----------
        request : aiotttp.request
            request object with details of the request that was sent to the server

            request.GET['query'] should exist or an error is returned **REQUIRED**

            request.GET['query']['arg'] -> json encoded timeseries that is the reference to
            which we're trying to find the closest match **REQUIRED**

        Returns
        -------
        web.Response
            JSON encoded results of the augmented select
        """
        try:
            if 'query' not in request.GET:
                view = FIND_SIMILAR_VIEW
                return web.Response(body=view.encode('utf-8'))

            json_query = json.loads(request.GET['query'])
            arg = json_query['arg']

            status, result = await self.client.find_similar(arg)

            if status !=TSDBStatus.OK:
                result = "Finding similar failed for argument, please check again. ".format(arg)

        except Exception as error:
            result = {"msg": "Could not parse request. Please see documentation."}
            result["type"] = str(type(error))
            result["args"] = str(error.args)

        finally:
            return web.Response(body=json.dumps(result).encode('utf-8'))

    async def tsdb_add_ts(self,request):
        """Handler for add time series

        Parameters
        ----------
        request : aiotttp.request
            request object with details of the request that was sent to the server

            request must be JSON encoded

            request.json()['primary_key'] --> primary key for this timeseries in the database. **REQUIRED**

            request.json()['ts'] --> timeseries to be added. **REQUIRED**


        Returns
        -------
        web.Response
            JSON encoded text indicating success or failure of write
        """
        try:
            request_dict = await request.json()

            pk = request_dict['primary_key']
            t = ts.TimeSeries(*request_dict['ts'])
            status, result = await self.client.insert_ts(pk,t)

            if status ==TSDBStatus.OK:
                result = "Successfully inserted timeseries {}".format(pk)
            else:
                result = "DB Insertion failed with pk {},ts {} , please check again. ".format(pk, *req_dict['ts'])

        except Exception as error:
            result = {"msg": "Could not parse request. Please see documentation."}
            result["type"] = str(type(error))
            result["args"] = str(error.args)

        finally:
            return web.Response(body=json.dumps(result).encode('utf-8'))

    async def tsdb_delete_ts(self,request):
        """Handler for delete time series

        Parameters
        ----------
        request : aiotttp.request
            request object with details of the request that was sent to the server

            request must be JSON encoded

            request.json()['primary_key'] --> primary key for this timeseries in the database. **REQUIRED**


        Returns
        -------
        web.Response
            JSON encoded text indicating success or failure of write
        """
        try:
            request_dict = await request.json()

            pk = request_dict['primary_key']
            status, result = await self.client.delete_ts(pk)

            if status ==TSDBStatus.OK:
                result = "Successfully deleted timeseries {}".format(pk)
            else:
                result = "Timeseries Deletion failed with pk {}, please check again. ".format(pk)

        except Exception as error:
            result = {"msg": "Could not parse request. Please see documentation."}
            result["type"] = str(type(error))
            result["args"] = str(error.args)

        finally:
            return web.Response(body=json.dumps(result).encode('utf-8'))

    async def tsdb_add_trigger(self,request):
        """Handler for add trigger

        Parameters
        ----------
        request : aiotttp.request
            request object with details of the request that was sent to the server

            request must be JSON encoded

            request.json()['proc'] --> name of the predefined stored proc to be run **REQUIRED**

            request.json()['onwhat'] --> name of the event after which trigger is run **REQUIRED**

            request.json()['target'] --> list of names of the output varibles in which we store the result of the stored procedure **REQUIRED**

            request.json()['arg'] --> optinal argument sent to the stored procedure

        Returns
        -------
        web.Response
            JSON encoded text indicating success or failure of write
        """
        try:
            request_dict = await request.json()
            status, result = await self.client.add_trigger(
                    request_dict['proc'],request_dict['onwhat'],request_dict['target'], request_dict['arg'])

            if status ==TSDBStatus.OK:
                result = "Successfully added trigger"
            else:
                result = "Adding trigger failed for {}, please check again. ".format(request.json())

        except Exception as error:
            result = {"msg": "Could not parse request. Please see documentation."}
            result["type"] = str(type(error))
            result["args"] = str(error.args)

        finally:
            return web.Response(body=json.dumps(result).encode('utf-8'))

    async def tsdb_remove_trigger(self,request):
        """Handler for remove trigger

        Parameters
        ----------
        request : aiotttp.request
            request object with details of the request that was sent to the server

            request must be JSON encoded

            request.json()['proc'] --> name of the predefined stored proc to be run **REQUIRED**

            request.json()['onwhat'] --> name of the event after which trigger is run **REQUIRED**

        Returns
        -------
        web.Response
            JSON encoded text indicating success or failure of write
        """
        try:
            request_dict = await request.json()
            print(request_dict)
            status, payload = await self.client.remove_trigger(
                    request_dict['proc'],request_dict['onwhat'])

            if status ==TSDBStatus.OK:
                result = "Successfully remove trigger"
            else:
                result = "Removing trigger failed for {}, please check again. ".format(request.json())

        except Exception as error:
            result = {"msg": "Could not parse request. Please see documentation."}
            result["type"] = str(type(error))
            result["args"] = str(error.args)

        finally:
            return web.Response(body=json.dumps(result).encode('utf-8'))

    async def tsdb_add_metadata(self,request):
        """Handler for remove trigger

        Parameters
        ----------
        request : aiotttp.request
            request object with details of the request that was sent to the server

            request must be JSON encoded

            request.json()['primary_key'] --> primary key for this timeseries in the database. **REQUIRED**

            request.json()['metadata_dict'] --> dictionary containing the metadata that we want to add to this timeseries **REQUIRED**

        Returns
        -------
        web.Response
            JSON encoded text indicating success or failure of write
        """
        try:
            request_dict = await request.json()
            status, payload = await self.client.upsert_meta(
                    request_dict['primary_key'],request_dict['metadata_dict'])

            if status ==TSDBStatus.OK:
                result = "Successfully add metadata for pk {} metadata {}".format(request_dict['primary_key'], request_dict['metadata_dict'])
            else:
                result = "Adding metadata failed for pk {} metadata {}, please check again.".format(request_dict['primary_key'], request_dict['metadata_dict'])

        except Exception as error:
            result = {"msg": "Could not parse request. Please see documentation."}
            result["type"] = str(type(error))
            result["args"] = str(error.args)

        finally:
            return web.Response(body=json.dumps(result).encode('utf-8'))


if __name__=='__main__':
    webapp = WebApplication()
    webapp.run()