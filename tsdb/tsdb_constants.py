####################################################
#
# This file records all the constant variables used
# in tsdb module
#
####################################################


OPMAP = {
    '<': 0,
    '>': 1,
    '==': 2,
    '!=': 3,
    '<=': 4,
    '>=': 5
}

FILES_DIR = 'persistent_files'

MAX_CARD = 8

INDEXES = {
    1: None, #Binary Tree
    2: None  #bitmask
}

TYPES = {
    'float': 'd',
    'bool': '?',
    'int': 'i',
}
TYPE_DEFAULT = {
    'float': 0.0,
    'bool': False,
    'int': 0
}

TS_FIELD_LENGTH = 4

BYTES_PER_NUM = 8

REFRESH_RATE = 50

TS_LENGTH = 100

NUMVPS = 5


schema_type = {
  'pk':    {'type': 'string', 'index': None},
  'ts':    {'type': None,     'index': None},
  'order': {'type': 'int',    'index': 2,    'values': [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]},
  'blarg': {'type': 'int',    'index': 2,    'values': [1, 2]},
  'mean':  {'type': 'float',  'index': 1},
  'std':   {'type': 'float',  'index': 1},
  'vp':    {'type': 'bool',   'index': 2,    'values': [0,1]},
  'd-vp1': {'type': 'float',  'index': 1}

}

identity = lambda x: x

schema_convert = {
  'pk': {'convert': identity, 'index': None},
  'ts': {'convert': identity, 'index': None},
  'order': {'convert': int, 'index': 1},
  'blarg': {'convert': int, 'index': 1},
  'useless': {'convert': identity, 'index': None},
  'mean': {'convert': float, 'index': 1},
  'std': {'convert': float, 'index': 1},
  'vp': {'convert': bool, 'index': 1}
}

