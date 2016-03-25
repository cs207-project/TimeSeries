import pkg_resources
from pype.pipeline import Pipeline

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'
