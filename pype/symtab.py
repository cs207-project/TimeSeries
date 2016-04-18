import collections
import enum

SymbolType = enum.Enum('SymbolType', 'component var input output libraryfunction librarymethod')
Symbol = collections.namedtuple('Symbol','name type ref')

class SymbolTable(object):
  """
    A symbol table is a dictionary of scoped symbol tables.
    Each scoped symbol table is a dictionary of metadata for each variable.
  """
 
  def __init__(self):
    self.T = {} # {scope: {name:str => {type:SymbolType => ref:object} }}
    self.T['global'] = {}

  def __getitem__(self, component):
    return self.T[component]

  def scopes(self):
    return self.T.keys()

  def __repr__(self):
    return str(self.T)

  def pprint(self):
    print('---SYMBOL TABLE---')
    for (scope,table) in self.T.items():
      print(scope)
      for (name,symbol) in table.items():
        print(' ',name,'=>',symbol)

  def addsym(self, sym, scope='global'):
    if scope in self.scopes():
      self[scope][sym.name]=sym
    else:
      self.T[scope]={sym.name:sym}

  def lookupsym(self, sym, scope=None):
    if scope is not None:
      if sym in self.T[scope]:
        return self.T[scope][sym]
    if sym in self.T['global']:
      return self.T['global'][sym]
    return None
