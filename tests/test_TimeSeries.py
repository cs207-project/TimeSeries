from pytest import raises
import numpy as np
import timeserieslazy.TimeSeries as TS
from timeseries.lazy import *
import collections

testSeries = TS.TimeSeries(range(0,4),range(1,5))
testSeries2 = TS.TimeSeries(range(0,4),[10,20,30,40,50])

def test_len():
    assert len(testSeries) == 4

def test_contains():
    assert (2 in testSeries) == True

def test_getitem():
    assert testSeries[0] == 1

def test_setitem():
    tmpTestSeries = TS.TimeSeries(range(0,4),range(1,5))
    tmpTestSeries[0]=5
    assert tmpTestSeries[0] == 5

def test_equal():
    tmpTestSeries = TS.TimeSeries(range(0,4),range(1,5))
    assert tmpTestSeries == testSeries

def test_values():
    assert np.array_equal(testSeries.values(), range(1,5)) == True

def test_time():
    assert np.array_equal(testSeries.times(), range(0,4)) == True

def test_mean_empty():
    with raises(ValueError):
         TS.TimeSeries([],[]).mean() 

def test_median_empty():
    with raises(ValueError):
         TS.TimeSeries([],[]).median()

def test_mean():
    assert testSeries.mean() == 2.5

def test_median():
    assert testSeries.median() == 2.5

def test_itertimes():
    ti=testSeries.itertimes()
    assert next(ti)==0

def test_itervalue():
    vi=testSeries.itervalues()
    assert next(vi)==1

def test_iteritems():
    iti=testSeries.iteritems()
    assert next(iti)==(0,1)

def test_interpolation():
    a = TS.TimeSeries([0,5,10], [1,2,3])
    b = TS.TimeSeries([2.5,7.5], [100, -100])
    # Simple cases
    assert a.interpolate([1]) == TS.TimeSeries([1],[1.2])
    assert a.interpolate(b.times()) == TS.TimeSeries([2.5,7.5], [1.5, 2.5])
    # Boundary conditions
    assert a.interpolate([-100,100]) == TS.TimeSeries([-100,100],[1,3])
    
def test_add():
    a = TS.TimeSeries([0,5,10], [1,2,3])
    b = TS.TimeSeries([0,5,10], [10,20,30])
    c = 100
    d = TS.TimeSeries([0,1,2], [1,2,3])
    assert a+b == TS.TimeSeries([0,5,10],[11,22,33])
    assert a+c == TS.TimeSeries([0,5,10],[101,102,103])
    with raises(ValueError):
        a+d
    assert a+b == b+a
    assert c+a == a+c
    with raises(ValueError):
        d+a

def test_sub():
    a = TS.TimeSeries([0,5,10], [1,2,3])
    b = TS.TimeSeries([0,5,10], [10,20,30])
    c = 100
    d = TS.TimeSeries([0,1,2], [1,2,3])
    assert b-a == TS.TimeSeries([0,5,10],[9,18,27])
    assert a-c == TS.TimeSeries([0,5,10],[-99,-98,-97])
    with raises(ValueError):
        a-d

def test_neg():
    a = TS.TimeSeries([0,5,10], [1,2,3])
    b = TS.TimeSeries([0,5,10], [10,20,30])
    assert -a == TS.TimeSeries([0,5,10],[-1,-2,-3])

def test_pos():
    a = TS.TimeSeries([0,5,10], [-1,-2,3])
    assert +a == a

def test_mul():
    a = TS.TimeSeries([0,5,10], [1,2,3])
    b = TS.TimeSeries([0,5,10], [10,20,30])
    c = 100
    d = TS.TimeSeries([0,1,2], [1,2,3])
    assert a*b == TS.TimeSeries([0,5,10],[10,40,90])
    assert a*c == TS.TimeSeries([0,5,10],[100,200,300])
    with raises(ValueError):
        a*d
    assert a*b == b*a
    assert c*a == a*c
    with raises(ValueError):
        d*a

def test_abs():
    a = TS.TimeSeries([0,5], [3,4])
    assert abs(a)==5.

def test_bool():
    a = TS.TimeSeries([0],[0])
    assert abs(a)==False

def test_neg():
    a = TS.TimeSeries([0,5,10], [1,2,3])
    b = TS.TimeSeries([0,5,10], [10,20,30])
    assert -a == TS.TimeSeries([0,5,10],[-1,-2,-3])

def test_pos():
    a = TS.TimeSeries([0,5,10], [-1,-2,3])
    assert +a == a

@lazy
def check_length(a,b):
    return len(a)==len(b)

def test_check_length():
    thunk = check_length(TS.TimeSeries(range(0,4),range(1,5)).lazy, TS.TimeSeries(range(1,5),range(2,6)))
