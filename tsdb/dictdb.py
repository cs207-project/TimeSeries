from collections import defaultdict
from operator import and_
from functools import reduce
import operator

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
        # schema = {
        #'pk': {'convert': identity, 'index': None},
        #'ts': {'convert': identity, 'index': None},
        #'order': {'convert': int, 'index': 1},
        #'blarg': {'convert': int, 'index': 1},
        #'useless': {'convert': identity, 'index': None},
        # }
        "implement upserting field values, as long as the fields are in the schema."
        # meta is a dictionary

        # used as this client.upsert_meta('one', {'order': 1, 'blarg': 1})

        # updating if not inserting and inserting otherwise their metadata

        if pk not in self.rows:
            self.rows[pk] = {'pk': pk}

        meta_keys = meta.keys()
        meta_values = meta.values()

        for field in meta_keys:#'order'

            if field in self.schema:# found 'order' in schema

                convert_function = self.schema[field]['convert'] # schema['order']['convert'] = int
                self.rows[pk][field] = convert_function(meta[field])# self.row['one']['order'] = int(1)
            else:
                print(field)
                raise ValueError("Meta's field not supported by schema")

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
        # bla = client.select({'order': 1, 'blarg': 2})
        #implement select, AND'ing over the filters in the md metadata dict
        #remember that each item in the dictionary looks like key==value
        pks = set()
        for field, value in meta.items():
            if field in self.schema:

                convert_function = self.schema[field]['convert']
                idx = self.indexes[field][convert_function(value)]
                # idx is a set
                # print(idx,pks)
                if not bool(pks):
                    pks = idx
                else:
                    #print(pks & (idx))
                    pks = pks & idx
            else:
                raise KeyError("Meta's field not supported by schema")
        if not bool(pks):
            return None
        return list(pks)

