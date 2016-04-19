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

    def upsert_meta(self, primary_key, metadata_dict):
        # your code here
    def select(self, metadata_dict={}):
        # your code here

    # Feel free to change this to be completely synchronous
    # from here onwards. Return the status and the payload
    async def _send_coro(self, msg, loop):
        # your code here
        return status, payload

    #call `_send` with a well formed message to send.
    #once again replace this function if appropriate
    def _send(self, msg):
        loop = asyncio.get_event_loop()
        coro = asyncio.ensure_future(self._send_coro(msg, loop))
        loop.run_until_complete(coro)
        return coro.result()
