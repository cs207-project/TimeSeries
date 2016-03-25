import ply.lex

def test_lexer():
    lexer = ply.lex.lex()
    data = '''
    3 + 4 * 10
    + -20 *2
    abcdefg := 22         #test assign and comment
    >><>                  #test illegal sign

                          #test comment to see if this line is working or not
    22
        
    '''
    # Give the lexer some input
    lexer.input(data)
    # Tokenize
    while True:
        tok = lexer.token()

        if not tok: 
            break      # No more input
        print(tok,'\n')

