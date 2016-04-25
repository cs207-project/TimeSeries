from collections import defaultdict
from operator import and_
from functools import reduce
import operator
import numbers

# this dictionary will help you in writing a generic select operation
OPMAP = {
    '<': operator.lt,
    '>': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    '<=': operator.le,
    '>=': operator.ge
}

def metafiltered(d, schema, fieldswanted):
    d2 = {}
    if len(fieldswanted) == 0:
        keys = [k for k in d.keys() if k != 'ts']
    else:
        keys = [k for k in d.keys() if k in fieldswanted]
    for k in keys:
        if k in schema:
            d2[k] = schema[k]['convert'](d[k])
    return d2

class DictDB:
    "Database implementation in a dict"
    def __init__(self, schema,pk_field = 'pk'):
        "initializes database with indexed and schema"
        self.indexes = {}
        self.rows = {}
        self.schema = schema
        self.pkfield = pk_field
        for s in schema:
            indexinfo = schema[s]['index']
            # convert = schema[s]['convert']
            # later use binary search trees for highcard/numeric
            # bitmaps for lowcard/str_or_factor
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

    def _rows_to_return(self, pks, fields_to_ret):
        pks_ret = []
        fields_ret = []
        if fields_to_ret is None:
            print ('S> D> NO FIELDS')
            pks_ret, fields_ret = list(pks), [{}]*len(pks)
        elif fields_to_ret == []:
            print ('S> D> ALL FIELDS')
            # Need to loop through pks first
            for pk in pks:
                if pk in self.rows.keys():
                    pks_ret.append(pk)
                    fields_dict = self.rows[pk]
                    field_dict_ret = {}
                    for f_pk in fields_dict.keys():
                        if f_pk != 'ts':
                            field_dict_ret[f_pk] = fields_dict[f_pk]
                    fields_ret.append(field_dict_ret)
        elif isinstance(fields_to_ret,list):
            print ('S> D> FIELDS {}'.format(fields_to_ret))
            for pk in pks:
                if pk in self.rows.keys():
                    pks_ret.append(pk)
                    fields_dict = self.rows[pk]
                    field_dict_ret = {}
                    for f_pk in fields_dict.keys():
                        if f_pk in fields_to_ret:
                            field_dict_ret[f_pk] = fields_dict[f_pk]
                    fields_ret.append(field_dict_ret)
        return pks_ret, fields_ret

    def select(self, meta, fields_to_ret, additional):
        # bla = client.select({'order': 1, 'blarg': 2})
        #implement select, AND'ing over the filters in the md metadata dict
        #remember that each item in the dictionary looks like key==value
        pks = set(self.rows.keys())
        #print('selffffffffffff indexes',self.indexes)
            #self.indexes

        for field, condition in meta.items():
            filter_pks = set()
            if field in self.schema:
                convert_function = self.schema[field]['convert']
                # Store filtered rows

                # Check if query is exact or range
                if (isinstance(condition, numbers.Real)):
                    for p in pks:
                        if field in self.rows[p] and self.rows[p][field] == convert_function(condition):
                            filter_pks.add(p)
                    pks = pks & filter_pks
                elif (isinstance(condition, dict)):
                    op, val = list(condition.items())[0]
                    for p in pks:
                        if field in self.rows[p] and OPMAP[op](self.rows[p][field], convert_function(val)):
                            filter_pks.add(p)
                    pks = pks & filter_pks
            # else:
            #
            #     raise KeyError("Meta's field not supported by schema")
        if additional is None:
            return self._rows_to_return(pks, fields_to_ret)
        else:
            #print(additional, '=========*******========addtional')
            # Limiting and sorting stuff goes here
            # client.select({'order': {'>=': 4}}, fields=['order', 'blarg', 'mean'], additional={'sort_by': '-order'})

            pks_list = list(pks)
            if 'sort_by' in additional:

                sorting_key = additional['sort_by']
                #print(pks_list, '****', sorting_key, '[[[[[[[[[[[[[[]]]]]]]]]]]]]')
                if sorting_key[0] == '+':
                    # + <- True, - <- False
                    sorting_order_reversed = False
                elif sorting_key[0] == '-':
                    sorting_order_reversed = True

                sorting_scheme = sorting_key[1:]

                assert sorting_scheme in self.schema

                pks_list = sorted(pks_list,key = lambda x: self.rows[x][sorting_scheme], reverse = sorting_order_reversed)
                print(pks_list,'[[[[[[[[[[[[[[]]]]]]]]]]]]]')
            if 'limit' in additional:
                pks_list = pks_list[:additional['limit']]
            #print(pks_list,'[[[[[[[[[[[[[[]]]]]]]]]]]]]')
            return self._rows_to_return(set(pks_list), fields_to_ret)


