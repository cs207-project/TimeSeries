from dictdb import DictDB

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


testDb.insert_ts('1-2', np.arange(2))
testDb.insert_ts('1-3', np.arange(3))
testDb.insert_ts('1-4', np.arange(4))

testDb.upsert_meta('1-2', {'mean':1.5, 'len':len(np.arange(2))})
testDb.upsert_meta('1-3', {'mean':2, 'len':len(np.arange(3))})
testDb.upsert_meta('1-4', {'mean':2.5, 'len':len(np.arange(4))})

#print(ddb.select({'len':5}))  # Should be {'fakets1', 'fakets3'}
print(testDb.select({'len':4, 'mean':2.5}))  # Should be {'fakets1'}
#print(ddb.select({'len':5, 'mean':5}))  # Should be empty set
print(testDb.select({'mean':1}))