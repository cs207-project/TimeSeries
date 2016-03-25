
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = '371EF72B57DF7D01BB0A145AD73D5ADC'
    
_lr_action_items = {'OP_ADD':([15,],[19,]),'$end':([2,3,5,6,9,10,18,27,],[-5,0,-1,-4,-2,-3,-6,-7,]),'RBRACE':([12,13,14,16,17,28,31,35,41,45,46,47,48,51,54,55,57,],[-26,-9,-27,27,-28,-8,-21,-11,-13,-22,-20,-24,-23,-10,-12,-25,-19,]),'NUMBER':([8,12,13,14,16,17,19,20,21,22,26,28,29,30,31,32,33,34,35,40,41,43,44,45,46,47,48,51,54,55,57,],[14,-26,-9,-27,14,-28,14,14,14,14,14,-8,-30,14,-21,14,14,14,-11,14,-13,14,-29,-22,-20,-24,-23,-10,-12,-25,-19,]),'IMPORT':([1,],[7,]),'OP_MUL':([15,],[21,]),'OP_SUB':([15,],[22,]),'OUTPUT':([15,],[25,]),'RPAREN':([11,12,14,17,20,23,25,29,30,31,32,33,34,35,37,38,39,41,42,43,44,45,46,47,48,51,52,53,54,55,56,57,58,],[18,-26,-27,-28,31,35,41,-30,45,-21,46,47,48,-11,-17,-15,51,-13,54,55,-29,-22,-20,-24,-23,-10,-14,57,-12,-25,58,-19,-16,]),'LPAREN':([0,2,5,6,8,9,10,12,13,14,16,17,18,19,20,21,22,23,25,26,27,28,29,30,31,32,33,34,35,37,38,39,40,41,42,43,44,45,46,47,48,51,52,54,55,57,58,],[1,-5,1,-4,15,-2,-3,-26,-9,-27,15,-28,-6,15,15,15,15,36,36,15,-7,-8,-30,15,-21,15,15,15,-11,-17,-15,36,15,-13,36,15,-29,-22,-20,-24,-23,-10,-14,-12,-25,-19,-16,]),'ID':([4,7,8,12,13,14,15,16,17,19,20,21,22,23,24,25,26,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,54,55,57,58,],[8,11,12,-26,-9,-27,20,12,-28,12,12,12,12,37,40,37,12,-8,-30,12,-21,12,12,12,-11,50,-17,-15,37,12,-13,37,12,-29,-22,-20,-24,-23,56,-18,-10,-14,-12,-25,-19,-16,]),'ASSIGN':([15,],[24,]),'LBRACE':([0,2,5,6,9,10,18,27,],[4,-5,4,-4,-2,-3,-6,-7,]),'OP_DIV':([15,],[26,]),'INPUT':([15,],[23,]),'STRING':([8,12,13,14,16,17,19,20,21,22,26,28,29,30,31,32,33,34,35,40,41,43,44,45,46,47,48,51,54,55,57,],[17,-26,-9,-27,17,-28,17,17,17,17,17,-8,-30,17,-21,17,17,17,-11,17,-13,17,-29,-22,-20,-24,-23,-10,-12,-25,-19,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'declaration':([23,25,39,42,],[38,38,52,52,]),'declaration_list':([23,25,],[39,42,]),'component':([0,5,],[2,9,]),'program':([0,],[3,]),'expression':([8,16,19,20,21,22,26,30,32,33,34,40,43,],[13,28,29,29,29,29,29,44,44,44,44,53,44,]),'statement_list':([0,],[5,]),'expression_list':([8,],[16,]),'type':([36,],[49,]),'parameter_list':([19,20,21,22,26,],[30,32,33,34,43,]),'import_statement':([0,5,],[6,10,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> statement_list','program',1,'p_program','parser.py',8),
  ('statement_list -> statement_list component','statement_list',2,'p_statement_list','parser.py',13),
  ('statement_list -> statement_list import_statement','statement_list',2,'p_statement_list','parser.py',14),
  ('statement_list -> import_statement','statement_list',1,'p_statement_list','parser.py',15),
  ('statement_list -> component','statement_list',1,'p_statement_list','parser.py',16),
  ('import_statement -> LPAREN IMPORT ID RPAREN','import_statement',4,'p_import_statement','parser.py',27),
  ('component -> LBRACE ID expression_list RBRACE','component',4,'p_component','parser.py',31),
  ('expression_list -> expression_list expression','expression_list',2,'p_expression_list','parser.py',35),
  ('expression_list -> expression','expression_list',1,'p_expression_list','parser.py',36),
  ('expression -> LPAREN INPUT declaration_list RPAREN','expression',4,'p_expression_input','parser.py',45),
  ('expression -> LPAREN INPUT RPAREN','expression',3,'p_expression_input','parser.py',46),
  ('expression -> LPAREN OUTPUT declaration_list RPAREN','expression',4,'p_expression_output','parser.py',53),
  ('expression -> LPAREN OUTPUT RPAREN','expression',3,'p_expression_output','parser.py',54),
  ('declaration_list -> declaration_list declaration','declaration_list',2,'p_declaration_list','parser.py',61),
  ('declaration_list -> declaration','declaration_list',1,'p_declaration_list','parser.py',62),
  ('declaration -> LPAREN type ID RPAREN','declaration',4,'p_declaration','parser.py',71),
  ('declaration -> ID','declaration',1,'p_declaration','parser.py',72),
  ('type -> ID','type',1,'p_type','parser.py',80),
  ('expression -> LPAREN ASSIGN ID expression RPAREN','expression',5,'p_expression_assign','parser.py',84),
  ('expression -> LPAREN ID parameter_list RPAREN','expression',4,'p_expression_parameter_list','parser.py',88),
  ('expression -> LPAREN ID RPAREN','expression',3,'p_expression_parameter_list','parser.py',89),
  ('expression -> LPAREN OP_ADD parameter_list RPAREN','expression',4,'p_expression_add','parser.py',97),
  ('expression -> LPAREN OP_SUB parameter_list RPAREN','expression',4,'p_expression_sub','parser.py',101),
  ('expression -> LPAREN OP_MUL parameter_list RPAREN','expression',4,'p_expression_mul','parser.py',105),
  ('expression -> LPAREN OP_DIV parameter_list RPAREN','expression',4,'p_expression_div','parser.py',109),
  ('expression -> ID','expression',1,'p_expression_id','parser.py',113),
  ('expression -> NUMBER','expression',1,'p_expression_num','parser.py',117),
  ('expression -> STRING','expression',1,'p_expression_str','parser.py',121),
  ('parameter_list -> parameter_list expression','parameter_list',2,'p_parameter_list','parser.py',125),
  ('parameter_list -> expression','parameter_list',1,'p_parameter_list','parser.py',126),
]
