
from timeseries import TimeSeries
import numpy as np
from scipy.stats import norm
import time
identity = lambda x: x
from tsdb.tsdb_constants import schema_convert
from tsdb.tsdb_ops import *
from tsdb.tsdb_server import *
from timeseries import TimeSeries
import unittest

class TSDBServerTests(unittest.TestCase):
    def setUp(self):
        for i in range(5):
            schema_convert["d_vp-{}".format(i)] = {'convert': float, 'index': 1}
        self.db = DictDB(schema_convert, 'pk')
        self.server = TSDBServer(self.db)
        self.prot = TSDBProtocol(self.server)

        # Dumb server tests
        assert(self.server.db == self.db)
        assert(self.server.port == 9999)
        self.t1 = np.arange(0.0, 1.0, 0.01)
        self.v1 = norm.pdf(self.t1, 60, 10)
        self.t2 = np.arange(1.0, 2.0, 0.01)
        self.v2 = norm.pdf(self.t1, 60, 10)

        self.ats1 = TimeSeries(self.t1, self.v1)
        self.ats2 = TimeSeries(self.t2, self.v2)

    def tearDown(self):
        pass

    async def test_protocol(self):

        # Test TSDBOp_InsertTS
        insert_op = {}
        insert_op['pk'] = 1
        insert_op['ts'] = self.ats1
        insert_op['op'] = 'insert_ts'
        InsertedTS = await TSDBOp_InsertTS(1, self.ats1)
        assert(insert_op == InsertedTS)

    # Test Protocol Insert
        insert_return = await self.prot._insert_ts(insert_op)
        assert(insert_return['op'] == 'insert_ts')
        assert(insert_return['status'] == TSDBStatus.OK)
        assert(insert_return['payload'] == None)
        inserted_row = self.server.db.rows[1]
        assert(inserted_row['pk'] == 1)
        assert(inserted_row['ts'] == self.ats1)

    # Add some more data
        await self.prot._insert_ts(TSDBOp_InsertTS(2, self.ats1))
        inserted_row = self.server.db.rows[2]
        assert(inserted_row['ts'] == self.ats1)

        # Test Protocol Upsert
        upserted_meta = await TSDBOp_UpsertMeta(2, {'ts': self.ats2, 'order': 1})
        upsert_return = self.prot._upsert_meta(upserted_meta)
        assert(upsert_return['op'] == 'upsert_meta')
        assert(upsert_return['status'] == TSDBStatus.OK)
        assert(upsert_return['payload'] == None)

        # Test Protocol Select (None fields)
        metadata_dict = {'pk': {'>': 0}}
        fields = None
        additional = None
        select_op = await TSDBOp_Select(metadata_dict, fields, additional)
        select_return = self.prot._select(select_op)
        assert(select_return['op'] == 'select')
        assert(select_return['status'] == TSDBStatus.OK)
        assert(select_return['payload'][1] == {})
        assert(select_return['payload'][2] == {})

        # Test Protocol Select
        metadata_dict = {'pk': {'>': 0}}
        fields = ['ts']
        additional = None
        select_op = await TSDBOp_Select(metadata_dict, fields, additional)
        select_return = self.prot._select(select_op)
        assert(select_return['op'] == 'select')
        assert(select_return['status'] == TSDBStatus.OK)
        assert(select_return['payload'][1]['ts'] == self.ats1)
        assert(select_return['payload'][2]['ts'] == self.ats2)

        # Test Add Trigger
        add_trigger_op = await TSDBOp_AddTrigger('stats', 'insert_ts', ['mean', 'std'], None)
        self.prot._add_trigger(add_trigger_op)

        mod = import_module('procs.stats')
        storedproc = getattr(mod,'main')

        assert(self.server.triggers['insert_ts'] ==  [('stats', storedproc, None, ['mean', 'std'])])

    def test_protocol_delete(self):

        insert_op = {}
        insert_op['pk'] = 1
        insert_op['ts'] = self.ats1
        insert_op['op'] = 'insert_ts'

        # Test Protocol Insert
        insert_return = self.prot._insert_ts(insert_op)
        assert(insert_return['op'] == 'insert_ts')
        assert(insert_return['status'] == TSDBStatus.OK)
        assert(insert_return['payload'] == None)
        inserted_row = self.server.db.rows[1]
        assert(inserted_row['pk'] == 1)
        assert(inserted_row['ts'] == self.ats1)

        insert_return2 = self.prot._insert_ts(insert_op)
        assert(insert_return2['op'] == 'insert_ts')
        assert(insert_return2['status'] == TSDBStatus.INVALID_KEY)

        delete_op = {}
        delete_op['pk'] = 1
        delete_op['op'] = 'delete_ts'

        delete_return = self.prot._delete_ts(delete_op)
        assert(delete_return['op'] == 'delete_ts')
        assert(delete_return['status'] == TSDBStatus.OK)
        assert(delete_return['payload'] == None)
        print(len(self.server.db.rows))
        assert (len(self.server.db.rows) == 0)

        with self.assertRaises(ValueError):
            delete_return2 = self.prot._delete_ts(delete_op)

    def test_protocol_triggers(self):
        # Test Add Trigger
        add_trigger_op = TSDBOp_AddTrigger('stats', 'insert_ts', ['mean', 'std'], None)
        self.prot._add_trigger(add_trigger_op)

        mod = import_module('procs.stats')
        storedproc = getattr(mod,'main')
        assert(self.server.triggers['insert_ts'] ==  [('stats', storedproc, None, ['mean', 'std'])])


        # Test delete Trigger
        delete_trigger_op = TSDBOp_RemoveTrigger('stats', 'insert_ts')
        self.prot._remove_trigger(delete_trigger_op)

        mod = import_module('procs.stats')
        storedproc = getattr(mod,'main')
        assert(self.server.triggers['insert_ts'] ==  [])


    def test_augmented_select(self):

        insert_op = {}
        insert_op['pk'] = 1
        insert_op['ts'] = self.ats1
        insert_op['op'] = 'insert_ts'

        # Test Protocol Insert
        insert_return = self.prot._insert_ts(insert_op)
        assert(insert_return['op'] == 'insert_ts')
        assert(insert_return['status'] == TSDBStatus.OK)
        assert(insert_return['payload'] == None)
        inserted_row = self.server.db.rows[1]
        assert(inserted_row['pk'] == 1)
        assert(inserted_row['ts'] == self.ats1)

        # Test Protocol Select (None fields)
        metadata_dict = {'pk': {'>': 0}}
        fields = None
        additional = None
        aug_select_op = TSDBOp_AugmentedSelect('corr', ['mean', 'std'], [self.t2,self.v2], metadata_dict, additional )
        aug_select_return = self.prot._augmented_select(aug_select_op)

        assert(aug_select_return['op'] == 'augmented_select')
        assert(aug_select_return['status'] == TSDBStatus.OK)
        print(aug_select_return['payload'])
        assert(aug_select_return['payload'] == {1: {'mean': 0.0}})

