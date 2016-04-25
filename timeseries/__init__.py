import pkg_resources
from timeseries.TimeSeries import *
from timeseries.lazy import *
try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'
