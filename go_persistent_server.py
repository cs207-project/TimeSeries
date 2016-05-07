from tsdb.tsdb_persistent import PersistentDB
from tsdb.tsdb_server import TSDBServer
import os
import timeseries as ts

dirPath = "files/testing"
if not os.path.isdir(dirPath):
    os.makedirs(dirPath)
    _createdDirs = True
else:
    _createdDirs = False

schema = {
  'pk':    {'type': 'string', 'index': None},
  'ts':    {'type': None,     'index': None},
  'order': {'type': 'int',    'index': 2,    'values': [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]},
  'blarg': {'type': 'int',    'index': 2,    'values': [1, 2]},
  'mean':  {'type': 'float',  'index': 1},
  'std':   {'type': 'float',  'index': 1},
  'vp':    {'type': 'bool',   'index': 2,    'values': [0,1]},
  'd-vp1': {'type': 'float',  'index': 1},
  'd-vp2': {'type': 'float',  'index': 1},
  'd-vp3': {'type': 'float',  'index': 1},
  'd-vp4': {'type': 'float',  'index': 1},
  'd-vp5': {'type': 'float',  'index': 1}
}

TS_LENGTH = 100

def main():
    db = PersistentDB(schema, pk_field='pk', db_name='testing', ts_length=TS_LENGTH, testing=True)
    server = TSDBServer(db)
    server.run()
    db.delete_database()

if __name__=='__main__':
    main()