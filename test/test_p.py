import unittest
from tsdb.persistentdb import PersistentDB
import os
import timeseries as ts
import numpy as np
from tsdb.tsdb_constants import schema

class PersistentDBTests(unittest.TestCase):
    def setUp(self):
        self.dirPath = "files/testing"
        if not os.path.isdir(self.dirPath):
            os.makedirs(self.dirPath)
            self._createdDirs = True
        else:
            self._createdDirs = False

        self.schema = schema

        self.tsLength = 100

        self.db = PersistentDB(schema, pk_field='pk', db_name='testing', ts_length=self.tsLength, testing=True)

        for i in range(100):
            pk = 'ts-'+str(i)
            values = np.array(range(self.tsLength)) + i
            series = ts.TimeSeries(values, values)
            meta = {}
            n_order = len(schema['order']['values'])# 11
            meta['order'] = schema['order']['values'][i % n_order]
            n_blarg = 2
            meta['blarg'] = schema['blarg']['values'][i % n_blarg]
            meta['mean'] = float(series.mean())# make sure they are python floats, not numpy floats
            meta['std'] = float(series.std())
            meta['vp'] = False
            self.db.insert_ts(pk, series)
            self.db.upsert_meta(pk, meta)

    def tearDown(self):
        self.db.delete_database()

    def test_bad_testing_dbname(self):
        with self.assertRaises(ValueError):
            otherdb = PersistentDB(self.schema, pk_field='pk', db_name='testing', ts_length=self.tsLength)

    def test_meta_save_ts(self):
        self.db.close()
        self.db = PersistentDB(pk_field='pk', db_name='testing', ts_length=self.tsLength, testing=True)
        self.assertEqual(len(self.db),100)

    def test_schema_change_good(self):
        self.db.close()
        self.db = PersistentDB(self.schema, pk_field='pk', db_name='testing', ts_length=self.tsLength, testing=True)

    def test_schema_change_bad(self):
        badschema = dict(self.schema)
        badschema['blarg'] = {'type': 'int',    'index': 2,    'values': [1, 2, 3]}
        self.db.close()
        with self.assertRaises(ValueError):
            self.db = PersistentDB(badschema, pk_field='pk', db_name='testing', ts_length=self.tsLength, testing=True)

    def test_bad_insert(self):
        pk = 'bad'
        existing = 'ts-0'
        with self.assertRaises(ValueError):
            bad_series = np.array(range(self.tsLength+3))
            self.db.insert_ts(pk, bad_series)
        with self.assertRaises(ValueError):
            values = np.array(range(self.tsLength+5))
            bad_series = ts.TimeSeries(values, values)
            self.db.insert_ts(pk, bad_series)
        with self.assertRaises(ValueError):
            values = np.array(range(self.tsLength))
            series = ts.TimeSeries(values,values)
            self.db.insert_ts('ts-0', series)

    def test_read_meta(self):
        for i in range(100):
            pk = 'ts-'+str(i)
            values = np.array(range(self.tsLength)) + i
            series = ts.TimeSeries(values, values)
            r_meta = self.db._get_meta_list(pk)
            n_order = len(self.schema['order']['values'])# 11
            self.assertEqual(r_meta[self.db.metaheap.fields.index('order')],self.schema['order']['values'][i % n_order])
            n_blarg = 2
            self.assertEqual(r_meta[self.db.metaheap.fields.index('blarg')],self.schema['blarg']['values'][i % n_blarg])
            self.assertEqual(r_meta[self.db.metaheap.fields.index('mean')],series.mean())
            self.assertEqual(r_meta[self.db.metaheap.fields.index('std')],series.std())

    def test_read_ts(self):
        for i in range(100):
            pk = 'ts-'+str(i)
            values = np.array(range(self.tsLength)) + i
            series = ts.TimeSeries(values, values)
            r_ts = self.db._return_ts(pk)
            self.assertEqual(series,r_ts)

    def test_select(self):
        self.db.select({'pk':'ts-0'})
        self.db.select({'pk':'ts-35'})
        self.db.select({'order':2})
        self.db.select({'order':{'>=':2}},['blarg'],{'sort_by':'+blarg'})
        self.db.select({'order':{'>=':2}},['blarg'],{'sort_by':'-order'})
        val = self.db.select({'order':{'>=':2}},['pk','blarg'],{'sort_by':'-order', 'limit':10})
        self.assertTrue(len(val[0]) <= 10)
        with self.assertRaises(ValueError):
            self.db.select({'order':{'>=':2}},['blarg'],{'sort_by':'=blarg'})
        with self.assertRaises(ValueError):
            self.db.select({'order':{'>=':2}},['blarg'],{'sort_by':'-blargh'})
        self.db.select({'order':{'>=':2}},None,{'sort_by':'-blarg'})
        with self.assertRaises(TypeError):
            self.db.select({'order':{'>=':2}},('pk','blarg'),{'sort_by':'-order', 'limit':10})

    def test_indices(self):
        "test indices via the select function, which calls on them"
        n_test = 10
        for i in range(n_test):
            pk = 'ts-'+str(i)
            tsmeta = self.db._get_meta_dict(pk)
            tsinstance = tsmeta['ts']
            # assert values are in indices
            for field, value in tsmeta.items():
                if field in self.schema.keys() and self.schema[field]['index'] is not None:
                    self.assertTrue(pk in self.db.select({field:value})[0])

    def test_index_bulk(self):
        self.db.index_bulk()

    # def test_upsert_meta(self):
    #     n_test = 10
    #     for i in range(n_test):
    #         pk = 'ts-'+str(i)
    #         tsmeta = self.db._get_meta_dict(pk)
    #         tsinstance = tsmeta['ts']
    #         oldval = tsmeta['order']
    #         orderval = oldval + 1 if oldval != 5 else -5
    #         tsmeta['order'] = orderval
    #
    #         # change value of order and check that indices change
    #         self.db.upsert_meta(pk, tsmeta)
    #         newmeta = self.db._get_meta_dict(pk)
    #         self.assertEqual(newmeta['order'],orderval)
    #
    #         self.assertTrue(pk not in self.db.select({'order':oldval})[0])
    #         self.assertTrue(pk in self.db.select({'order':orderval})[0])
    #
    #         # replace the values
    #         replaceval = orderval - 1 if orderval != -5 else 5
    #         tsmeta['order'] = orderval
    #         self.db.upsert_meta(pk, tsmeta)
    #
    #     with self.assertRaises(TypeError):
    #         tsmeta['order'] = "wrong type"
    #         self.db.upsert_meta(pk, tsmeta)

    def test_delete(self):
        n_delete = 10
        # delete and check to make sure they're gone
        for i in range(n_delete):
            pk = 'ts-'+str(i)
            tsmeta = self.db._get_meta_dict(pk)
            tsinstance = tsmeta['ts']

            self.db.delete_ts(pk) # delete the timeseries
            with self.assertRaises(KeyError):
                self.db[pk] # check to make sure it's gone
            self.assertEqual(self.db.select({'pk':pk}), ([],[]))
            for field, value in tsmeta.items(): # make sure it's gone from indexes
                if field in self.schema.keys() and self.schema[field]['index'] is not None:
                    self.assertTrue(pk not in self.db.select({field:value})[0])

        # reinsert
        for i in range(n_delete):
            pk = 'ts-'+str(i)
            values = np.array(range(self.tsLength)) + i
            series = ts.TimeSeries(values, values)
            meta = {}
            n_order = len(self.schema['order']['values'])# 11
            meta['order'] = self.schema['order']['values'][i % n_order]
            n_blarg = 2
            meta['blarg'] = self.schema['blarg']['values'][i % n_blarg]
            meta['mean'] = float(series.mean())
            meta['std'] = float(series.std())
            meta['vp'] = False
            self.db.insert_ts(pk, series)
            self.db.upsert_meta(pk, meta)

        # check to make sure everything is working as before
        for i in range(n_delete):
            pk = 'ts-'+str(i)
            values = np.array(range(self.tsLength)) + i
            series = ts.TimeSeries(values, values)
            r_meta = self.db._get_meta_list(pk)
            n_order = len(self.schema['order']['values'])# 11
            self.assertTrue(r_meta[self.db.metaheap.fields.index('order')] == self.schema['order']['values'][i % n_order])
            n_blarg = 2
            self.assertTrue(r_meta[self.db.metaheap.fields.index('blarg')] == self.schema['blarg']['values'][i % n_blarg])
            self.assertTrue(r_meta[self.db.metaheap.fields.index('mean')] == series.mean())
            self.assertTrue(r_meta[self.db.metaheap.fields.index('std')] == series.std())

    # def test_vps(self):
    #     self.db.add_vp('vp-0', 'ts-88')
    #     self.db.add_vp('vp-1', 'ts-87')
    #     with self.assertRaises(IndexError):
    #         self.db.add_vp('vp-2', 'ts-1000')# doesn't exist in db
    #     self.assertTrue('vp-0' in self.db.vps)
    #     self.db.delete_vp('vp-0')
    #     self.assertTrue('vp-0' not in self.db.vps)
    #     with self.assertRaises(IndexError):
    #         self.db.delete_vp('vp-3')# doesn't exist in db
    #
    #     self.db.close()
    #     self.db = PersistentDB(pk_field='pk', db_name='testing', ts_length=self.tsLength, testing=True)
    #     self.assertTrue('vp-1' in self.db.vps)

if __name__ == '__main__':
    unittest.main()
