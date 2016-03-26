import pkg_resources
import timeseries.TimeSeries
from timeseries.lazy import *
try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'
