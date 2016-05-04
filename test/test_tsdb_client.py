from tsdb import TSDBClient
from timeseries.TimeSeries import TimeSeries
import numpy as np
import subprocess
import asynctest
import time
from scipy.stats import norm

def tsmaker(m, s, j):
    "returns metadata and a time series in the shape of a jittered normal"
    meta={}
    meta['order'] = int(np.random.choice([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]))
    meta['blarg'] = int(np.random.choice([1, 2]))
    t = np.arange(0.0, 1.0, 0.1)
    v = norm.pdf(t, m, s) + j*np.random.randn(10)
    return meta, TimeSeries(t, v)

class Test_TSDB_Client(asynctest.TestCase):

    def setUp(self):
        self.server_log_file = open('.test_tsdb_client_log','w')
        self.server_proc = subprocess.Popen(['python', 'go_server.py']
            ,stdout=self.server_log_file,stderr=subprocess.STDOUT)
        time.sleep(1)

        self.client = TSDBClient()
        self.client.add_trigger('junk', 'insert_ts', None, 'db:one:ts')

        self.client.add_trigger('stats', 'insert_ts', ['mean', 'std'], None)
        #Set up 50 time series
        mus = np.random.uniform(low=0.0, high=1.0, size=10)
        sigs = np.random.uniform(low=0.05, high=0.4, size=10)
        jits = np.random.uniform(low=0.05, high=0.2, size=10)

        # dictionaries for time series and their metadata
        self.tsdict={}
        self.metadict={}
        for i, m, s, j in zip(range(10), mus, sigs, jits):
            meta, tsrs = tsmaker(m, s, j)
            # the primary key format is ts-1, ts-2, etc
            pk = "ts-{}".format(i)
            self.tsdict[pk] = tsrs
            meta['vp'] = False # augment metadata with a boolean asking if this is a  VP.
            self.metadict[pk] = meta

        # choose 5 distinct vantage point time series
        self.vpkeys = ["ts-{}".format(i) for i in np.random.choice(range(10), size=5, replace=False)]
        for i in range(5):
            # add 5 triggers to upsert distances to these vantage points
            self.client.add_trigger('corr', 'insert_ts', ["d_vp-{}".format(i)], self.tsdict[self.vpkeys[i]])
            # change the metadata for the vantage points to have meta['vp']=True
            self.metadict[self.vpkeys[i]]['vp']=True

    def tearDown(self):
        # Shuts down the server
        self.server_proc.terminate()
        self.server_log_file.close()
        time.sleep(1)

    def test_upsert(self):
        print('Test upsert')

        # Having set up the triggers, now inser the time series, and upsert the metadata
        for k in self.tsdict:
            self.client.insert_ts(k, self.tsdict[k])
            self.client.upsert_meta(k, self.metadict[k])

    def test_select1(self):
        print("Test select")
        print('---------DEFAULT------------')
        self.client.select()

    def test_select2(self):
        print("Test select")
        print('---------ADDITIONAL------------')
        self.client.select(additional={'sort_by': '-order'})

    def test_select3(self):
        print("Test select")
        print('----------ORDER FIELD-----------')
        _, results = self.client.select(fields=['order'])
        for k in results:
            print(k, results[k])

    def test_select4(self):
        print("Test select")
        print('---------ALL FILEDS------------')
        self.client.select(fields=[])

    def test_select5(self):
        print("Test select")
        print('------------TS with order 1---------')
        self.client.select({'order': 1}, fields=['ts'])

    def test_select6(self):
        print("Test select")
        print('------------All fields, blarg 1 ---------')
        self.client.select({'blarg': 1}, fields=[])

    def test_select7(self):
        print("Test select")
        print('------------order 1 blarg 2 no fields---------')
        _, bla = self.client.select({'order': 1, 'blarg': 2})
        print(bla)

    def test_select8(self):
        print("Test select")
        print('------------order >= 4  order, blarg and mean sent back, also sorted---------')
        _, results = self.client.select({'order': {'>=': 4}}, fields=['order', 'blarg', 'mean'], additional={'sort_by': '-order'})
        for k in results:
            print(k, results[k])

    def test_select9(self):
        print("Test select")
        print('------------order 1 blarg >= 1 fields blarg and std---------')
        _, results = self.client.select({'blarg': {'>=': 1}, 'order': 1}, fields=['blarg', 'std'])
        for k in results:
            print(k, results[k])

if __name__ == '__main__':
    asynctest.main()