#!/usr/bin/env python3
from tsdb import TSDBServer, DictDB
import timeseries as ts

identity=lambda x:x
schema = {
  'pk': {'convert': identity, 'index': None},  #will be indexed anyways
  'ts': {'convert': identity, 'index': None},
  'order': {'convert': int, 'index': 1},
  'blarg': {'convert': int, 'index': 1},
  'useless': {'convert': identity, 'index': None},
  'mean': {'convert': identity, 'index': None},
  'std': {'convert': identity, 'index': None},
}

def main():
  db = DictDB(schema, 'pk')
  server = TSDBServer(db)
  server.run()

if __name__=='__main__':
  main()
