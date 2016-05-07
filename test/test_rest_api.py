#!/usr/bin/env python3
import timeseries as ts
import subprocess
import time
import unittest
import numpy as np
import requests
import json
from scipy.stats import norm

NUMVPS = 5



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

def insert_ts_to_json(primary_key, ts):
    return json.dumps({'primary_key':primary_key, 'ts':ts.to_json()})

def upsert_meta_to_json(primary_key, metadata_dict):
    return json.dumps({'primary_key':primary_key, 'metadata_dict': metadata_dict})

def add_trigger_to_json(proc, onwhat, target, arg):
    if hasattr(arg, 'to_json'):
        arg = arg.to_json()
    return json.dumps({'proc':proc, 'onwhat':onwhat, 'target':target, 'arg':arg})

def make_remove_trigger(proc, onwhat):
    return json.dumps({'proc':proc,'onwhat':onwhat})

class RestApiTest(unittest.TestCase):
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

    def test_main(self):
        # add a trigger. notice the argument. It does not do anything here but
        # could be used to save a shlep of data from client to server.
        data = add_trigger_to_json('junk', 'insert_ts', None, 'db:one:ts')
        response = requests.post(self.web_url+'/add_trigger', data)
        self.assertEqual(response.status_code, 200)

        data = add_trigger_to_json('stats', 'insert_ts', ['mean', 'std'], None)
        r = requests.post(self.web_url+'/add_trigger', data)
        self.assertEqual(r.status_code, 200)


        #Set up 50 time series
        mus = np.random.uniform(low=0.0, high=1.0, size=50)
        sigs = np.random.uniform(low=0.05, high=0.4, size=50)
        jits = np.random.uniform(low=0.05, high=0.2, size=50)

        # dictionaries for time series and their metadata
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
        vpkeys = ["ts-{}".format(i) for i in np.random.choice(range(50), size=5, replace=False)]
        for i in range(5):
            # add 5 triggers to upsert distances to these vantage points
            data = add_trigger_to_json('corr', 'insert_ts', ["d_vp-{}".format(i)], tsdict[vpkeys[i]])
            requests.post(self.web_url+'/add_trigger', data)
            # change the metadata for the vantage points to have meta['vp']=True
            metadict[vpkeys[i]]['vp'] = True
        # Having set up the triggers, now insert the time series, and upsert the metadata
        for k in tsdict:
            data = insert_ts_to_json(k, tsdict[k])
            requests.post(self.web_url+'/insert_ts', data)
            data = upsert_meta_to_json(k, metadict[k])
            requests.post(self.web_url+'/add_metadata', data)

        # ===============================
        # In go_clinet.py
        # SELECT test cases
        # ===============================
        # client.select()
        # test = {'query':{}} <- this one works
        params = '{"additional":{"sort_by":"-order"}}'
        print(params)
        r = requests.get(self.web_url+'/select?query='+params)
        print(r.url)
        print(r.content)
        # #we first create a query time series.
        # _, query = tsmaker(0.5, 0.2, 0.1)
        #
        # # Step 1: in the vpdist key, get  distances from query to vantage points
        # # this is an augmented select
        # vpdist = {}
        # payload = {'proc':'corr','target':'d','arg':query.to_json()}
        # for v in vpkeys:
        #     payload['where'] = {'pk': v}
        #     r = requests.get(self.server_url+'/augselect',params={'query':json.dumps(payload)})
        #     results = json.loads(r.content.decode('utf-8'))
        #     vpdist[v] = results[v]['d']
        #
        # closest_vpk = min(vpkeys,key=lambda v:vpdist[v])
        #
        # # Step 2: find all time series within 2*d(query, nearest_vp_to_query)
        # #this is an augmented select to the same proc in correlation
        # payload = {'proc':'corr','target':'d','arg':query.to_json()}
        # payload['where'] = {'d_'+closest_vpk: {'<=': 2*vpdist[closest_vpk]}}
        # r = requests.get(self.server_url+'/augselect',params={'query':json.dumps(payload)})
        # results = json.loads(r.content.decode('utf-8'))
        #
        # #2b: find the smallest distance amongst this ( or k smallest)
        # #you can do this in local code
        # nearestwanted = min(results.keys(),key=lambda p: results[p]['d'])
        #
        # self.assertEqual(nearestwanted,'ts-35')

if __name__ == '__main__':
    unittest.main()



