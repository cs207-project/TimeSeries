from dictdb import DictDB
from timeseries.TimeSeries import TimeSeries
import numpy as np

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
testDb = DictDB(schema)

testDb.insert_ts('one', TimeSeries([1, 2, 3], [1, 4, 9]))
testDb.insert_ts('two', TimeSeries([2, 3, 4], [4, 9, 16]))
testDb.insert_ts('three', TimeSeries([9, 3, 4], [4, 0, 16]))
testDb.insert_ts('four', TimeSeries([0, 0, 4], [1, 0, 4]))

testDb.upsert_meta('one', {'order': 1, 'blarg': 1})
testDb.upsert_meta('two', {'order': 2})
testDb.upsert_meta('three', {'order': 1, 'blarg': 2})
testDb.upsert_meta('four', {'order': 2, 'blarg': 2})

pks, payload = testDb.select({'order': {'>=': 1}}, [], {'limit': 2})
print(pks, payload)