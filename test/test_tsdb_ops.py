import unittest
from unittest.mock import Mock
from tsdb.tsdb_server import *
from tsdb.tsdb_ops import *
import timeseries as ts
import numpy as np
import asyncio
import time
from tsdb.tsdb_constants import schema_convert

class TSDBServerTest(unittest.TestCase):

    def setUp(self):
        self.db = DictDB(schema_convert,'pk')
        self.server = TSDBServer(self.db)
        self.prot = TSDBProtocol(self.server)
        self.des = Deserializer()
        self.vpkeys = ['one']
        self._populate()

    def tearDown(self):
        pass

    def test_upsert_meta1(self):
        msg = TSDBOp_UpsertMeta('one', {'order': 1, 'blarg': 1})
        status, payload =  self._send(msg)
        self.assertIs(payload,None)

    def test_upsert_meta2(self):
        msg = TSDBOp_UpsertMeta('two', {'order': 2})
        status, payload =  self._send(msg)
        self.assertIs(payload,None)

    def test_upsert_meta3(self):
        msg = TSDBOp_UpsertMeta('three', {'order': 1, 'blarg': 2})
        status, payload =  self._send(msg)
        self.assertIs(payload,None)

    def test_upsert_meta4(self):
        msg = TSDBOp_UpsertMeta('four', {'order': 2, 'blarg': 2})
        status, payload =  self._send(msg)
        self.assertIs(payload,None)

    def test_insert_duplicate(self):
        msg = TSDBOp_InsertTS('two',ts.TimeSeries([2, 3, 4],[4, 34, 16]))
        status, payload = self._send(msg)
        self.assertEqual(status,TSDBStatus.INVALID_KEY)

    def test_select1(self):
        msg = TSDBOp_Select({},[],None)
        # msg = {}
        # msg['op'] = 'select'
        # msg['md'] = metadata_dict
        status, payload =  self._send(msg)
        self.assertEqual(payload, None)

    def test_select8(self):
        msg = TSDBOp_UpsertMeta('two', {'order': 2})
        status, payload =  self._send(msg)

        msg = TSDBOp_UpsertMeta('four', {'order': 3, 'blarg': 2})
        status, payload =  self._send(msg)

        msg = TSDBOp_Select({'order': {'>': 1}}, [], {'sort_by':'+order'})
        status, payload = self._send(msg)
        self.assertEqual(payload, None)

        msg = TSDBOp_Select({'order': {'>': 1}}, [], {'sort_by':'-order'})
        status, payload = self._send(msg)
        self.assertEqual(payload, None)

        msg = TSDBOp_UpsertMeta('four', {'order': 2, 'blarg': 2})
        status, payload =  self._send(msg)

    def test_del1(self):
        msg = TSDBOp_DeleteTS('two')
        status, payload = self._send(msg)

        msg = TSDBOp_UpsertMeta('four', {'order': 3, 'blarg': 2})
        status, payload =  self._send(msg)

        msg = TSDBOp_Select({'order': {'>': 1}}, [], {'sort_by':'+order'})
        status, payload = self._send(msg)
        self.assertEqual(payload, None)

        msg = TSDBOp_InsertTS('two',ts.TimeSeries([2, 3, 4],[4, 9, 16]))
        status, payload = self._send(msg)

        msg = TSDBOp_UpsertMeta('four', {'order': 2, 'blarg': 2})
        status, payload =  self._send(msg)

    # def test_augmented_select(self):
    #
    #     msg = TSDBOp_UpsertMeta('two', {'order': 2})
    #     status, payload =  self._send(msg)
    #
    #     msg = TSDBOp_UpsertMeta('four', {'order': 3, 'blarg': 2})
    #     status, payload =  self._send(msg)
    #     msg = TSDBOp_AugmentedSelect('stats',['mean','std'], None, {'order': {'>': 1}}, None)
    #     status, payload =  self._send(msg)
    #
    #     self.assertEqual(payload['four']['mean'], np.mean([1,0,4]))
    #     self.assertEqual(payload['four']['std'], np.std([1,0,4]))
    #
    #     self.assertEqual(payload['two']['mean'], np.mean([4, 9, 16]))
    #     self.assertEqual(payload['two']['std'], np.std([4, 9, 16]))

    def test_find_similar(self):

        query = ts.TimeSeries([1, 2, 3],[4, 0, 3])
        msg = TSDBOp_FindSimilar(query,self.vpkeys)
        status, payload =  self._send(msg)

        self.assertEqual(payload, None)

    def _populate(self):

        msg = TSDBOp_AddTrigger('corr','insert_ts',['d_vp-1'],ts.TimeSeries([1,2,3],[1,4,9]))
        status, payload =  self._send(msg)

        msg = TSDBOp_InsertTS('one', ts.TimeSeries([1, 2, 3],[1,4,9]))
        status, payload = self._send(msg)

        msg = TSDBOp_InsertTS('two',ts.TimeSeries([1, 2, 3],[4, 9, 16]))
        status, payload = self._send(msg)

        msg = TSDBOp_InsertTS('three',ts.TimeSeries([1, 2, 3],[4,0,16]))
        status, payload = self._send(msg)

        msg = TSDBOp_InsertTS('four',ts.TimeSeries([1, 2, 3],[1,0,4]))
        status, payload = self._send(msg)

    def _send(self,msg):
        w = Mock(spec=asyncio.WriteTransport)
        self.prot.conn = w
        self.prot.data_received(serialize(msg.to_json()))

        for method, args, _ in w.method_calls:
            if method == 'write':
                self.des.append(args[0])
                decodedResponse  = self.des.deserialize()
                obj = TSDBOp_Return.from_json(decodedResponse)
                # print("object!!!")
                # print(obj)
                status = obj['status']  # until proven otherwise.
                payload = obj['payload']  # until proven otherwise.
                break
        return status,payload

if __name__ == '__main__':
    unittest.main()