# class RestApiTest(unittest.TestCase):
#     def setUp(self):
#         '''Method or coroutine called to prepare the test fixture.'''
#         self.server_log_file = open('.test_rest_api_server_log', 'w')
#         self.server_proc = subprocess.Popen(['python', 'go_server.py'], stdout=self.server_log_file, stderr=subprocess.STDOUT)
#         print("popen go server")
#         time.sleep(10)
#
#         self.web_url = 'http://localhost:8080/tsdb'
#         self.web_log_file = open('.test_rest_api_web_log', 'w')
#         self.web_proc = subprocess.Popen(['python', 'go_web.py'], stdout=self.web_log_file, stderr=subprocess.STDOUT)
#         print("P oepn go web")
#         time.sleep(10)
#
#     # def tearDown(self):
#     #     '''Method called immediately after the test method has been called and the result recorded.'''
#     #     self.server_proc.terminate()
#     #     self.server_log_file.close()
#     #
#     #     self.web_proc.terminate()
#     #     self.web_log_file.close()
#
#     def test_addTrigger(self):
#         data = self.add_trigger_to_json('junk', 'insert_ts', None, 'db:one:ts')
#         response = requests.post(self.web_url+'/add_trigger', data)
#         print("did i come to trigger?")
#         self.assertEqual(response.status_code, 200)
#
#     def add_trigger_to_json(self, proc, onwhat, target, arg):
#         # arg is mostly ts
#         if hasattr(arg, 'to_json'):
#             arg = arg.to_json()
#         return json.dumps({'proc':proc, 'onwhat':onwhat, 'target':target, 'arg':arg})
#
#     def test_main(self):
#         pass
#         # r = requests.get(self.web_url+'/select?query={}')
#         # response = requests.post(self.web_url+'/add_trigger', data)
#         # self.assertEqual(response.status_code, 200)
#         #
#         # r = requests.post(self.web_url+'/add/trigger',make_add_trigger(
#         #                         'stats', 'insert_ts', ['mean', 'std'], None))
#         # self.assertEqual(r.status_code, 200)
#         # np.random.seed(12345)
#         # N_ts = 50
#         # N_vp = NUMVPS
#         #
#         # #Set up 50 time series
#         # mus = np.random.uniform(low=0.0, high=1.0, size=N_ts)
#         # sigs = np.random.uniform(low=0.05, high=0.4, size=N_ts)
#         # jits = np.random.uniform(low=0.05, high=0.2, size=N_ts)
#         #
#         # # dictionaries for time series and their metadata
#         # tsdict={}
#         # metadict={}
#         # for i, m, s, j in zip(range(N_ts), mus, sigs, jits):
#         #     meta, tsrs = tsmaker(m, s, j)
#         #     # the primary key format is ts-1, ts-2, etc
#         #     pk = "ts-{}".format(i)
#         #     tsdict[pk] = tsrs
#         #     meta['vp'] = False # augment metadata with a boolean asking if this is a  VP.
#         #     metadict[pk] = meta
#         #
#         # # choose 5 distinct vantage point time series
#         # vpkeys = ["ts-{}".format(i) for i in np.random.choice(range(N_ts), size=N_vp, replace=False)]
#         # for i in range(N_vp):
#         #     # add 5 triggers to upsert distances to these vantage points
#         #     requests.post(self.web_url+'/add/trigger',
#         #                   make_add_trigger('corr', 'insert_ts', ["d_vp-{}".format(i)], tsdict[vpkeys[i]]))
#         #     # change the metadata for the vantage points to have meta['vp']=True
#         #     metadict[vpkeys[i]]['vp']=True
#         # # Having set up the triggers, now inser the time series, and upsert the metadata
#         # for k in tsdict:
#         #     requests.post(self.web_url+'/add/ts',
#         #                   make_insert_ts(k, tsdict[k]))
#         #     requests.post(self.web_url+'/add/metadata',
#         #                   make_upsert_meta(k, metadict[k]))
#         #
#         # #we first create a query time series.
#         # _, query = tsmaker(0.5, 0.2, 0.1)
#         #
#         # # Step 1: in the vpdist key, get  distances from query to vantage points
#         # # this is an augmented select
#         # vpdist = {}
#         # payload = {'proc':'corr','target':'d','arg':query.to_json()}
#         # for v in vpkeys:
#         #     payload['where'] = {'pk': v}
#         #     r = requests.get(self.web_url+'/augselect',params={'query':json.dumps(payload)})
#         #     results = json.loads(r.content.decode('utf-8'))
#         #     vpdist[v] = results[v]['d']
#         #
#         # closest_vpk = min(vpkeys,key=lambda v:vpdist[v])
#         #
#         # # Step 2: find all time series within 2*d(query, nearest_vp_to_query)
#         # #this is an augmented select to the same proc in correlation
#         # payload = {'proc':'corr','target':'d','arg':query.to_json()}
#         # payload['where'] = {'d_'+closest_vpk: {'<=': 2*vpdist[closest_vpk]}}
#         # r = requests.get(self.web_url+'/augselect',params={'query':json.dumps(payload)})
#         # results = json.loads(r.content.decode('utf-8'))
#         #
#         # #2b: find the smallest distance amongst this ( or k smallest)
#         # #you can do this in local code
#         # nearestwanted = min(results.keys(),key=lambda p: results[p]['d'])
#         #
#         # self.assertEqual(nearestwanted,'ts-35')
#
# if __name__ == '__main__':
#     unittest.main()
