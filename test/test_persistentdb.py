import unittest
from tsdb.persistentdb import PersistentDB
import os
import timeseries as ts
import numpy as np
from tsdb.tsdb_constants import schema

class PersistentDBTests(unittest.TestCase):
    def setUp(self):
        self.dirPath = "persistent_files/testing"
        if not os.path.isdir(self.dirPath):
            os.makedirs(self.dirPath)
            self._createdDirs = True
        else:
            self._createdDirs = False

        self.schema = schema
        self.ts_length = 100

        self.db = PersistentDB(schema, pk_field='pk', db_name='testing', ts_length=self.ts_length)

        for i in range(100):
            pk = 'ts-'+str(i)
            values = np.array(range(self.ts_length)) + i
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


    def test_select1(self):
        self.db.select({'pk':'ts-0'})

    def test_select2(self):
        self.db.select({'pk':'ts-35'})

    def test_select3(self):
        self.db.select({'order':2})

    def test_select4(self):
        self.db.select({'order':{'>=':2}},['blarg'],{'sort_by':'+blarg'})

    def test_select5(self):
        self.db.select({'order':{'>=':2}},['blarg'],{'sort_by':'-order'})

    def test_select6(self):
        val = self.db.select({'order':{'>=':2}},['pk','blarg'],{'sort_by':'-order', 'limit':10})
        self.assertTrue(len(val[0]) <= 10)

    def test_select7(self):
        with self.assertRaises(ValueError):
            self.db.select({'order':{'>=':2}},['blarg'],{'sort_by':'=blarg'})

    def test_select8(self):
        with self.assertRaises(ValueError):
            self.db.select({'order':{'>=':2}},['blarg'],{'sort_by':'-blargh'})

    def test_select9(self):
        self.db.select({'order':{'>=':2}},None,{'sort_by':'-blarg'})

    def test_select10(self):
        with self.assertRaises(TypeError):
            self.db.select({'order':{'>=':2}},('pk','blarg'),{'sort_by':'-order', 'limit':10})

    def test_meta_save_ts(self):
        self.db.close()
        self.db = PersistentDB(pk_field='pk', db_name='testing', ts_length=self.ts_length)
        self.assertEqual(len(self.db),100)

    def test_schema_change_good(self):
        self.db.close()
        self.db = PersistentDB(self.schema, pk_field='pk', db_name='testing', ts_length=self.ts_length)

    def test_schema_change_bad(self):
        badschema = dict(self.schema)
        badschema['blarg'] = {'type': 'int', 'index': 2, 'values': [1, 2, 3]}
        self.db.close()
        with self.assertRaises(ValueError):
            self.db = PersistentDB(badschema, pk_field='pk', db_name='testing', ts_length=self.ts_length)

    def test_insert_exception(self):
        pk = 'bad'
        existing = 'ts-0'
        with self.assertRaises(ValueError):
            bad_series = np.array(range(self.ts_length+3))
            self.db.insert_ts(pk, bad_series)
        with self.assertRaises(ValueError):
            values = np.array(range(self.ts_length+5))
            bad_series = ts.TimeSeries(values, values)
            self.db.insert_ts(pk, bad_series)
        with self.assertRaises(ValueError):
            values = np.array(range(self.ts_length))
            series = ts.TimeSeries(values,values)
            self.db.insert_ts('ts-0', series)

    def test_get_meta(self):
        for i in range(100):
            pk = 'ts-'+str(i)
            values = np.array(range(self.ts_length)) + i
            series = ts.TimeSeries(values, values)
            r_meta = self.db._get_meta_list(pk)
            n_order = len(self.schema['order']['values'])
            self.assertEqual(r_meta[self.db.metaheap.fields.index('order')], self.schema['order']['values'][i % n_order])
            n_blarg = 2
            self.assertEqual(r_meta[self.db.metaheap.fields.index('blarg')],self.schema['blarg']['values'][i % n_blarg])
            self.assertEqual(r_meta[self.db.metaheap.fields.index('mean')],series.mean())
            self.assertEqual(r_meta[self.db.metaheap.fields.index('std')],series.std())

    def test_read_ts(self):
        for i in range(100):
            pk = 'ts-'+str(i)
            values = np.array(range(self.ts_length)) + i
            series = ts.TimeSeries(values, values)
            r_ts = self.db._return_ts(pk)
            self.assertEqual(series,r_ts)

    def test_indices(self):
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

    def test_delete_ts(self):
        n_delete = 10
        # delete and check to make sure they're gone
        for i in range(n_delete):
            pk = 'ts-'+str(i)
            tsmeta = self.db._get_meta_dict(pk)

            self.db.delete_ts(pk) # delete the timeseries

            #Check 1: __get__() get by pk fail
            with self.assertRaises(KeyError):
                self.db[pk] # check to make sure it's gone

            #Check 2: db_select return empty sets
            self.assertEqual(self.db.select({'pk':pk}), ([],[]))

            #Check 3: does not exist in index
            for field, value in tsmeta.items(): # make sure it's gone from indexes
                if field in self.schema.keys() and self.schema[field]['index'] is not None:
                    self.assertTrue(pk not in self.db.select({field:value})[0])

        #Check 4: check the db after deletion is clean and can hold the same pk and timeseries again
        # insert the deleted ts and check to make sure everything is working as before
        for i in range(n_delete):
            pk = 'ts-'+str(i)
            values = np.array(range(self.ts_length)) + i
            series = ts.TimeSeries(values, values)
            meta = {}
            meta['mean'] = float(series.mean())
            meta['std'] = float(series.std())
            meta['vp'] = False
            meta['blarg'] = self.schema['blarg']['values'][i % 2] #blarg only has two value
            n_order = len(self.schema['order']['values'])# 11
            meta['order'] = self.schema['order']['values'][i % n_order]
            self.db.insert_ts(pk, series)
            self.db.upsert_meta(pk, meta)

        for i in range(n_delete):
            pk = 'ts-'+str(i)
            values = np.array(range(self.ts_length)) + i
            series = ts.TimeSeries(values, values)
            r_meta = self.db._get_meta_list(pk)
            n_order = len(self.schema['order']['values'])# 11
            self.assertTrue(r_meta[self.db.metaheap.fields.index('order')] == self.schema['order']['values'][i % n_order])
            n_blarg = 2
            self.assertTrue(r_meta[self.db.metaheap.fields.index('blarg')] == self.schema['blarg']['values'][i % n_blarg])
            self.assertTrue(r_meta[self.db.metaheap.fields.index('mean')] == series.mean())
            self.assertTrue(r_meta[self.db.metaheap.fields.index('std')] == series.std())

if __name__ == '__main__':
    unittest.main()
