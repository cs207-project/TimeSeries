import pkg_resources

from pype.ast import *
from pype.lexer import *
from pype.lib_import import *
from pype.parser import *
from pype.pipeline import *
from pype.semantic_analysis import *
from pype.symtab import *
from pype.translate import *
from ply import lex

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'
