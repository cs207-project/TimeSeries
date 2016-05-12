import unittest
import asynctest
import numpy as np
from scipy.stats import norm
from web.web_for_coverage import WebInterface
import time
import subprocess
import timeseries as ts
import json


def tsmaker(m, s, j):
    "returns metadata and a time series in the shape of a jittered normal"
    meta={}
    meta['order'] = int(np.random.choice([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]))
    meta['blarg'] = int(np.random.choice([1, 2]))
    t = np.arange(0.0, 1.0, 0.01)
    v = norm.pdf(t, m, s) + j*np.random.randn(100)
    return meta, ts.TimeSeries(t, v)


class test_webinterface(asynctest.TestCase):
    def setUp(self):
        '''Method or coroutine called to prepare the test fixture.'''
        self.server = subprocess.Popen(['python', 'go_server.py'])
        time.sleep(1)

        self.web = subprocess.Popen(['python', 'go_web.py'])
        time.sleep(1)

        self.web_interface = WebInterface()

    def tearDown(self):
        self.server.terminate()
        self.web.terminate()

    async def test_web_total(self):

        results = self.web_interface.add_trigger(
            'junk', 'insert_ts', None, 'db:one:ts')
        assert results == 200

        results = self.web_interface.add_trigger(
            'stats', 'insert_ts', ['mean', 'std'], None)
        assert results == 200

        #Set up 50 time series
        mus = np.random.uniform(low=0.0, high=1.0, size=50)
        sigs = np.random.uniform(low=0.05, high=0.4, size=50)
        jits = np.random.uniform(low=0.05, high=0.2, size=50)

        # initialize dictionaries for time series and their metadata
        tsdict = {}
        metadict = {}
        for i, m, s, j in zip(range(50), mus, sigs, jits):
            meta, tsrs = tsmaker(m, s, j)
            # the primary key format is ts-1, ts-2, etc
            pk = "ts-{}".format(i)
            tsdict[pk] = tsrs
            meta['vp'] = False # augment metadata with a boolean asking if this is a  VP.
            metadict[pk] = meta


        vpkeys = ["ts-{}".format(i) for i in np.random.choice(range(50), size=5, replace=False)]
        for i in range(5):
            # add 5 triggers to upsert distances to these vantage points
            # data = json.dumps({'proc':'corr', 'onwhat':'insert_ts', 'target':["d_vp-{}".format(i)], 'arg':tsdict[vpkeys[i]].to_json()})
            # r = requests.post(self.web_url+'/add_trigger', data)

            r = self.web_interface.add_trigger('corr', 'insert_ts', ["d_vp-{}".format(i)], tsdict[vpkeys[i]].to_json())
            assert(r == 200)
            # change the metadata for the vantage points to have meta['vp']=True
            metadict[vpkeys[i]]['vp'] = True

        # Having set up the triggers, now insert the time series, and upsert the metadata
        # ==========================================
        # When it's first time to insert these keys in TSDB_server,
        # insert_ts will work and return TSDBStatus.OK
        # ==========================================
        for k in tsdict:
            results = self.web_interface.insert_ts(k, tsdict[k])
            assert(results == 200)

            # upsert meta
            results = self.web_interface.upsert_meta(k, metadict[k])
            assert(results == 200)

        # ==========================================
        # However if it's not first time to insert these keys,
        # insert_ts will return TSDBStatus.INVALID_KEY
        # ==========================================
        # pick a random pk
        idx = np.random.choice(list(tsdict.keys()))

        # check that the time series is there now
        results = self.web_interface.select({'pk': idx})
        assert results == 200

        # delete an existing time series
        results = self.web_interface.delete_ts(idx)
        assert results == 200

        # check that the time series is no longer there
        results = self.web_interface.select({'pk': idx})
        assert results == 200

        # add the time series back in
        results = self.web_interface.insert_ts(idx, tsdict[idx])
        assert results == 200

        #we first create a query time series.
        _, query = tsmaker(0.5, 0.2, 0.1)

        # Step 1: in the vpdist key, get  distances from query to vantage points
        # this is an augmented select
        vpdist = {}
        # payload = {"proc":"corr", "target":"d", "arg":query.to_json()}
        for v in vpkeys:
            # payload['where'] = {'pk': v}
            results = self.web_interface.augmented_select(
            proc='corr', target="d", arg=query, md={'pk':v})
            # r = requests.get(web_url+'/augmented_select', {'query':json.dumps(payload)})
            # print("aug_select r content", r.content)
            # results = json.loads(r.content.decode('utf-8'))
            # vpdist[v] = results[v]['d']


if __name__ == '__main__':
    unittest.main()