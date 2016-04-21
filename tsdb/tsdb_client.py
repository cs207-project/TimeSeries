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

    def insert_ts(self, primary_key, ts):
        # your code here, construct from the code in tsdb_ops.py
        message = TSDBOp_InsertTS(primary_key, ts)
        self._send(message.to_json())

    def upsert_meta(self, primary_key, metadata_dict):
        # your code here
        message = TSDBOp_UpsertMeta(primary_key, metadata_dict)
        self._send(message)


    def select(self, metadata_dict={}):
        # your code here
        status, payload = self._send(TSDBOp_Select(metadata_dict).to_json())


        return TSDBStatus(status), payload

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
        return status, payload

    #call `_send` with a well formed message to send.
    #once again replace this function if appropriate
    def _send(self, msg):
        loop = asyncio.get_event_loop()
        coro = asyncio.ensure_future(self._send_coro(msg, loop))
        loop.run_until_complete(coro)
        return coro.result()
