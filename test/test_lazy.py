from pytest import raises
import numpy as np
from timeseries.TimeSeries import *
from timeseries.lazy import *

@lazy
def lazy_add(a,b):
    return a+b

@lazy
def lazy_mul(a,b):
    return a*b

@lazy
def lazy_mul_three(a,b, c):
    return a*b*c

@lazy
def check_length(a,b):
    return len(a)==len(b)


def test_eval():
    thunk = lazy_mul( lazy_mul_three(1,lazy_add(1,1),lazy_add(1,2)), 4)
    assert thunk.eval() == 24

    thunk = check_length(TimeSeries(range(0,4),range(1,5)).lazy, TimeSeries(range(1,5),range(2,6)))
    assert thunk.eval()==True

def test_lazy():
    assert isinstance( lazy_add(1,2), LazyOperation )==True
