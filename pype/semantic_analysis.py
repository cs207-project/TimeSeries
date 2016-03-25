from .ast import *

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
