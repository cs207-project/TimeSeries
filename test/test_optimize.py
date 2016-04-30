from pytest import raises
from test.test_fgir import *
from pype.optimize import *
import copy


# for testing the sort (test case from Pype Part 3 explanation)
# just refer to Pype 3 part 3 graph
FG = Flowgraph('TEST_1')

A = FG.new_node(FGNodeType.unknown, 'x')
B = FG.new_node(FGNodeType.unknown, 'y')
C = FG.new_node(FGNodeType.unknown, 'n2')
D = FG.new_node(FGNodeType.assignment, 'z')
E = FG.new_node(FGNodeType.unknown, 'n4')
F = FG.new_node(FGNodeType.assignment, 'n5') #this is dead code for test
H = FG.new_node(FGNodeType.unknown, 'n6')
I = FG.new_node(FGNodeType.unknown, 'n7')

A.inputs = []
B.inputs = []
C.inputs = ['@N0','@N1']
D.inputs = ['@N2']
E.inputs = ['@N3']
F.inputs = ['@N6']
I.inputs = ['@N5']
FG.topological_sort(False)
FG.outputs = ['@N4']
# print(FG.inputs)

x = FGIR()
x.graphs['test'] = FG



def test_AssignmentEllision():
    test_fg = copy.deepcopy(FG)
    test_AE = AssignmentEllision()
    test_AE.visit(test_fg)
    # print(test_fg.nodes.keys())
    assert set(test_fg.nodes.keys()) == set(['@N6', '@N0', '@N1', '@N7', '@N2', '@N4'])
    # print(test_fg.dotfile())
  #   assert test_fg.dotfile()=='digraph TEST_1 {\n \
  # "@N2" -> "@N4"\n\
  # "@N0" -> "@N2"\n\
  # "@N1" -> "@N2"\n\
  # "@N6" -> "@N7"\n\
  # "@N4" [ color = "red" ]\n\
  # }\n'

def test_DeadCodeElimination():
    test_fg = copy.deepcopy(FG)
    testDeadCodeElimination = DeadCodeElimination()
    testDeadCodeElimination.visit(test_fg)
    assert set(test_fg.nodes.keys()) == set(['@N4', '@N3', '@N0', '@N2', '@N1'])
  #   assert FG.dotfile()== 'digraph TEST_1 {\
  # "@N2" -> "@N3"\
  # "@N3" -> "@N4"\
  # "@N0" -> "@N2"\
  # "@N1" -> "@N2"\
  # "@N4" [ color = "red" ]\
  # }'

# test_AssignmentEllision()
# test_DeadCodeElimination()