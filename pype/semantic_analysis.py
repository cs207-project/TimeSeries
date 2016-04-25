from .ast import *
from .error import *

class PrettyPrint(ASTVisitor):
  def __init__(self):
    pass
  def visit(self, node):
    print (node.__class__.__name__)

class CheckSingleAssignment(ASTVisitor):
  def __init__(self):
    self.assignment_table=[]
  
  def visit(self, node):
    if isinstance(node, ASTProgram):
      for child in node.children:
        self.visit(child)
    elif isinstance(node, ASTComponent):
      self.assignment_table=[]
    elif isinstance(node, ASTAssignmentExpr):
      name=node.binding.name
      if name in self.assignment_table:
        raise Exception("Assignment expressions bind to the same name: "+name)
      else:
        self.assignment_table.append(name)
    else:      
      pass

class CheckSingleIOExpression(ASTVisitor):
  def __init__(self):
    self.component = None
    self.component_has_input = False
    self.component_has_output = False

  def visit(self, node):
    if isinstance(node, ASTComponent):
      self.component = node.name.name
      self.component_has_input = False
      self.component_has_output = False
    elif isinstance(node, ASTInputExpr):
      if self.component_has_input:
        raise PypeSyntaxError('Component '+str(self.component)+' has multiple input expressions')
      self.component_has_input = True
    elif isinstance(node, ASTOutputExpr):
      if self.component_has_output:
        raise PypeSyntaxError('Component '+str(self.component)+' has multiple output expressions')
      self.component_has_output = True

class CheckUndefinedVariables(ASTVisitor):
  def __init__(self, symtab):
    self.symtab = symtab
    self.scope=None
    
  def visit(self, node):
    if isinstance(node, ASTComponent):
      self.scope = node.name.name
    elif isinstance(node, ASTID):
      if self.symtab.lookupsym(node.name, scope=self.scope) is None:
        raise PypeSyntaxError('Undefined variable: '+str(node.name))
