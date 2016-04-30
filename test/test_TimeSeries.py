from pytest import raises
import numpy as np
from timeseries.TimeSeries import TimeSeries
from timeseries.lazy import *
import collections

# Test data
ts0 = TimeSeries([],[])
ts1 = TimeSeries(range(0,4),range(1,5))
ts2 = TimeSeries(range(0,4),[10,20,30,40,50])
ts3 = TimeSeries([0,5,10], [1,2,3])
ts4 = TimeSeries([2.5,7.5], [100, -100])

# Lab 07
def test_len():
    assert len(ts1) == 4

def test_getitem():
    assert ts1[0] == 1

def test_setitem():
    tmpTestSeries = TimeSeries(range(0,4),range(1,5))
    tmpTestSeries[0]=5
    assert tmpTestSeries[0] == 5

# Lab 08 same as Lab 07


# Lab 10
def test_contains():
    assert (2 in ts1) == True

def test_values():
    assert np.array_equal(ts1.values(), range(1,5)) == True

def test_times():
    assert np.array_equal(ts1.times(), range(0,4)) == True

def test_items():
    assert ts1.items()==list((t,v) for t,v in zip(range(0,4), range(1,5)))

def test_interpolation():
    # Simple cases
    c = TimeSeries([1.],[1.2])
    d = ts3.interpolate([1.])
    assert c == d
    assert ts3.interpolate(ts4.times()) == TimeSeries([2.5,7.5], [1.5, 2.5])
    # Boundary conditions
    assert ts3.interpolate([-100,100]) == TimeSeries([-100,100],[1,3])

@lazy
def check_length(a,b):
    return len(a)==len(b)

def test_check_length():
    thunk = check_length(TimeSeries(range(0,4),range(1,5)).lazy, TimeSeries(range(1,5),range(2,6)))

# Lab 11
def test_median():
    assert ts1.median() == 2.5
    with raises(ValueError):
         ts0.median()


# Lab 12
def test_itertimes():
    ti=ts1.itertimes()
    assert next(ti)==0

def test_itervalue():
    vi=ts1.itervalues()
    assert next(vi)==1

def test_iteritems():
    iti=ts1.iteritems()
    assert next(iti)==(0,1)


# Lab 15
def test_equal():
    tmpTestSeries = TimeSeries(range(0,4),range(1,5))
    assert tmpTestSeries == ts1
    
def test_add():
    c = 100
    d = TimeSeries([0,1,2], [1,2,3])
    assert ts1+ts2 == TimeSeries(range(0,4),[11,22,33,44,55])
    assert ts1+c == TimeSeries(range(0,4),[101,102,103,104,105])
    with raises(ValueError):
        ts1+d
    assert ts1+ts2 == ts2+ts1
    assert c+ts1 == ts1+c
    with raises(ValueError):
        d+ts1

def test_sub():
    a = TimeSeries([0,5,10], [1,2,3])
    b = TimeSeries([0,5,10], [10,20,30])
    c = 100
    d = TimeSeries([0,1,2], [1,2,3])
    assert b-a == TimeSeries([0,5,10],[9,18,27])
    assert a-c == TimeSeries([0,5,10],[-99,-98,-97])
    with raises(ValueError):
        a-d

def test_neg():
    a = TimeSeries([0,5,10], [1,2,3])
    b = TimeSeries([0,5,10], [10,20,30])
    assert -a == TimeSeries([0,5,10],[-1,-2,-3])

def test_pos():
    a = TimeSeries([0,5,10], [-1,-2,3])
    assert +a == a

def test_mul():
    a = TimeSeries([0,5,10], [1,2,3])
    b = TimeSeries([0,5,10], [10,20,30])
    c = 100
    d = TimeSeries([0,1,2], [1,2,3])
    assert a*b == TimeSeries([0,5,10],[10,40,90])
    assert a*c == TimeSeries([0,5,10],[100,200,300])
    with raises(ValueError):
        a*d
    assert a*b == b*a
    assert c*a == a*c
    with raises(ValueError):
        d*a

def test_abs():
    a = TimeSeries([0,5], [3,4])
    assert abs(a)==5.

def test_bool():
    a = TimeSeries([0],[0])
    assert abs(a)==False

def test_neg():
    a = TimeSeries([0,5,10], [1,2,3])
    b = TimeSeries([0,5,10], [10,20,30])
    assert -a == TimeSeries([0,5,10],[-1,-2,-3])

def test_pos():
    a = TimeSeries([0,5,10], [-1,-2,3])
    assert +a == a

# Lab 19
def test_std():
    assert ts1.std() == 1.1180339887498949
    with raises(ValueError):
        ts0.std()

def test_mean():
    assert ts1.mean() == 2.5
    with raises(ValueError):
        ts0.mean() 

# Pype Component
def test_div():
    a = TimeSeries([0,5,10], [1,2,3])
    b = TimeSeries([0,5,10], [10,20,30])
    c = 10
    assert b/a == TimeSeries([0,5,10], [10,10,10])
    assert b/c == TimeSeries([0,5,10], [1,2,3])