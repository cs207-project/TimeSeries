from tsdb import TSDBClient
from timeseries.TimeSeries import TimeSeries
import numpy as np
import subprocess
import asynctest
from scipy.stats import norm
import time

def tsmaker(m, s, j):
    "returns metadata and a time series in the shape of a jittered normal"
    meta={}
    meta['order'] = int(np.random.choice([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]))
    meta['blarg'] = int(np.random.choice([1, 2]))
    t = np.arange(0.0, 1.0, 0.1)
    v = norm.pdf(t, m, s) + j*np.random.randn(10)
    return meta, TimeSeries(t, v)

class Test_TSDB_Client(asynctest.TestCase):

    async def setUp(self):
        self.server_log_file = open('.test_tsdb_client_log','w')
        self.server_proc = subprocess.Popen(['python', 'go_server.py']
            ,stdout=self.server_log_file,stderr=subprocess.STDOUT)

        time.sleep(1)

        self.client = TSDBClient()
        await self.client.add_trigger('junk', 'insert_ts', None, 'db:one:ts')
        await self.client.add_trigger('stats', 'insert_ts', ['mean', 'std'], None)

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
            await self.client.add_trigger('corr', 'insert_ts', ["d_vp-{}".format(i)], self.tsdict[self.vpkeys[i]])
            # change the metadata for the vantage points to have meta['vp']=True
            self.metadict[self.vpkeys[i]]['vp']=True

        print('Test upsert')

        # Having set up the triggers, now inser the time series, and upsert the metadata
        for k in self.tsdict:
            await self.client.insert_ts(k, self.tsdict[k])
            await self.client.upsert_meta(k, self.metadict[k])

        time.sleep(1)

    def tearDown(self):
        # Shuts down the server
        self.server_proc.terminate()
        self.server_log_file.close()
        time.sleep(1)

    async def test_select1(self):
        print("Test select")
        print('---------DEFAULT------------')
        await self.client.select()

    async def test_select2(self):
        print("Test select")
        print('---------ADDITIONAL------------')
        await self.client.select(additional={'sort_by': '-order'})

    async def test_select3(self):
        print("Test select")
        print('----------ORDER FIELD-----------')
        _, results = await self.client.select(fields=['order'])
        for k in results:
            print(k, results[k])

    async def test_select4(self):
        print("Test select")
        print('---------ALL FILEDS------------')
        await self.client.select(fields=[])

    async def test_select5(self):
        print("Test select")
        print('------------TS with order 1---------')
        await self.client.select({'order': 1}, fields=['ts'])

    async def test_select6(self):
        print("Test select")
        print('------------All fields, blarg 1 ---------')
        await self.client.select({'blarg': 1}, fields=[])

    async def test_select7(self):
        print("Test select")
        print('------------order 1 blarg 2 no fields---------')
        _, bla = await self.client.select({'order': 1, 'blarg': 2})
        print(bla)

    async def test_select8(self):
        print("Test select")
        print('------------order >= 4  order, blarg and mean sent back, also sorted---------')
        _, results = await self.client.select({'order': {'>=': 4}}, fields=['order', 'blarg', 'mean'], additional={'sort_by': '-order'})
        for k in results:
            print(k, results[k])

    async def test_select9(self):
        print("Test select")
        print('------------order 1 blarg >= 1 fields blarg and std---------')
        _, results = await self.client.select({'blarg': {'>=': 1}, 'order': 1}, fields=['blarg', 'std'])
        for k in results:
            print(k, results[k])

if __name__ == '__main__':
    asynctest.main()