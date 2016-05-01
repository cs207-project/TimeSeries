from pytest import raises
from pype.pipeline import *
from pype.pipeline import Pipeline
from timeseries.TimeSeries import TimeSeries
import unittest

input1 = """(import timeseries)
{ standardize
  (input (TimeSeries t))
  (:= mu (mean t))
  (:= sig (std t))
  (:= new_t (/ (- t mu) sig))
  (output new_t)
}"""


example_error_ppl='./samples/example_error.ppl'
example0_ppl='samples/example0.ppl'
example0_token='test/samples/example0.tokens'
example1_ppl='test/samples/example1.ppl'
example1_token='test/samples/example1.tokens'

def test_lexer():
    lexer.input(open(example1_ppl).read())
    output=open(example1_token)
    for token, line in zip(lexer, output):
        assert str(token) == line.strip()
    lexer.input(open(example_error_ppl).read())
    for token in lexer:
        print (token)

def test_pype4():
    time = []
    values = []

    for x in range(100):
        time.append(x)
        values.append(x-50)
    a = TimeSeries(time, values)


    ast = parser.parse(input1, lexer=lexer)

    # Semantic analysis
    ast.walk( CheckSingleAssignment() )
    ast.walk( CheckSingleIOExpression() )
    syms = ast.walk( SymbolTableVisitor() )
    ast.walk( CheckUndefinedVariables(syms) )


    # Translation
    ir = ast.mod_walk( LoweringVisitor(syms) )

    ir.flowgraph_pass( AssignmentEllision() )
    ir.flowgraph_pass( DeadCodeElimination() )
    ir.topological_flowgraph_pass( InlineComponents() )

    # PCode Generation
    pcodegen = PCodeGenerator()
    ir.flowgraph_pass( pcodegen )
    pcodes = pcodegen.pcodes
    standardized_TS = pcodes['standardize'].run(a)

    assert(round(standardized_TS.mean(), 7) == 0)
    assert(round(standardized_TS.std()-1, 7) == 0)

def pprint(p):
    for g in p.ir:
        print(p.ir[g].dotfile())
        print(p.ir[g].topological_sort())

def test_compile():
    p = Pipeline(example0_ppl)
    # p.compile(example0_ppl)
    pprint(p)

test_compile()