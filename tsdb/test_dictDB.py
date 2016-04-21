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
class TimeSeries():

    def __init__(self, times, values):

        if (iter(times) and iter(values)):
            # reorder according to Time step
            idx = np.argsort(times)
            times = np.array(times)[idx]
            values = np.array(values)[idx]

            self._TimeSeries=np.vstack((times,values))
            self._vindex = 0
            self._values = self._TimeSeries[1]
            self._times = self._TimeSeries[0]

testDb.insert_ts('one', TimeSeries([1, 2, 3], [1, 4, 9]))
testDb.insert_ts('two', TimeSeries([2, 3, 4], [4, 9, 16]))
testDb.insert_ts('three', TimeSeries([9, 3, 4], [4, 0, 16]))
testDb.insert_ts('four', TimeSeries([0, 0, 4], [1, 0, 4]))

testDb.upsert_meta('one', {'order': 1, 'blarg': 1})
testDb.upsert_meta('two', {'order': 2})
testDb.upsert_meta('three', {'order': 1, 'blarg': 2})
testDb.upsert_meta('four', {'order': 2, 'blarg': 2})
#print(testDb.select())
print(testDb.select({'order': 1}))
print(testDb.select({'blarg': 1}))
