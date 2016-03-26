from pype.lexer import lexer
from pype.pipeline import Pipeline

example0_ppl='test/samples/example0.ppl'
example0_token='test/samples/example0.tokens'
example1_ppl='test/samples/example1.ppl'
example1_token='test/samples/example1.tokens'

def test_lexer():
    lexer.input(open(example1_ppl).read())
    output=open(example1_token)
    for token, line in zip(lexer, output):
        assertEqual(str(token), line.strip())

def test_example0(example0_ppl):
    t=Pipeline(example0_ppl)

def test_example1():
    t=Pipeline(example1_ppl)
