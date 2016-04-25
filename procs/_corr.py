import numpy.fft as nfft
import numpy as np
import timeseries as ts
from scipy.stats import norm

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
    #print(type(x),type(m),type(s))
    #print(type((x-m)/s),'hey go fuck yourself')
    return (x-m)/s

def ccor(ts1, ts2):
    "given two standardized time series, compute their cross-correlation using FFT"
    #your code here
    #print(type(ts1))
    #print(type(ts1.values()))
    f1 = nfft.fft(ts1.values())
    f2 = nfft.fft(ts2.values())
    #print(f1)

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
    ccor_value = ccor(ts1, ts2)
    return np.sum(np.exp(ccor_value*mult))/np.sqrt(np.sum(np.exp(ccor_value))*np.sum(np.exp(mult*ccor_value)))



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
