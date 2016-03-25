class ASTVisitor():
  def visit(self, astnode):
    'A read-only function which looks at a single AST node.'
    pass
  def return_value(self):
    return None

class ASTNode(object):
  def __init__(self):
    self.parent = None
    self._children = []

  @property
  def children(self):
    return self._children
  @children.setter
  def children(self, children):
    self._children = children
    for child in children:
      child.parent = self

  def pprint(self,indent=''):
    '''Recursively prints a formatted string representation of the AST.'''
    if self is not None:
        print (indent+self.__class__.__name__)
        indent+='\t'
        for child in self.children:
            if isinstance(child, ASTID):
                print (indent+child.__class__.__name__)
            else:
                child.pprint(indent)

  def walk(self, visitor):
    '''Traverses an AST, calling visitor.visit() on every node.

    This is a depth-first, pre-order traversal. Parents will be visited before
    any children, children will be visited in order, and (by extension) a node's
    children will all be visited before its siblings.
    The visitor may modify attributes, but may not add or delete nodes.'''
    if self is not None:
        visitor.visit(self)
        for child in self.children:
            child.walk(visitor)
    return visitor.return_value()

class ASTProgram(ASTNode):
  def __init__(self, statements):
    super().__init__()
    self.children = statements

class ASTImport(ASTNode):
  def __init__(self, mod):
    super().__init__()
    self.mod = mod
  @property
  def module(self):
    return self.mod

class ASTComponent(ASTNode): 
  def __init__(self, name, expressions):
    super().__init__()
    expressions.insert(0,ASTID(name))
    self.children=expressions

  @property
  def name(self): 
    return self.children[0]
  @property
  def expressions(self): 
    return self.children[1:]

class ASTInputExpr(ASTNode):
  def __init__(self, declarations):
    super().__init__()
    self.children=declarations

class ASTOutputExpr(ASTNode): 
  def __init__(self, declarations):
    super().__init__()
    self.children=declarations

class ASTAssignmentExpr(ASTNode): 
  def __init__(self, binding, value):
    super().__init__()
    self.children=[ASTID(binding),value]
  @property
  def binding(self):
      return self.children[0]
  @property
  def value(self):
      return self.children[1:]

class ASTEvalExpr(ASTNode): 
  def __init__(self, op, args):
    super().__init__()
    if args is not None:
        args.insert(0,ASTID(op))
        self.children=args
    else:
        self.children=[ASTID(op)]

  @property
  def op(self):
    return self.children[0]
  @property
  def args(self):
    return self.children[1:]

# These are already complete.
class ASTID(ASTNode):
  def __init__(self, name, typedecl=None):
    super().__init__()
    self.name = name
    self.type = typedecl

class ASTLiteral(ASTNode):
  def __init__(self, value):
    super().__init__()
    self.value = value
    self.type = 'Scalar'


