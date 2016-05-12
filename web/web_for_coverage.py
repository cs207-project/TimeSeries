import requests
import json


class WebInterface:
    '''
    Similar to REST API web application,
    but to cover the coverage.
    '''

    def __init__(self):
        self.url = 'http://127.0.0.1:8080/tsdb/'

    def insert_ts(self, pk, ts):
        """
        Insert a timeseries into the database by sending a request to the server.

        Parameters
        ----------
        primary_key: int
            a unique identifier for the timeseries

        ts: a TimeSeries object
            the timeseries object intended to be inserted to database
        """

        if hasattr(ts, 'to_json'):
            ts = ts.to_json()
        payload = {'pk': pk, 'ts': ts}

        return self.request_post('insert_ts', payload)

    def delete_ts(self, pk):
        """
        Delete a timeseries from the database by sending a request to the server.

        Parameters
        ----------
        primary_key: int
            a unique identifier for the timeseries
        """

        msg = {'pk': pk}

        return self.request_post('delete_ts', msg)


    def upsert_meta(self, pk, md):
        """
        Upserting metadata into the timeseries in the database designated by the promary key by sending the server a request.

        Parameters
        ----------
        primary_key: int
            a unique identifier for the timeseries

        metadata_dict: dict
            the metadata to upserted into the timeseries
        """

        payload = {'pk': pk, 'md': md}
        return self.request_post('add_metadata', payload)

    def select(self, md={}, fields=None, additional=None):
        """
        Selecting timeseries elements in the database that match the criteria
        set in metadata_dict and return corresponding fields with additional
        features.

        Parameters
        ----------
        metadata_dict: dict
            the selection criteria (filters)
            (Options : 'blarg', 'order')

        fields: dict
            If not `None`, only these fields of the timeseries are returned.
            Otherwise, the timeseries are returned.

        additional: dict
            additional computation to perform on the query matches before they're
            returned. Currently provide "sort_by" and "limit" functionality

        """
        payload = {'md': md, 'fields': fields, 'additional': additional}
        return self.request_get('select', payload)

    def augmented_select(self, proc, target, arg=None, md={}, additional=None):
        """
        Parameters
        ----------
        proc : enum
            which of the modules in procs,
            or name of module in procs with coroutine main.
            (Options: 'corr', 'junk', 'stats')
        target : array of fieldnames
            will be mapped to the array of results from the coroutine.
            If the target is None rather than a list of fields, we'll assume no upserting
        arg : additional argument
            (ex : Timeseries object)
        metadata_dict : dict
                        store info for TimeSeries other than TimeSeries object itself
                        (ex. vantage point is metadata_dict['ts-14']['vp']
        additional : dict
                    (Options: {"sort_by":"-order"})

        Returns
        -------
        tsdb status & payload
        """
        if hasattr(arg, 'to_json'):
            arg = arg.to_json()
        payload = {'proc': proc, 'target': target, 'arg': arg, 'md': md, 'additional': additional}

        return self.request_get('augmented_select', payload)


    def add_trigger(self, proc, onwhat, target, arg=None):
        """
        Send the server a request to add a trigger.

        Parameters
        ----------
        `proc` : enum
            which of the modules in procs,
            or name of module in procs with coroutine main.
            (Options: 'corr', 'junk', 'stats')
        `onwhat` :
            which op is this trigger running on
            (ex : "insert_ts")
        `target` : array of fieldnames
            will be mapped to the array of results from the coroutine.
            If the target is None rather than a list of fields, we'll assume no upserting
        `arg` :
            additional argument
            (ex : Timeseries object)
        """

        payload = {'proc': proc, 'onwhat': onwhat, 'target': target, 'arg': arg}

        return self.request_post('add_trigger', payload)

    def remove_trigger(self, proc, onwhat, target=None):

        payload = {'proc': proc, 'onwhat': onwhat, 'target': target}


        return self.request_post('remove_trigger', payload)

    def request_get(self, handler, payload):
        try:
            r = requests.get(self.url + handler, data={'query':json.dumps(payload)})
            return r.status_code
        except:
            return json.loads('Could not proceed the GET REQUEST')

    def request_post(self, handler, payload):
        try:
            r = requests.post(self.url + handler, data=json.dumps(payload))
            return r.status_code
        except:
            return json.loads('Could not proceed the POST REQUEST')