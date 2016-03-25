import ply.lex

reserved = { # pattern : token-name
  'input' : 'INPUT',
  'output' : 'OUTPUT',
  'import' : 'IMPORT',
}
# 'tokens' is a special word in ply's lexers.
tokens = [ 
  'LPAREN','RPAREN', # Individual parentheses
  'LBRACE','RBRACE', # Individual braces
  'OP_ADD','OP_SUB','OP_MUL','OP_DIV', # the four basic arithmetic symbols
  'STRING', # Anything enclosed by double quotes
  'ASSIGN', # The two characters :=
  'NUMBER', # An arbitrary number of digits
  'ID', # a sequence of letters, numbers, and underscores. Must not start with a number.
] + list(reserved.values())

# TODO You'll need a list of token specifications here.


# Delimeters
t_LPAREN              = r'\('
t_RPAREN              = r'\)'
t_LBRACE              = r'\{'
t_RBRACE              = r'\}'



# Operators
t_OP_ADD              = r'\+'
t_OP_SUB              = r'-'
t_OP_MUL              = r'\*'
t_OP_DIV              = r'/'



# Strings 
t_STRING              = r'\"([^\\\n]|(\\.))*?\"'



# Assign
t_ASSIGN              = r':='



# Numbers
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t



# TODO Ignore whitespace.
t_ignore  = ' '



# TODO Write one rule for IDs and reserved keywords. Section 4.3 has an example.
t_ID = r'[A-Za-z_][A-Za-z0-9_]*'



# TODO Ignore comments. Comments in PyPE are just like in Python. Section 4.5.
t_ignore_COMMENT = r'\#.*'


# Helper function in finding columns
def find_column(input,token):
    last_cr = input.rfind('\n',0,token.lexpos)
    if last_cr < 0:
      last_cr = 0
    column = (token.lexpos - last_cr) 
    return column



# TODO Write a rule for newlines that track line numbers. Section 4.6.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)



# TODO Write an error-handling routine. It should print both line and column numbers.
def t_error(t):
    print("Illegal character '%s'" % t.value[0], "Error Line", t.lexer.lineno, "Error Column", find_column(data,t))
    t.lexer.skip(1)


# This actually builds the lexer.
lexer = ply.lex.lex()


"""
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
"""
