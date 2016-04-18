class ASTVisitor():
  def visit(self, astnode):
    'A read-only function which looks at a single AST node.'
    pass
  def return_value(self):
    return None

class ASTModVisitor(ASTVisitor):
  '''A visitor class that can also construct a new, modified AST.
  Two methods are offered: the normal visit() method, which focuses on analyzing
  and/or modifying a single node; and the post_visit() method, which allows you
  to modify the child list of a node.
  The default implementation does nothing; it simply builds up itself, unmodified.'''
  def visit(self, astnode):
    # Note that this overrides the super's implementation, because we need a
    # non-None return value.
    return astnode
  def post_visit(self, visit_value, child_values):
    '''A function which constructs a return value out of its children.
    This can be used to modify an AST by returning a different or modified
    ASTNode than the original. The top-level return value will then be the
    new AST.'''
    return visit_value

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
    """
    Recursively prints a formatted string representation of the AST.

    Parameters
    ----------
    """
    if self is not None:
        print (indent+self.__class__.__name__)
        indent+='\t'
        for child in self.children:
            if isinstance(child, ASTID):
                print (indent+child.__class__.__name__)
            else:
                child.pprint(indent)

  def walk(self, visitor):
    """
    Traverses an AST, calling visitor.visit() on every node.
    This is a depth-first, pre-order traversal. Parents will be visited before
    any children, children will be visited in order, and (by extension) a node's
    children will all be visited before its siblings.
    The visitor may modify attributes, but may not add or delete nodes.

    Parameters
    ----------
    visitor : ASTVisitor
      visitor for a single AST node
    """
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
    """
    Initialize an ASTComponent node with name and expressions

    Parameters
    ----------
    name : ASTID
      ASTID node repreesnts the name of ASTComponent
    expressions : list
      list of AST Expression nodes
    """
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
    """
    Initialize an ASTAssignmentExpr node with binding and value

    Parameters
    ----------
    binding : ASTID
      ASTID node represents binding of ASTAssignmentExpr node
    value : ASTID or ASTLiteral
      ASTID node represents the binded value
    """
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
    """
    Initialize an ASTEvalExpr node with op and args

    Parameters
    ----------
    op : ASTID
      ASTID node represents the operation
    args : list of ASTID or ASTLiteral
      list of ASTID or ASTLiteral represents the args
    """
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
    """
    Initialize an ASTID node with name and type declaration

    Parameters
    ----------
    name : string
      name of ASTID node
    typedecl : str
      data type of ASTID node
    """
    super().__init__()
    self.name = name
    self.type = typedecl

class ASTLiteral(ASTNode):
  def __init__(self, value):
    """
    Initialize an ASTLiteral node with value

    Parameters
    ----------
    value : number or string
      value of ASTLiteral node
    """
    super().__init__()
    self.value = value
    self.type = 'Scalar'


