import coverage
import timeseries as ts
import subprocess
import time
import numpy as np
import requests
import json
from scipy.stats import norm

coverage.process_startup()

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


def setUp():
    '''Method or coroutine called to prepare the test fixture.'''
    global server_proc
    server_proc = subprocess.Popen(['python', 'go_server.py'])
    time.sleep(1)

    global web_url, web_proc
    web_url = 'http://localhost:8080/tsdb'
    web_proc = subprocess.Popen(['python', 'go_web.py'])
    time.sleep(1)

def tearDown():
    '''Method called immediately after the test method has been called and the result recorded.'''
    server_proc.terminate()
    web_proc.terminate()

def test_total():
    setUp()

    data = json.dumps({'proc':'junk', 'onwhat':'insert_ts', 'target':None, 'arg':'db:one:ts'})
    response = requests.post(web_url+'/add_trigger', data)
    assert(response.status_code == 200)

    data = json.dumps({'proc':'stats', 'onwhat':'insert_ts', 'target':['mean', 'std'], 'arg':None})
    r = requests.post(web_url+'/add_trigger', data)
    assert(r.status_code == 200)


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
        data = json.dumps({'proc':'corr', 'onwhat':'insert_ts', 'target':["d_vp-{}".format(i)], 'arg':tsdict[vpkeys[i]].to_json()})
        r = requests.post(web_url+'/add_trigger', data)
        assert(r.status_code == 200)
        # change the metadata for the vantage points to have meta['vp']=True
        metadict[vpkeys[i]]['vp'] = True

    # Having set up the triggers, now insert the time series, and upsert the metadata
    # ==========================================
    # When it's first time to insert these keys in TSDB_server,
    # insert_ts will work and return TSDBStatus.OK
    # ==========================================
    for k in tsdict:
        data = json.dumps({'primary_key':k, 'ts':tsdict[k].to_json()})
        r = requests.post(web_url+'/insert_ts', data)
        assert(r.status_code == 200)

        # upsert meta
        data = json.dumps({'primary_key':k, 'metadata_dict': metadict[k]})
        r = requests.post(web_url+'/add_metadata', data)
        assert(r.status_code == 200)

#     # ==========================================
#     # However if it's not first time to insert these keys,
#     # insert_ts will return TSDBStatus.INVALID_KEY
#     # ==========================================
#
#
#
#     # ===============================
#     # In go_client.py
#     # SELECT test cases
#     # ===============================
#     # additional test
#     # returned ts instances correctly
#     params = '{"additional":{"sort_by":"-order"}}'
#     r = requests.get(web_url+'/select?query='+params)
#     assert(r.status_code == 200)
#
#     # order field test
#     # returned ts instances correctly
#     # to see : r.content
#     params = '{"fields":["order"]}'
#     r = requests.get(web_url+'/select?query='+params)
#     assert(r.status_code == 200)
#
#
#     #we first create a query time series.
#     _, query = tsmaker(0.5, 0.2, 0.1)
#
#     # Step 1: in the vpdist key, get  distances from query to vantage points
#     # this is an augmented select
#     vpdist = {}
#     payload = {"proc":"corr", "target":"d", "arg":query.to_json()}
#     for v in vpkeys:
#         print("v", v)
#         payload['where'] = {'pk': v}
#         r = requests.get(web_url+'/augmented_select', {'query':json.dumps(payload)})
#         print("aug_select r content", r.content)
#         results = json.loads(r.content.decode('utf-8'))
#         vpdist[v] = results[v]['d']
#
#     lowest_dist_vp = min(vpkeys, key=lambda v:vpdist[v])
#     print(lowest_dist_vp)
#
#     tearDown()


# def test_insert_ts_and_upsert_meta(self):
#     # Having set up the triggers, now insert the time series, and upsert the metadata
#     # ==========================================
#     # When it's first time to insert these keys in TSDB_server,
#     # insert_ts will work and return TSDBStatus.OK
#     # ==========================================
#     for k in tsdict:
#         data = json.dumps({'primary_key':k, 'ts':tsdict[k].to_json()})
#         r = requests.post(web_url+'/insert_ts', data)
#         assertEqual(r.status_code, 200)
#
#         # upsert meta
#         data = json.dumps({'primary_key':k, 'metadata_dict': metadict[k]})
#         r = requests.post(web_url+'/add_metadata', data)
#         assertEqual(r.status_code, 200)
#
#     # ==========================================
#     # However if it's not first time to insert these keys,
#     # insert_ts will return TSDBStatus.INVALID_KEY
#     # ==========================================
#
# def test_select(self):
#     # ===============================
#     # In go_client.py
#     # SELECT test cases
#     # ===============================
#     # additional test
#     # returned ts instances correctly
#     params = '{"additional":{"sort_by":"-order"}}'
#     r = requests.get(web_url+'/select?query='+params)
#     assertEqual(r.status_code, 200)
#
#     # order field test
#     # returned ts instances correctly
#     # to see : r.content
#     params = '{"fields":["order"]}'
#     r = requests.get(web_url+'/select?query='+params)
#     assertEqual(r.status_code, 200)
#
# def test_augmented_select_and_delete_ts(self):
#     #we first create a query time series.
#     _, query = tsmaker(0.5, 0.2, 0.1)
#
#     # Step 1: in the vpdist key, get  distances from query to vantage points
#     # this is an augmented select
#     vpdist = {}
#     payload = {"proc":"corr", "target":"d", "arg":query.to_json()}
#     for v in vpkeys:
#         print("v", v)
#         payload['where'] = {'pk': v}
#         r = requests.get(web_url+'/augmented_select', {'query':json.dumps(payload)})
#         print("aug_select r content", r.content)
#         results = json.loads(r.content.decode('utf-8'))
#         vpdist[v] = results[v]['d']
#
#     lowest_dist_vp = min(vpkeys, key=lambda v:vpdist[v])
#     print(lowest_dist_vp)
#
# def test_delete_ts(self):
#     pass
#     # just try to delete 'ts-99' for test
#     # don't check like this. Just compare the dictDB case.
#     # r = requests.post(web_url+'/delete_ts', json.dumps({'primary_key':'ts-99'}))
#     # print("status", r.status_code)
#     # print("content", r.content)
#     # assertEqual(r.status_code, 200)