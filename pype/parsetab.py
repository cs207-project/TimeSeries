
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = 'BA90F0C8CB04659A4089667E76C36B34'
    
_lr_action_items = {'OP_DIV':([13,],[19,]),'IMPORT':([5,],[9,]),'OP_SUB':([13,],[23,]),'RPAREN':([11,12,16,17,21,24,25,29,30,31,32,33,34,35,38,39,40,41,42,43,44,45,46,47,48,51,52,53,54,55,56,57,58,],[18,-28,-26,-27,32,40,41,45,-30,46,-11,-15,47,-17,52,53,-21,-13,54,55,-29,-25,-24,-10,-14,57,-23,-20,-12,-22,58,-19,-16,]),'$end':([1,2,3,4,7,8,18,28,],[-1,-5,0,-4,-2,-3,-6,-7,]),'LPAREN':([0,1,2,4,7,8,10,12,14,15,16,17,18,19,20,21,23,24,25,26,27,28,29,30,31,32,33,34,35,37,38,39,40,41,42,43,44,45,46,47,48,52,53,54,55,57,58,],[5,5,-5,-4,-2,-3,13,-28,-9,13,-26,-27,-6,13,13,36,13,13,36,13,-8,-7,13,-30,13,-11,-15,36,-17,13,13,13,-21,-13,36,13,-29,-25,-24,-10,-14,-23,-20,-12,-22,-19,-16,]),'OP_MUL':([13,],[20,]),'STRING':([10,12,14,15,16,17,19,20,23,24,26,27,29,30,31,32,37,38,39,40,41,43,44,45,46,47,52,53,54,55,57,],[12,-28,-9,12,-26,-27,12,12,12,12,12,-8,12,-30,12,-11,12,12,12,-21,-13,12,-29,-25,-24,-10,-23,-20,-12,-22,-19,]),'INPUT':([13,],[21,]),'ASSIGN':([13,],[22,]),'LBRACE':([0,1,2,4,7,8,18,28,],[6,6,-5,-4,-2,-3,-6,-7,]),'ID':([6,9,10,12,13,14,15,16,17,19,20,21,22,23,24,25,26,27,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,52,53,54,55,57,58,],[10,11,16,-28,24,-9,16,-26,-27,16,16,35,37,16,16,35,16,-8,16,-30,16,-11,-15,35,-17,50,16,16,16,-21,-13,35,16,-29,-25,-24,-10,-14,56,-18,-23,-20,-12,-22,-19,-16,]),'OUTPUT':([13,],[25,]),'RBRACE':([12,14,15,16,17,27,32,40,41,45,46,47,52,53,54,55,57,],[-28,-9,28,-26,-27,-8,-11,-21,-13,-25,-24,-10,-23,-20,-12,-22,-19,]),'OP_ADD':([13,],[26,]),'NUMBER':([10,12,14,15,16,17,19,20,23,24,26,27,29,30,31,32,37,38,39,40,41,43,44,45,46,47,52,53,54,55,57,],[17,-28,-9,17,-26,-27,17,17,17,17,17,-8,17,-30,17,-11,17,17,17,-21,-13,17,-29,-25,-24,-10,-23,-20,-12,-22,-19,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'statement_list':([0,],[1,]),'declaration':([21,25,34,42,],[33,33,48,48,]),'component':([0,1,],[2,7,]),'expression_list':([10,],[15,]),'program':([0,],[3,]),'import_statement':([0,1,],[4,8,]),'parameter_list':([19,20,23,24,26,],[29,31,38,39,43,]),'declaration_list':([21,25,],[34,42,]),'type':([36,],[49,]),'expression':([10,15,19,20,23,24,26,29,31,37,38,39,43,],[14,27,30,30,30,30,30,44,44,51,44,44,44,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> statement_list','program',1,'p_program','parser.py',7),
  ('statement_list -> statement_list component','statement_list',2,'p_statement_list','parser.py',12),
  ('statement_list -> statement_list import_statement','statement_list',2,'p_statement_list','parser.py',13),
  ('statement_list -> import_statement','statement_list',1,'p_statement_list','parser.py',14),
  ('statement_list -> component','statement_list',1,'p_statement_list','parser.py',15),
  ('import_statement -> LPAREN IMPORT ID RPAREN','import_statement',4,'p_import_statement','parser.py',26),
  ('component -> LBRACE ID expression_list RBRACE','component',4,'p_component','parser.py',30),
  ('expression_list -> expression_list expression','expression_list',2,'p_expression_list','parser.py',34),
  ('expression_list -> expression','expression_list',1,'p_expression_list','parser.py',35),
  ('expression -> LPAREN INPUT declaration_list RPAREN','expression',4,'p_expression_input','parser.py',44),
  ('expression -> LPAREN INPUT RPAREN','expression',3,'p_expression_input','parser.py',45),
  ('expression -> LPAREN OUTPUT declaration_list RPAREN','expression',4,'p_expression_output','parser.py',52),
  ('expression -> LPAREN OUTPUT RPAREN','expression',3,'p_expression_output','parser.py',53),
  ('declaration_list -> declaration_list declaration','declaration_list',2,'p_declaration_list','parser.py',60),
  ('declaration_list -> declaration','declaration_list',1,'p_declaration_list','parser.py',61),
  ('declaration -> LPAREN type ID RPAREN','declaration',4,'p_declaration','parser.py',70),
  ('declaration -> ID','declaration',1,'p_declaration','parser.py',71),
  ('type -> ID','type',1,'p_type','parser.py',79),
  ('expression -> LPAREN ASSIGN ID expression RPAREN','expression',5,'p_expression_assign','parser.py',83),
  ('expression -> LPAREN ID parameter_list RPAREN','expression',4,'p_expression_parameter_list','parser.py',87),
  ('expression -> LPAREN ID RPAREN','expression',3,'p_expression_parameter_list','parser.py',88),
  ('expression -> LPAREN OP_ADD parameter_list RPAREN','expression',4,'p_op_add_expression','parser.py',96),
  ('expression -> LPAREN OP_SUB parameter_list RPAREN','expression',4,'p_op_sub_expression','parser.py',100),
  ('expression -> LPAREN OP_MUL parameter_list RPAREN','expression',4,'p_op_mul_expression','parser.py',104),
  ('expression -> LPAREN OP_DIV parameter_list RPAREN','expression',4,'p_op_div_expression','parser.py',108),
  ('expression -> ID','expression',1,'p_expression_id','parser.py',112),
  ('expression -> NUMBER','expression',1,'p_expression_num','parser.py',116),
  ('expression -> STRING','expression',1,'p_expression_str','parser.py',120),
  ('parameter_list -> parameter_list expression','parameter_list',2,'p_parameter_list','parser.py',124),
  ('parameter_list -> expression','parameter_list',1,'p_parameter_list','parser.py',125),
]
