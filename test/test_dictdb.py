from tsdb.dictdb import DictDB
from timeseries.TimeSeries import TimeSeries
import numpy as np
import unittest

class DictDBTests(unittest.TestCase):
    def setUp(self):
        identity = lambda x: x

        schema = {
          'pk': {'convert': identity, 'index': None},
          'ts': {'convert': identity, 'index': None},
          'order': {'convert': int, 'index': 1},
          'blarg': {'convert': int, 'index': 1},
          'useless': {'convert': identity, 'index': None},
          'mean':{'convert': float, 'index':3},
          'len': {'convert': int, 'index':4}
        }

        self.testDb = DictDB(schema)

        self.testDb.insert_ts('one', TimeSeries([1, 2, 3], [1, 4, 9]))
        self.testDb.insert_ts('two', TimeSeries([2, 3, 4], [4, 9, 16]))
        self.testDb.insert_ts('three', TimeSeries([9, 3, 4], [4, 0, 16]))
        self.testDb.insert_ts('four', TimeSeries([0, 0, 4], [1, 0, 4]))
        self.testDb.upsert_meta('one', {'order': 1, 'blarg': 1})
        self.testDb.upsert_meta('two', {'order': 2})
        self.testDb.upsert_meta('three', {'order': 1, 'blarg': 2})
        self.testDb.upsert_meta('four', {'order': 2, 'blarg': 2})

    def test_insert_ts(self):
        print('Test insert_ts')
        with self.assertRaises(ValueError):
            self.testDb.insert_ts('one', TimeSeries([1, 2, 3], [1, 4, 9]))

    def test_upsert_meta(self):
        print('Test upsert_meta')
        with self.assertRaises(ValueError):
            self.testDb.upsert_meta('four', {'order': 2, 'blarg': 2, 'non-existing-key': 1})

    def test_update_indices(self):
        print('Test update_indices')
        with self.assertRaises(KeyError):
            self.testDb.update_indices('None-existing-key')

    def test_select_1(self):
        print('Test select 1')
        with self.assertRaises(KeyError):
            self.testDb.select({'non-existing-key': 1})

    def test_select_2(self):
        print('Test select 2')
        pks, payload = self.testDb.select({})
        self.assertEqual(set(pks), set(['one', 'two', 'three', 'four']))

    def test_select_3(self):
        print('Test select 3')
        pks, payload = self.testDb.select({'order': 1})
        self.assertEqual(set(pks), set(['one', 'three']))

    def test_select_4(self):
        print('Test select 4')
        pks, payload = self.testDb.select({'order': {'>': 1}, 'blarg': 2}, ['pk','blarg','order'], None)
        self.assertEqual(set(pks), set(['four']))

    def test_select_5(self):
        print('Test select 5')
        pks, payload = self.testDb.select({'order': {'>': 1}}, [], {'sort_by':'-order'})
        self.assertEqual(set(pks), set(['four', 'two']))

    def test_select_6(self):
        print('Test select 6')
        pks, payload = self.testDb.select({'order': {'>': 1}}, [], {'sort_by':'+order'})
        self.assertEqual(set(pks), set(['four', 'two']))

    def test_select_7(self):
        print('Test select 7')
        pks, payload = self.testDb.select({'order': {'>=': 1}}, [], {'sort_by':'+order', 'limit': 2})
        self.assertEqual(set(pks), set(['one', 'three']))

    def test_select_8(self):
        print('Test select 8')
        with self.assertRaises(KeyError):
            self.testDb.select({'order': {'>=': 1}}, [], {'sort_by':'=order', 'limit': 2})

    def test_select_9(self):
        print('Test select 9')
        with self.assertRaises(KeyError):
            self.testDb.select({'order': {'>=': 1}}, [], {'undefined': 0,'sort_by':'=order', 'limit': 2})

    def test_select_10(self):
        print('Test select 10')
        with self.assertRaises(ValueError):
            self.testDb.select({'order': {'>=': 1}}, [], {'undefined': 0,'sort_by':'+order', 'limit': -1})

if __name__ == '__main__':
    unittest.main()