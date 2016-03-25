import importlib
import inspect
import functools

from .symtab import *

ATTRIB_COMPONENT = '_pype_component'

def component(func):
  'Marks a functions as compatible for exposing as a component in PyPE.'
  # TODO
  func._attributes={'_pype_component':True}
  return func

def is_component(func):
  'Checks whether the @component decorator was applied to a function.'
  # TODO
  if '_attributes' in dir(func):
    if isinstance(func._attributes, dict) and '_pype_component' in func._attributes:
      return func._attributes['_pype_component']
    else:
      return False
  else:
    return False

class LibraryImporter(object):
  def __init__(self, modname=None):
    self.mod = None
    if modname is not None:
      self.import_module(modname)

  def import_module(self, modname):
    self.mod = importlib.import_module(modname)

  def add_symbols(self, symtab):
    assert self.mod is not None, 'No module specified or loaded'
    for (name,obj) in inspect.getmembers(self.mod):
      if inspect.isroutine(obj) and is_component(obj):
        # TODO: add a symbol to symtab
        #       it should be named name
        #       its type should be a libraryfunction SymbolType
        #       its ref should be the object itself (obj)
        symtab.addsym( Symbol(name, SymbolType.libraryfunction, obj) )
      elif inspect.isclass(obj):
        for (methodname,method) in inspect.getmembers(obj):
           # TODO:
           #   check if method was decorated like before
           #   add a symbol like before, but with type librarymethod
           #   (the ref should be the method, not obj)
          if inspect.isroutine(method) and is_component(method):
            symtab.addsym( Symbol(methodname, SymbolType.librarymethod, method) )
    return symtab
