import numpy.fft as nfft
import numpy as np
import timeseries as ts
from scipy.stats import norm
# import pyfftw
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

    # Get the next 2 th power 110 -> 128
    next_2 = int(2**np.ceil(np.log(len(ts1.values()))))

    # 
    ts1_value = ts1.values()
    ts2_value = ts2.values()
    ts1_container,ts2_container = [],[]
    ts1_zero_container = [0]*len(ts1.values())
    ts2_zero_container = [0]*len(ts2.values())

    ts1_c_array,ts2_c_array = [None]*(len(ts1.values())*2),[None]*(len(ts2.values())*2)

    ts1_c_array[::2] = ts1_value
    ts1_c_array[1::2] = ts1_zero_container
    ts2_c_array[::2] = ts2_value
    ts2_c_array[1::2] = ts2_zero_container

    for i in range(len(ts1_c_array)+1,next_2*2):
        ts1_c_array.append(np.double(0))

    for i in range(len(ts2_c_array)+1,next_2*2):
        ts2_c_array.append(np.double(0))
    ts1_c_array.insert(0,0)
    ts2_c_array.insert(0,0)


    ts1_c_array = createfromlist(np.double(ts1_c_array))
    ts2_c_array = createfromlist(np.double(ts2_c_array))
    
    four1(ts1_c_array,next_2,1)
    four1(ts2_c_array,next_2,1)


    for i in range(len(ts2.values())*2+1):
        ts1_container.append(darray_get(ts1_c_array,i))
    for j in range(len(ts1.values())*2+1):
<<<<<<< HEAD
        ts2_container.append(darray_get(ts2_c_array,j))


    ts1_fft = np.asarray(ts1_container[1::2]) + 1j * np.asarray(ts1_container[2::2])
    ts2_fft = np.asarray(ts2_container[1::2]) + 1j * np.asarray(ts2_container[2::2])
    ts1_fft = ts1_fft[:len(ts1)+1]
    ts2_fft = ts2_fft[:len(ts2)+1]


    # ifft part

    ts1_ts2_conj = ts1_fft * np.conj(ts2_fft)
    ts1_ts2_ifft_container = [0]*len(ts1_ts2_conj)*2
    ts1_ts2_ifft_container[::2] = ts1_ts2_conj.real
    ts1_ts2_ifft_container[1::2] = ts1_ts2_conj.imag

    for i in range(len(ts1_ts2_conj)+1, next_2 *2):
        ts1_ts2_ifft_container.append(0)

    ts1_ts2_ifft_container.insert(0,0)

    ts1_ts2_ifft_container = createfromlist(ts1_ts2_ifft_container)

    four1(ts1_ts2_ifft_container, next_2, -1)

    ts1_ts2_ifft_container_python = []

    for i in range(len(ts1_ts2_conj)*2+1):
        ts1_ts2_ifft_container_python.append(darray_get(ts1_ts2_ifft_container,i))

    ccor_value = np.asarray(ts1_ts2_ifft_container_python[1::2])

=======
        f4.append(darray_get(f8,j))
    f1 = np.asarray(f3[1::2]) + 1j * np.asarray(f3[2::2])
    f2 = np.asarray(f4[1::2]) + 1j * np.asarray(f4[2::2])
    f1 = f1[:len(ts1)+1]
    f2 = f2[:len(ts2)+1]

    f1_f2_conj = f1 * np.conj(f2)
    f3 = [0]*len(f1_f2_conj)*2
    f3[::2] = f1_f2_conj.real
    f3[1::2] = f1_f2_conj.imag
    for i in range(len(f1_f2_conj)+1, next_2 * 2):
        f3.append(0)
    f3.insert(0,0)
    f4 = createfromlist(f3)
    four1(f4, next_2, -1)
    f10 = []
    for i in range(len(f1_f2_conj)*2 + 1):
        f10.append(darray_get(f4, i))
    ccor_value = np.asarray(f10[1::2])


>>>>>>> 6898a732e3cb6d648bf847d59c832217bb0e2b4a
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
