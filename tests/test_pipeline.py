from pype.lexer import lexer
from pype.parser import parser
from pype.semantic_analysis import CheckSingleAssignment, PrettyPrint
from pype.translate import SymbolTableVisitor
from pype.Pipeline import Pipeline

def test_example0():
    t=Pipeline('./samples/example0.ppl')

def test_example1():
    t=Pipeline('./samples/example1.ppl')
