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

INDEXES = {
    1: None, #Binary Tree
    2: None #bitmask
}

FILES_DIR = 'persistent_files'

MAX_CARD = 8

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


schema = {
  'pk':    {'type': 'string', 'index': None},
  'ts':    {'type': None,     'index': None},
  'order': {'type': 'int',    'index': 2,    'values': [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]},
  'blarg': {'type': 'int',    'index': 2,    'values': [1, 2]},
  'mean':  {'type': 'float',  'index': 1},
  'std':   {'type': 'float',  'index': 1},
  'vp':    {'type': 'bool',   'index': 2,    'values': [0,1]},
  'd-vp1': {'type': 'float',  'index': 1}
}

