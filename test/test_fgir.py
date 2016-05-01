from pytest import raises
from pype.fgir import *


one_tree = Flowgraph('test_fgir')

test_fgir_A = one_tree.new_node(FGNodeType.unknown, 'x')
test_fgir_B = one_tree.new_node(FGNodeType.unknown, 'y')
test_fgir_C = one_tree.new_node(FGNodeType.unknown, 'n2')
test_fgir_D = one_tree.new_node(FGNodeType.unknown, 'z')
test_fgir_E = one_tree.new_node(FGNodeType.unknown, 'n4')

test_fgir_A.inputs = []
test_fgir_B.inputs = []
test_fgir_C.inputs = ['@N0','@N1']
test_fgir_D.inputs = ['@N2']
test_fgir_E.inputs = ['@N3']

def test_topological_sort():
    assert one_tree.topological_sort(False) \
           in [['@N0', '@N1', '@N2', '@N3', '@N4'],
               ['@N1', '@N0', '@N2', '@N3', '@N4']]
