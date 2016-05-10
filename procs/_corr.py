import numpy.fft as nfft
import numpy as np
import timeseries as ts
from scipy.stats import norm
import pyfftw
import sys
#sys.path.append("/Users/yuhantang/CS207/TimeSeries/procs")
from .interface import *

def createfromlist(l):
    d = new_darray(len(l))
    for i in range(0,len(l)):
        darray_set(d,i,l[i])
    return d

def tsmaker(m, s, j):
    meta={}
    meta['order'] = int(np.random.choice([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]))
    meta['blarg'] = int(np.random.choice([1, 2]))
    t = np.arange(0.0, 1.0, 0.01)
    v = norm.pdf(t, m, s) + j*np.random.randn(100)
    return meta, ts.TimeSeries(t, v)

def random_ts(a):
    t = np.arange(0.0, 1.0, 0.01)
    v = a*np.random.random(100)
    return ts.TimeSeries(t, v)

def stand(x, m, s):

    return (x-m)/s

def ccor(ts1, ts2):
    "given two standardized time series, compute their cross-correlation using FFT"

    next_2 = int(2**np.ceil(np.log(len(ts1.values()))))
    ts_1 = pyfftw.empty_aligned(len(ts1), dtype='complex128', n=16)
    ts_1[:] = ts1
    f1 = ts1.values()
    f2 = ts2.values()
    f3,f4 = [],[]
    f5 = [0]*len(ts1.values())
    f6 = [0]*len(ts2.values())

    f7,f8 = [None]*(len(f5)*2),[None]*(len(f6)*2)

    f7[::2] = f1
    f7[1::2] = f5
    f8[::2] = f2
    f8[1::2] = f6

    for i in range(len(f7)+1,next_2*2):
        f7.append(np.double(0))

    for i in range(len(f8)+1,next_2*2):
        f8.append(np.double(0))
    f7.insert(0,0)
    f8.insert(0,0)
    f7 = createfromlist(np.double(f7))
    f8 = createfromlist(np.double(f8))
    
    four1(f7,next_2,1)
    four1(f8,next_2,1)
    for i in range(len(ts2.values())*2+1):
        f3.append(darray_get(f7,i))
    for j in range(len(ts1.values())*2+1):
        f4.append(darray_get(f8,j))
    f1 = np.asarray(f3[1::2]) + 1j * np.asarray(f3[2::2])
    f2 = np.asarray(f4[1::2]) + 1j * np.asarray(f4[2::2])
    f1 = f1[:len(ts1)+1]
    f2 = f2[:len(ts2)+1]
    ccor_value = nfft.ifft(f1 * np.conj(f2)).real
    return 1/len(ts1) * ccor_value


def max_corr_at_phase(ts1, ts2):
    ccorts = ccor(ts1, ts2)
    idx = np.argmax(ccorts)
    maxcorr = ccorts[idx]
    return idx, maxcorr

#The equation for the kernelized cross correlation is given at
#http://www.cs.tufts.edu/~roni/PUB/ecml09-tskernels.pdf
#normalize the kernel there by np.sqrt(K(x,x)K(y,y)) so that the correlation
#of a time series with itself is 1.
def kernel_corr(ts1, ts2, mult=1):
    "compute a kernelized correlation so that we can get a real distance"
    #your code here.
    cross_correlation = ccor(ts1, ts2) * mult
    corr_ts1, corr_ts2 = ccor(ts1, ts1) * mult, ccor(ts2, ts2) * mult
    return np.sum(np.exp(cross_correlation))/np.sqrt(np.sum(np.exp(corr_ts1))*np.sum(np.exp(corr_ts2)))



#this is for a quick and dirty test of these functions
#you might need to add procs to pythonpath for this to work
if __name__ == "__main__":
    print("HI")
    _, t1 = tsmaker(0.5, 0.1, 0.01)
    _, t2 = tsmaker(0.5, 0.1, 0.01)
    print(t1.mean(), t1.std(), t2.mean(), t2.std())
    import matplotlib.pyplot as plt
    plt.plot(t1)
    plt.plot(t2)
    plt.show()
    standts1 = stand(t1, t1.mean(), t1.std())
    standts2 = stand(t2, t2.mean(), t2.std())
    #print(type(standts1),'this is the type=================*********')
    #assert 1 == 2
    idx, mcorr = max_corr_at_phase(standts1, standts2)
    print(idx, mcorr)
    sumcorr = kernel_corr(standts1, standts2, mult=10)
    print(sumcorr)
    t3 = random_ts(2)
    t4 = random_ts(3)
    plt.plot(t3)
    plt.plot(t4)
    plt.show()
    standts3 = stand(t3, t3.mean(), t3.std())
    standts4 = stand(t4, t4.mean(), t4.std())
    idx, mcorr = max_corr_at_phase(standts3, standts4)
    print(idx, mcorr)
    sumcorr = kernel_corr(standts3, standts4, mult=10)
    print(sumcorr)
