from .ast import *
from .symtab import *
from .lib_import import LibraryImporter

class SymbolTableVisitor(ASTVisitor):
  def __init__(self):
    self.symbol_table = SymbolTable()
    self.scope='global'

  def return_value(self):
    return self.symbol_table

  def visit(self, node):
    if isinstance(node, ASTImport):
      # Import statements make library functions available to PyPE
      imp = LibraryImporter(node.module)
      imp.add_symbols(self.symbol_table)

    # TODO
    # Add symbols for the following types of names:
    #   inputs: anything in an input expression
    #     the SymbolType should be input, and the ref can be None
    #     the scope should be the enclosing component
    #   assigned names: the bound name in an assignment expression
    #     the SymbolType should be var, and the ref can be None
    #     the scope should be the enclosing component
    #   components: the name of each component
    #     the SymbolType should be component, and the ref can be None
    #     the scope sould be *global*
    if isinstance(node, ASTProgram):
      for child in node.children:
        self.visit(child)

    if isinstance(node, ASTInputExpr):
      self.symbol_table.addsym(Symbol(node.children[0].name, SymbolType.input, None),scope=self.scope)
    
    if isinstance(node, ASTAssignmentExpr):
      self.symbol_table.addsym(Symbol(node.binding, SymbolType.var,None),scope=self.scope)
        
    if isinstance(node, ASTComponent):
      self.scope=node.name.name
      self.symbol_table.addsym(Symbol(self.scope, SymbolType.component, None))
   
    # Note, you'll need to track scopes again for some of these.
    # You may need to add class state to handle this.
