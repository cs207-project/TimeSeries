from pytest import raises
from pype.lexer import lexer
from pype.pipeline import Pipeline

example_error_ppl='test/samples/example_error.ppl'
example0_ppl='test/samples/example0.ppl'
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
