from timeseries.lexer import lexer
from timeseries.parser import parser
from timeseries.semantic_analysis import CheckSingleAssignment, PrettyPrint
from timeseries.translate import SymbolTableVisitor

class Pipeline(object):
  def __init__(self, source):
    with open(source) as f:
      self.compile(f)

  def compile(self, file):
    input = file.read()
    # Lexing, parsing, AST construction
    ast = parser.parse(input, lexer=lexer)
    # Pretty print in ast class
    ast.pprint()
    # Pretty print using node visitor
    ast.walk( PrettyPrint() )
    # Semantic analysis
    ast.walk( CheckSingleAssignment() )
    # Translation
    syms = ast.walk( SymbolTableVisitor())
    # Pretty print symbol table
    syms.pprint()
    return syms

def test_example0():
    t=Pipeline('./samples/example0.ppl')

def test_example1():
    t=Pipeline('./samples/example1.ppl')
