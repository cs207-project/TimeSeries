import asyncio
from .dictdb import DictDB
from importlib import import_module
from collections import defaultdict
from .tsdb_serialization import Deserializer, serialize
from .tsdb_error import *
from .tsdb_ops import *


class TSDBProtocol(asyncio.Protocol):
    def __init__(self, server):
        self.server = server
        self.deserializer = Deserializer()
        self.futures = []

    def _insert_ts(self, op):
        "server function for inserting a time series"
        try:
            self.server.db.insert_ts(op['pk'], op['ts'])
        except ValueError as e:
            print(e)
            return TSDBOp_Return(TSDBStatus.INVALID_KEY, op['op'])
        return TSDBOp_Return(TSDBStatus.OK, op['op'])

    def _upsert_meta(self, op):
        "server function for upserting metadata corresponding to a time series"
        self.server.db.upsert_meta(op['pk'], op['md'])
        return TSDBOp_Return(TSDBStatus.OK, op['op'])

    def _select(self, op):
        "server function for select"
        loids = self.server.db.select(op['md'])
        return TSDBOp_Return(TSDBStatus.OK, op['op'], loids)


    def connection_made(self, conn):
        "callback for when the conection is made."
        #connection or transport is saved as an instance variable
        self.conn = conn

    def data_received(self, data):
        """
        callback for when data comes. This is the workhorse function which calls database functionality, gets results if appropriate (for select), and bundles them back to the client.
        """
        print('S> data received ['+str(len(data))+']: '+str(data))
        self.deserializer.append(data)
        if self.deserializer.ready():
            msg = self.deserializer.deserialize()
            status = TSDBStatus.OK  # until proven otherwise.
            response = TSDBOp_Return(status, None)  # until proven otherwise.
            try:
                op = TSDBOp.from_json(msg)
            except TypeError as e:
                response = TSDBOp_Return(TSDBStatus.INVALID_OPERATION, None)
            if status is TSDBStatus.OK:
                if isinstance(op, TSDBOp_InsertTS):
                    response = self._insert_ts(op)
                elif isinstance(op, TSDBOp_UpsertMeta):
                    response = self._upsert_meta(op)
                elif isinstance(op, TSDBOp_Select):
                    response = self._select(op)
                else:
                    response = TSDBOp_Return(TSDBStatus.UNKNOWN_ERROR, op['op'])

            self.conn.write(serialize(response.to_json()))
            self.conn.close()

    def connection_lost(self, transport):
        "callbackfor when the client closes the connection"
        print('S> connection lost')


class TSDBServer(object):

    def __init__(self, db, port=9999):
        self.port = port
        self.db = db
        self.triggers = defaultdict(list)  # for later
        self.autokeys = {}

    def exception_handler(self, loop, context):
        print('S> EXCEPTION:', str(context))
        loop.stop()

    def run(self):
        "implements our event loop"
        loop = asyncio.get_event_loop()
        # NOTE: enable this if you'd rather have the server stop on an error
        #       currently it dumps the protocol and keeps going; new connections
        #       are unaffected. Rather nice, actually.
        #loop.set_exception_handler(self.exception_handler)
        self.listener = loop.create_server(lambda: TSDBProtocol(self), '127.0.0.1', self.port)
        print('S> Starting TSDB server on port',self.port)
        listener = loop.run_until_complete(self.listener)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print('S> Exiting.')
        except Exception as e:
            print('S> Exception:',e)
        finally:
            listener.close()
            loop.close()
