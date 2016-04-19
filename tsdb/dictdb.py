from collections import defaultdict
from operator import and_
from functools import reduce


class DictDB:
    "Database implementation in a dict"
    def __init__(self, schema):
        "initializes database with indexed and schema"
        self.indexes = {}
        self.rows = {}
        self.schema = schema
        self.pkfield = 'pk'
        for s in schema:
            indexinfo = schema[s]['index']
            if indexinfo is not None:
                self.indexes[s] = defaultdict(set)

    def insert_ts(self, pk, ts):
        "given a pk and a timeseries, insert them"
        if pk not in self.rows:
            self.rows[pk] = {'pk': pk}
        else:
            raise ValueError('Duplicate primary key found during insert')
        self.rows[pk]['ts'] = ts
        self.update_indices(pk)

    def upsert_meta(self, pk, meta):
        "implement upserting field values, as long as the fields are in the schema."
        # your code here
        self.update_indices(pk)

    def index_bulk(self, pks=[]):
        if len(pks) == 0:
            pks = self.rows
        for pkid in self.pks:
            self.update_indices(pkid)

    def update_indices(self, pk):
        row = self.rows[pk]
        for field in row:
            v = row[field]
            if self.schema[field]['index'] is not None:
                idx = self.indexes[field]
                idx[v].add(pk)

    def select(self, meta):
        #implement select, AND'ing over the filters in the md metadata dict
        #remember that each item in the dictionary looks like key==value
