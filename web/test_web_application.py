import asynctest
import timeseries as ts
import subprocess
import time
import unittest
import numpy as np
import requests
import json
from scipy.stats import norm

# m is the mean, s is the standard deviation, and j is the jitter
# the meta just fills in values for order and blarg from the schema
def tsmaker(m, s, j):
    "returns metadata and a time series in the shape of a jittered normal"
    meta={}
    meta['order'] = int(np.random.choice([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]))
    meta['blarg'] = int(np.random.choice([1, 2]))
    t = np.arange(0.0, 1.0, 0.01)
    v = norm.pdf(t, m, s) + j*np.random.randn(100)
    return meta, ts.TimeSeries(t, v)

def select_to_str(md=None, fields=None, additional=None):
    return_str= '{'
    if md is not None:
        return_str+='"md":'+str(md)
    if fields is not None:
        return_str+='"fields":'+str(fields)
    if additional is not None:
        return_str+='"additional":'+str(additional)
    return_str+='}'
    return return_str


def make_remove_trigger(proc, onwhat):
    return json.dumps({'proc':proc,'onwhat':onwhat})



class Test_Web_Application(unittest.TestCase):
    def setUp(self):
        '''Method or coroutine called to prepare the test fixture.'''
        self.server_log_file = open('.test_rest_api_server_log', 'w')
        self.server_proc = subprocess.Popen(['python', 'go_server.py'], stdout=self.server_log_file, stderr=subprocess.STDOUT)
        time.sleep(1)

        self.web_url = 'http://localhost:8080/tsdb'
        self.web_log_file = open('.test_rest_api_web_log', 'w')
        self.web_proc = subprocess.Popen(['python', 'go_web.py'], stdout=self.web_log_file, stderr=subprocess.STDOUT)
        time.sleep(1)

    def tearDown(self):
        '''Method called immediately after the test method has been called and the result recorded.'''
        self.server_proc.terminate()
        self.server_log_file.close()

        self.web_proc.terminate()
        self.web_log_file.close()

    def test_add_trigger(self):
        data = json.dumps({'proc':'junk', 'onwhat':'insert_ts', 'target':None, 'arg':'db:one:ts'})
        response = requests.post(self.web_url+'/add_trigger', data)
        self.assertEqual(response.status_code, 200)

        data = json.dumps({'proc':'stats', 'onwhat':'insert_ts', 'target':['mean', 'std'], 'arg':None})
        r = requests.post(self.web_url+'/add_trigger', data)
        self.assertEqual(r.status_code, 200)

        #Set up 50 time series
        mus = np.random.uniform(low=0.0, high=1.0, size=50)
        sigs = np.random.uniform(low=0.05, high=0.4, size=50)
        jits = np.random.uniform(low=0.05, high=0.2, size=50)

        # dictionaries for time series and their metadata
        global tsdict
        global metadict
        tsdict={}
        metadict={}
        for i, m, s, j in zip(range(50), mus, sigs, jits):
            meta, tsrs = tsmaker(m, s, j)
            # the primary key format is ts-1, ts-2, etc
            pk = "ts-{}".format(i)
            tsdict[pk] = tsrs
            meta['vp'] = False # augment metadata with a boolean asking if this is a  VP.
            metadict[pk] = meta

        # choose 5 distinct vantage point time series
        global vpkeys
        vpkeys = ["ts-{}".format(i) for i in np.random.choice(range(50), size=5, replace=False)]
        for i in range(5):
            # add 5 triggers to upsert distances to these vantage points
            data = add_trigger_to_json('corr', 'insert_ts', ["d_vp-{}".format(i)], tsdict[vpkeys[i]])
            r = requests.post(self.web_url+'/add_trigger', data)
            self.assertEqual(r.status_code, 200)
            # change the metadata for the vantage points to have meta['vp']=True
            metadict[vpkeys[i]]['vp'] = True

    def test_insert_ts_and_upsert_meta(self):
        # Having set up the triggers, now insert the time series, and upsert the metadata
        # ==========================================
        # When it's first time to insert these keys in TSDB_server,
        # insert_ts will work and return TSDBStatus.OK
        # ==========================================
        for k in tsdict:
            data = json.dumps({'primary_key':k, 'ts':tsdict[k].to_json()})
            r = requests.post(self.web_url+'/insert_ts', data)
            self.assertEqual(r.status_code, 200)

            # upsert meta
            data = json.dumps({'primary_key':k, 'metadata_dict': metadict[k]})
            r = requests.post(self.web_url+'/add_metadata', data)
            self.assertEqual(r.status_code, 200)

        # ==========================================
        # However if it's not first time to insert these keys,
        # insert_ts will return TSDBStatus.INVALID_KEY
        # ==========================================

    def test_select(self):
        # ===============================
        # In go_client.py
        # SELECT test cases
        # ===============================
        # additional test
        # returned ts instances correctly
        params = '{"additional":{"sort_by":"-order"}}'
        r = requests.get(self.web_url+'/select?query='+params)
        self.assertEqual(r.status_code, 200)

        # order field test
        # returned ts instances correctly
        # to see : r.content
        params = '{"fields":["order"]}'
        r = requests.get(self.web_url+'/select?query='+params)
        self.assertEqual(r.status_code, 200)

    def test_augmented_select(self):
        #we first create a query time series.
        _, query = tsmaker(0.5, 0.2, 0.1)

        # Step 1: in the vpdist key, get  distances from query to vantage points
        # this is an augmented select
        vpdist = {}
        payload = {"proc":"corr", "target":"d", "arg":query.to_json()}
        for v in vpkeys:
            payload['where'] = {'pk': v}
            r = requests.get(self.web_url+'/augmented_select', {'query':json.dumps(payload)})
            results = json.loads(r.content.decode('utf-8'))
            vpdist[v] = results[v]['d']

        lowest_dist_vp = min(vpkeys, key=lambda v:vpdist[v])
        print(lowest_dist_vp)


if __name__ == '__main__':
    unittest.main()