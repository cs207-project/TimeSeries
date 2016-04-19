import timeseries as ts
from .tsdb_error import *

# Interface classes for TSDB network operations.
# These are a little clunky (extensibility is meh), but it does provide strong
# typing for TSDB ops and a straightforward mechanism for conversion to/from
# JSON objects.


class TSDBOp(dict):
    def __init__(self, op):
        self['op'] = op

    def to_json(self, obj=None):
        # This is both an interface function and its own helper function.
        # It recursively converts elements in a hierarchical data structure
        # into a JSON-encodable form. It does *not* handle class instances
        # unless they have a 'to_json' method.
        if obj is None:
            obj = self
        json_dict = {}
        if isinstance(obj, str) or not hasattr(obj, '__len__') or obj is None:
            return obj
        for k, v in obj.items():
            if isinstance(v, str) or not hasattr(v, '__len__') or v is None:
                json_dict[k] = v
            elif isinstance(v, TSDBStatus):
                json_dict[k] = v.name
            elif isinstance(v, list):
                json_dict[k] = [self.to_json(i) for i in v]
            elif isinstance(v, dict):
                json_dict[k] = self.to_json(v)
            elif hasattr(v, 'to_json'):
                json_dict[k] = v.to_json()
            else:
                raise TypeError('Cannot convert object to JSON: '+str(v))
        return json_dict

    @classmethod
    def from_json(cls, json_dict):
        if 'op' not in json_dict:
            raise TypeError('Not a TSDB Operation: '+str(json_dict))
        if json_dict['op'] not in typemap:
            raise TypeError('Invalid TSDB Operation: '+str(json_dict['op']))
        return typemap[json_dict['op']].from_json(json_dict)


class TSDBOp_InsertTS(TSDBOp):
    def __init__(self, pk, ts):
        super().__init__('insert_ts')
        self['pk'], self['ts'] = pk, ts

    @classmethod
    def from_json(cls, json_dict):
        return cls(json_dict['pk'], ts.TimeSeries(*(json_dict['ts'])))


class TSDBOp_Return(TSDBOp):

    def __init__(self, status, op, payload=None):
        super().__init__(op)
        self['status'], self['payload'] = status, payload

    @classmethod
    def from_json(cls, json_dict):  #should not be used
        return cls(json_dict['status'], json_dict['payload'])

class TSDBOp_UpsertMeta(TSDBOp):

    def __init__(self, pk, md):
        #print('-----------')
        super().__init__('upsert_meta')
        self['pk'], self['md'] = pk, md

    @classmethod
    def from_json(cls, json_dict):
        return cls(json_dict['pk'], json_dict['md'])


class TSDBOp_Select(TSDBOp):

    def __init__(self, md):
        super().__init__('select')
        self['md'] = md #we abuse the metadata dict to carry the payload for `select`

    @classmethod
    def from_json(cls, json_dict):
        return cls(json_dict['md'])



# This simplifies reconstructing TSDBOp instances from network data.
typemap = {
  'insert_ts': TSDBOp_InsertTS,
  'upsert_meta': TSDBOp_UpsertMeta,
  'select': TSDBOp_Select,
}
