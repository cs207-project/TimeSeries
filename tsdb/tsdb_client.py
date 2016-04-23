import asyncio
from .tsdb_serialization import serialize, LENGTH_FIELD_LENGTH, Deserializer
from .tsdb_ops import *
from .tsdb_error import *

class TSDBClient(object):
    """
    The client. This could be used in a python program, web server, or REPL!
    """
    def __init__(self, port=9999):
        self.port = port
        self.deserializer = Deserializer()

    def insert_ts(self, primary_key, ts):
        # your code here, construct from the code in tsdb_ops.py
        ts_insert = TSDBOp_InsertTS(primary_key, ts)
        serialize_ts_insert = serialize(ts_insert.to_json())
        self._send(serialize_ts_insert)

    def upsert_meta(self, primary_key, metadata_dict):
        # your code here
        ts_update = TSDBOp_UpsertMeta(primary_key, metadata_dict)
        serialize_ts_update = serialize(ts_update.to_json())
        self._send(serialize_ts_update)


    def select(self, metadata_dict={}):
        # your code here
        # written by tyh, but not verified yet... - Qing & Grace
        # status, payload = self._send(TSDBOp_Select(metadata_dict).to_json())
        # return TSDBStatus(status), payload
        ts_select = TSDBOp_Select(metadata_dict)
        serialize_ts_select = serialize(ts_select.to_json())
        return self._send(serialize_ts_select)


    # Feel free to change this to be completely synchronous
    # from here onwards. Return the status and the payload
    async def _send_coro(self, msg, loop):
        # Might be useful - Tang
        # open_connection to socket first
        # Print message accordingly(check output.md)
        """
        C> writing
        S> data received [67]: b'C\x00\x00\x00{"ts": [[2, 3, 4], [4, 9, 16]], "pk": "two", "op": "insert_ts"}'
        S> connection lost
        C> status: TSDBStatus.OK
        C> payload: None
        """
        # wait response
        """
        print('S> data received ['+str(len(data))+']: '+str(data))
        self.deserializer.append(data)
        if self.deserializer.ready():
            msg = self.deserializer.deserialize()
        """
        # Above is how to deserialize
        # print status and payload as the shown message

        reader, writer = await asyncio.open_connection('', self.port, loop=loop)
        writer.write(msg)

        response = await reader.read(8192)
        # Deserialize response
        self.deserializer.append(response)
        if self.deserializer.ready():
            deserialized_response = self.deserializer.deserialize()
            status = deserialized_response['status']
            payload = deserialized_response['payload']

        print('C> status:',str(TSDBStatus(status)))
        print('C> payload:',payload)

        # Qing & Grace : We could not figure out how response work.
        # `await reader.read()` actually should be put before writer.close()
        # And using this `response` and `TSOBDp_Return`,
        # we should be able to figure out payload and status.

        return status, payload


    #call `_send` with a well formed message to send.
    #once again replace this function if appropriate
    def _send(self, msg):
        loop = asyncio.get_event_loop()
        coro = asyncio.ensure_future(self._send_coro(msg, loop))
        loop.run_until_complete(coro)
        return coro.result()
