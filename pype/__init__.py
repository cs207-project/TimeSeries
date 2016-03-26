import pkg_resources
from pype.semantic_analysis import *
from pype.lexer import *
from pype.ast import *
from pype.parser import *
from pype.pipeline import *
from pype.translate import *
from pype.symtab import *
from pype.lib_import import *
try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'
