from collections import defaultdict
from operator import and_
from functools import reduce
import operator
import numbers
from .tsdb_error import TSDBStatus

# this dictionary will help you in writing a generic select operation
OPMAP = {
    '<': operator.lt,
    '>': operator.gt,
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
    """
    Time series Database implementation in dictionary

    Attributes
    ----------
    indexes : dict
        The keys are the indexed fields. The values are the index for each field.
    rows : dict
        contains all the rows. This is a dictionary with keys the primary keys
    schema : dict
        the schema that the dictionary follows
    pkfield : str
        selects the field to be considered as the primary key. Defaults to `pk`.

    """

    def __init__(self, schema,pk_field = 'pk'):

        """
        initializes database with indexed and schema
        Parameters
        ----------
        schema : dict
            the schema that the database follows

        pkfield : str
            primary key field. Defaults to `pk`.

        """
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

    def __getitem__(self,key):
        """Return the the values at a given row identified by pk"""
        if key in self.rows:
            return self.rows[key]
        else:
            raise ValueError("primary_key not in the database: "+ str(key))

    def insert_ts(self, pk, ts):
        "given a pk and a timeseries, insert them"
        if pk not in self.rows:
            self.rows[pk] = {'pk': pk}
        else:
            raise ValueError('Duplicate primary key found during insert')

        self.rows[pk]['ts'] = ts
        self.update_indices(pk)

    def delete_ts(self, pk):
        """
        given a pk, delete corresponding TimeSeries from the DB.

        Parameters
        ----------
        pk : int
            primary_key, a unique identifier for the TimeSeries
        """

        # first, check if the pk exist in DB
        if pk not in self.rows:
            raise ValueError(TSDBStatus.INVALID_KEY, 'Tried to delete {}, but that primary key does not exist'.format(pk))

        # save the row for pk temporarily to remove meta data too
        tmp_row = self.rows[pk]
        # delete pk from rows dictionary
        del self.rows[pk]
        self.remove_from_indices(pk,tmp_row)

    def upsert_meta(self, pk, meta):
        """
        Upserting metadata into the timeseries in the database designated by the promary key

        Parameters
        ----------
        primary_key: int
            a unique identifier for the timeseries

        metadata_dict: dict
            the metadata to upserted into the timeseries
        """

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
        """
        Update indices based on change of a row given its primary key

        Parameters
        ----------
        primary_key: int
            a unique identifier (primary key) for the row to be updated
        """
        if pk not in self.rows:
            raise KeyError('pk does not exist in database')

        row = self.rows[pk]
        for field in row:
            v = row[field]
            if self.schema[field]['index'] is not None:
                idx = self.indexes[field]
                idx[v].add(pk)

    def select(self, meta, fields_to_ret = None, additional = None):
        """
        Selecting timeseries elements in the database that match the criteria
        set in metadata_dict and return corresponding fields with additional
        features.

        Parameters
        ----------
        metadata_dict: dict
            the selection criteria (filters)

        fields: dict
            If not `None`, only these fields of the timeseries are returned.
            Otherwise, the timeseries are returned.

        additional: dict
            additional computation to perform on the query matches before they're
            returned. Currently provide "sort_by" and "limit" functionality

        """
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
            else:
                raise KeyError("Meta's field not supported by schema")

        if additional is None:
            return self._rows_to_return(pks, fields_to_ret)
        else:
            pks_list = list(pks)
            if 'sort_by' in additional:

                sorting_key = additional['sort_by']
                if sorting_key[0] == '+':
                    # + <- True, - <- False
                    sorting_order_reversed = False
                elif sorting_key[0] == '-':
                    sorting_order_reversed = True
                else:
                    raise KeyError("Sort order must be '+' or '-'")

                sorting_scheme = sorting_key[1:]

                assert sorting_scheme in self.schema

                pks_list = sorted(pks_list,key = lambda x: self.rows[x][sorting_scheme], reverse = sorting_order_reversed)
            if 'limit' in additional:
                if additional['limit'] < 0:
                    raise ValueError('Limit must be greater than 0')
                pks_list = pks_list[:additional['limit']]

            if len(set(additional.keys()) - set(['sort_by', 'limit'])) > 0:
                raise KeyError("Undefined additional operation")

            return self._rows_to_return(set(pks_list), fields_to_ret)


    # ======================
    # Helper Functions
    # ======================
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

    def remove_from_indices(self, pk, row):
        "Remove pk from indices after deletion"
        for field in row:
            v = row[field]
            if self.schema[field]['index'] is not None:
                idx = self.indexes[field]# idx is a defaultdict(set)
                idx[v].remove(pk)#DNY: 'v' must be hashable