test = TSDBServerTests()
test.setUp()

test.test_protocol()

test.test_protocol_delete()

test.test_protocol_triggers()

test.test_augmented_select()
# #
# def tsmaker(m, s, j):
#     '''
#     Helper function: randomly generates a time series for testing.
#     Parameters
#     ----------
#     m : float
#         Mean value for generating time series data
#     s : float
#         Standard deviation value for generating time series data
#     j : float
#         Quantifies the "jitter" to add to the time series data
#     Returns
#     -------
#     A time series and associated meta data.
#     '''
#
#     # generate metadata
#     meta = {}
#     meta['order'] = int(np.random.choice(
#         [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]))
#     meta['blarg'] = int(np.random.choice([1, 2]))
#     meta['vp'] = False  # initialize vantage point indicator as negative
#
#     # generate time series data
#     t = np.arange(0.0, 1.0, 0.01)
#     v = norm.pdf(t, m, s) + j * np.random.randn(100)
#
#     # return time series and metadata
#     return meta, TimeSeries(t, v)
#
#
# def test_server():
#
#     ########################################
#     #
#     # set up
#     #
#     ########################################
#
#     # initialize database
#     db = DictDB(schema_convert, 'pk')
#
#     # initialize server
#     server = TSDBServer(db)
#     assert server.db == db
#     assert server.port == 9999
#
#     # initialize protocol
#     protocol = TSDBProtocol(server)
#     assert protocol.server == server
#
#     # parameters for testing
#     num_ts = 25
#     num_vps = 5
#
#     ########################################
#     #
#     # create dummy data for testing
#     #
#     ########################################
#
#     # a manageable number of test time series
#     mus = np.random.uniform(low=0.0, high=1.0, size=num_ts)
#     sigs = np.random.uniform(low=0.05, high=0.4, size=num_ts)
#     jits = np.random.uniform(low=0.05, high=0.2, size=num_ts)
#
#     # initialize dictionaries for time series and their metadata
#     tsdict = {}
#     metadict = {}
#
#     # fill dictionaries with randomly generated entries for database
#     for i, m, s, j in zip(range(num_ts), mus, sigs, jits):
#         meta, tsrs = tsmaker(m, s, j)  # generate data
#         pk = "ts-{}".format(i)  # generate primary key
#         tsdict[pk] = tsrs  # store time series data
#         metadict[pk] = meta  # store metadata
#
#     # for testing later on
#     ts_keys = sorted(tsdict.keys())
#
#     ########################################
#     #
#     # for all tests below:
#     # - package the operation
#     # - test that this is packaged as expected
#     # - run the operation
#     # - unpack the results of running the operation
#     # - test that the return values are as expected
#     #
#     ########################################
#
#     ########################################
#     #
#     # test time series insert
#     #
#     ########################################
#
#     for k in tsdict:
#         # package the operation
#         op = {'op': 'insert_ts', 'pk': k, 'ts': tsdict[k]}
#         # test that this is packaged as expected
#         assert op == TSDBOp_InsertTS(k, tsdict[k])
#         # run operation
#         result = protocol._insert_ts(op)
#         # unpack results
#         status, payload = result['status'], result['payload']
#         # test that return values are as expected
#         assert status == TSDBStatus.OK
#         assert payload is None
#
#     idx = np.random.choice(list(tsdict.keys()))
#
#     # try to insert a duplicate primary key
#     op = {'op': 'insert_ts', 'pk': idx, 'ts': tsdict[idx]}
#     # test that this is packaged as expected
#     assert op == TSDBOp_InsertTS(idx, tsdict[idx])
#     # run operation
#     result = protocol._insert_ts(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.INVALID_KEY
#     assert payload is None
#
#     ########################################
#     #
#     # test time series deletion
#     #
#     ########################################
#
#     idx = np.random.choice(list(tsdict.keys()))
#
#     # delete a valid time series
#
#     # package the operation
#     op = {'op': 'delete_ts', 'pk': idx}
#     # test that this is packaged as expected
#     assert op == TSDBOp_DeleteTS(idx)
#     # run operation
#     result = protocol._delete_ts(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#     # check that it isn't present any more
#
#     # package the operation
#     op = {'op': 'select', 'md': {'pk': idx}, 'fields': None,
#           'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({'pk': idx}, None, None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert len(payload) == 24
#
#     # add it back in
#
#     # package the operation
#     op = {'op': 'insert_ts', 'pk': idx, 'ts': tsdict[idx]}
#     # test that this is packaged as expected
#     assert op == TSDBOp_InsertTS(idx, tsdict[idx])
#     # run operation
#     result = protocol._insert_ts(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#     # check that it's present now
#
#     # package the operation
#     op = {'op': 'select', 'md': {'pk': idx}, 'fields': None,
#           'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({'pk': idx}, None, None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert len(payload) == 25
#     # delete an invalid time series
#
#     # package the operation
#     op = {'op': 'delete_ts', 'pk': 'mistake'}
#     # test that this is packaged as expected
#     assert op == TSDBOp_DeleteTS('mistake')
#     # run operation
#     try:
#         result = protocol._delete_ts(op)
#     except ValueError:
#         print('deletion with mistaken pk test pass')
#
#     ########################################
#     #
#     # test metadata upsert
#     #
#     ########################################
#
#     for k in metadict:
#         # package the operation
#         op = {'op': 'upsert_meta', 'pk': k, 'md': metadict[k]}
#         # test that this is packaged as expected
#         assert op == TSDBOp_UpsertMeta(k, metadict[k])
#         # run operation
#         result = protocol._upsert_meta(op)
#         # unpack results
#         status, payload = result['status'], result['payload']
#         # test that return values are as expected
#         assert status == TSDBStatus.OK
#         assert payload is None
#
#     ########################################
#     #
#     # test select operations
#     #
#     ########################################
#
#     # select all database entries; no metadata fields
#
#     # package the operation
#     op = {'op': 'select', 'md': {}, 'fields': None, 'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({}, None, None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     if len(payload) > 0:
#         assert list(payload[list(payload.keys())[0]].keys()) == []
#         assert sorted(payload.keys()) == ts_keys
#
#     # select all database entries; no metadata fields; sort by primary key
#
#     # package the operation
#     op = {'op': 'select', 'md': {}, 'fields': None,
#           'additional': {'sort_by': '+pk'}}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({}, None, {'sort_by': '+pk'})
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     if len(payload) > 0:
#         assert list(payload[list(payload.keys())[0]].keys()) == []
#
#     # select all database entries; all metadata fields
#
#     # package the operation
#     op = {'op': 'select', 'md': {}, 'fields': [], 'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({}, [], None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     if len(payload) > 0:
#         assert (sorted(list(payload[list(payload.keys())[0]].keys())) ==
#                 ['blarg', 'order', 'pk', 'vp'])
#         assert sorted(payload.keys()) == ts_keys
#
#     # select all database entries; all invalid metadata fields
#
#     # package the operation
#     op = {'op': 'select', 'md': {}, 'fields': ['wrong', 'oops'],
#           'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({}, ['wrong', 'oops'], None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     if len(payload) > 0:
#         assert sorted(list(payload[list(payload.keys())[0]].keys())) == []
#         assert sorted(payload.keys()) == ts_keys
#
#     # select all database entries; some invalid metadata fields
#
#     # package the operation
#     op = {'op': 'select', 'md': {}, 'fields': ['not_there', 'blarg'],
#           'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({}, ['not_there', 'blarg'], None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     if len(payload) > 0:
#         assert list(payload[list(payload.keys())[0]].keys()) == ['blarg']
#         assert sorted(payload.keys()) == ts_keys
#
#     # select all database entries; specific metadata fields
#
#     # package the operation
#     op = {'op': 'select', 'md': {}, 'fields': ['blarg', 'order'],
#           'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({}, ['blarg', 'order'], None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     if len(payload) > 0:
#         assert (sorted(list(payload[list(payload.keys())[0]].keys())) ==
#                 ['blarg', 'order'])
#         assert sorted(payload.keys()) == ts_keys
#
#     # not present based on how time series were generated
#
#     # package the operation
#     op = {'op': 'select', 'md': {'order': 10}, 'fields': None,
#           'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({'order': 10}, None, None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert len(payload) == 0
#
#     # not present based on how time series were generated
#
#     # package the operation
#     op = {'op': 'select', 'md': {'blarg': 0}, 'fields': None,
#           'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({'blarg': 0}, None, None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert len(payload) == 0
#
#     # multiple select criteria
#     # not present based on how time series were generated
#
#     # package the operation
#     op = {'op': 'select', 'md': {'order': 10, 'blarg': 0}, 'fields': None,
#           'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({'order': 10, 'blarg': 0}, None, None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert len(payload) == 0
#
#     # operator select criteria
#     # not present based on how time series were generated
#
#     # package the operation
#     op = {'op': 'select', 'md': {'order': {'>=': 10}}, 'fields': None,
#           'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({'order': {'>=': 10}}, None, None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert len(payload) == 0
#
#     # operator select criteria
#     # present based on how time series were generated
#
#     # package the operation
#     op = {'op': 'select', 'md': {'order': {'<': 10}}, 'fields': None,
#           'additional': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_Select({'order': {'<': 10}}, None, None)
#     # run operation
#     result = protocol._select(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert len(payload) > 0
#
#     ########################################
#     #
#     # test trigger operations
#     #
#     ########################################
#
#     # add dummy trigger
#
#     # package the operation
#     op = {'op': 'add_trigger', 'proc': 'junk', 'onwhat': 'insert_ts',
#           'target': None, 'arg': 'db:one:ts'}
#     # test that this is packaged as expected
#     assert op == TSDBOp_AddTrigger('junk', 'insert_ts', None, 'db:one:ts')
#     # run operation
#     result = protocol._add_trigger(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#     # add stats trigger
#
#     # package the operation
#     op = {'op': 'add_trigger', 'proc': 'stats', 'onwhat': 'insert_ts',
#           'target': ['mean', 'std'], 'arg': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_AddTrigger('stats', 'insert_ts', ['mean', 'std'], None)
#     # run operation
#     result = protocol._add_trigger(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#     # try to add a trigger on an invalid event
#
#     # package the operation
#     op = {'op': 'add_trigger', 'proc': 'junk', 'onwhat': 'stuff_happening',
#           'target': None, 'arg': 'db:one:ts'}
#     # test that this is packaged as expected
#     assert op == TSDBOp_AddTrigger(
#         'junk', 'stuff_happening', None, 'db:one:ts')
#     # run operation
#     result = protocol._add_trigger(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     # assert status == TSDBStatus.INVALID_OPERATION
#     assert payload is None
#
#     # try to add a trigger to an invalid field
#
#     # package the operation
#     op = {'op': 'add_trigger', 'proc': 'stats', 'onwhat': 'insert_ts',
#           'target': ['mean', 'wrong_one'], 'arg': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_AddTrigger(
#         'stats', 'insert_ts', ['mean', 'wrong_one'], None)
#     # run operation
#     result = protocol._add_trigger(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#     # try to remove a trigger that doesn't exist
#
#     # package the operation
#     op = {'op': 'remove_trigger', 'proc': 'invalid', 'onwhat': 'insert_ts'}
#     # test that this is packaged as expected
#     assert op == TSDBOp_RemoveTrigger('invalid', 'insert_ts')
#
#     # run operatio
#     result = protocol._remove_trigger(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#     # try to remove a trigger on an invalid event
#
#     # package the operation
#     op = {'op': 'remove_trigger', 'proc': 'stats', 'onwhat': 'invalid'}
#     # test that this is packaged as expected
#     assert op == TSDBOp_RemoveTrigger('stats', 'invalid')
#     # run operation
#     result = protocol._remove_trigger(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#     # try to remove a trigger associated with a particular target
#     # (used to delete vantage point representation)
#
#     # package the operation
#     op = {'op': 'remove_trigger', 'proc': 'stats', 'onwhat': 'insert_ts'}
#     # test that this is packaged as expected
#     assert op == TSDBOp_RemoveTrigger('stats', 'insert_ts')
#     # run operation
#     result = protocol._remove_trigger(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#     # add trigger back in
#
#     # package the operation
#     op = {'op': 'add_trigger', 'proc': 'stats', 'onwhat': 'insert_ts',
#           'target': ['mean', 'std'], 'arg': None}
#     # test that this is packaged as expected
#     assert op == TSDBOp_AddTrigger(
#         'stats', 'insert_ts', ['mean', 'std'], None)
#     # run operation
#     result = protocol._add_trigger(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#
#     ########################################
#     #
#     # test augmented select operations
#     #
#     ########################################
#
#     # remove trigger
#
#     op = {'op': 'remove_trigger', 'proc': 'stats', 'onwhat': 'insert_ts'}
#     # test that this is packaged as expected
#     assert op == TSDBOp_RemoveTrigger('stats', 'insert_ts')
#     # run operation
#     result = protocol._remove_trigger(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#     # add a new time series
#
#     # package the operation
#     op = {'op': 'insert_ts', 'pk': 'test', 'ts': tsdict['ts-1']}
#     # test that this is packaged as expected
#     assert op == TSDBOp_InsertTS('test', tsdict['ts-1'])
#     # run operation
#     result = protocol._insert_ts(op)
#     # unpack results
#     status, payload = result['status'], result['payload']
#     # test that return values are as expected
#     assert status == TSDBStatus.OK
#     assert payload is None
#
#     ########################################
#     #
#     # tear down
#     #
#     ########################################
#
#     db = None
#     server = None
#     protocol = None
#
# test_server()