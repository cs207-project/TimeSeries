import asyncio
from .tsdb_serialization import serialize, LENGTH_FIELD_LENGTH, Deserializer
from .tsdb_ops import *
from .tsdb_error import *

class TSDBClient(object):
    """
    The Time Series Database client. This could be used in a python program, web server, or REPL!

    Note
    ----
    Includes basic time-series database client operation like insert_ts, select, sending messages etc.

    """
    def __init__(self, port=9999):
        """
        Instantiate a TSDBClient class object

        Parameters
        ----------
        port : int
            the port client uses to connect to the server. Default: 9999.
        """
        self.port = port
        self.deserializer = Deserializer()

    def insert_ts(self, primary_key, ts):
        """
        Insert a timeseries into the database by sending a request to the server.

        Parameters
        ----------
        primary_key: int
            a unique identifier for the timeseries

        ts: a TimeSeries object
            the timeseries object intended to be inserted to database
        """

        ts_insert = TSDBOp_InsertTS(primary_key, ts)
        self._send(ts_insert.to_json())

    def upsert_meta(self, primary_key, metadata_dict):
        """
        Upserting metadata into the timeseries in the database designated by the promary key by sending the server a request.

        Parameters
        ----------
        primary_key: int
            a unique identifier for the timeseries

        metadata_dict: dict
            the metadata to upserted into the timeseries
        """
        ts_update = TSDBOp_UpsertMeta(primary_key, metadata_dict)
        self._send(ts_update.to_json())

    def select(self, metadata_dict={}, fields=None, additional=None):
        """
        Selecting timeseries elements in the database that match the criteria
        set in metadata_dict and return corresponding fields with additional
        features.

        Parameters
        ----------
        metadata_dict: dict
            the selection criteria (filters)

        fields: dict
            If not `None`, only these fields of the timeseries are returned.
            Otherwise, the timeseries are returned.

        additional: dict
            additional computation to perform on the query matches before they're
            returned. Currently provide "sort_by" and "limit" functionality

        """
        ts_select = TSDBOp_Select(metadata_dict, fields, additional)
        return self._send(ts_select.to_json())

    def augmented_select(self, proc, target, arg=None, metadata_dict={}, additional=None):

        ts_augmented_select = TSDBOp_AugmentedSelect(proc, target, arg, metadata_dict, additional)
        return self._send(ts_augmented_select.to_json())

    def add_trigger(self, proc, onwhat, target, arg):
        """
        Send the server a request to add a trigger.

        Parameters
        ----------
        `proc` : enum
            which of the modules in procs. Options: 'corr', 'junk', 'stats'
        `onwhat` :
            the trigger
        `target` : dict
            metadata to be upserted
        `arg` :
            additional argument
        """
        msg = TSDBOp_AddTrigger(proc, onwhat, target, arg)
        return self._send(msg.to_json())

    def remove_trigger(self, proc, onwhat):
        msg = TSDBOp_RemoveTrigger(proc, onwhat)
        return self._send(msg.to_json())

    def find_similar(self, arg):
        """Send the server a request to find the closest ts to this one
        """
        msg = TSDBOp_FindSimilar(arg)
        status, payload = self._send(msg.to_json())
        return TSDBStatus(status), payload
    # from here onwards. Return the status and the payload
    async def _send_coro(self, msg, loop):
        '''
        Open connection and write the serialized message

        Parameters
        ----------
        msg: json
            unserialised message to be sent
        loop:
            a pluggable event loop with various system-specific implementations provided by asyncio;

        Returns
        -------
        tsdb status and payload
        '''
        reader, writer = await asyncio.open_connection('127.0.0.1', self.port, loop=loop)
        writer.write(serialize(msg))
        await writer.drain()
        # Wait for response
        response = await reader.read()
        writer.close()
        # Deserialize response
        self.deserializer.append(response)
        if self.deserializer.ready():
            deserialized_response = self.deserializer.deserialize()
            status = deserialized_response['status']
            payload = deserialized_response['payload']
        # Print out status and payload
        print('C> status:',str(TSDBStatus(status)))
        print('C> payload:',payload)
        print('-----------')
        print('C> writing')

        return status, payload


    #
    #once again replace this function if appropriate
    def _send(self, msg):
        '''
        Call `_send` with a well formed message to send.

        Parameters
        ----------
        msg: bytes
            serialised message to be sent

        Returns
        -------
        result of coroutines execution
        '''

        loop = asyncio.get_event_loop()
        coro = asyncio.ensure_future(self._send_coro(msg, loop))
        loop.run_until_complete(coro)
        return coro.result()

