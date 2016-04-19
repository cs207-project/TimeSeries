#!/usr/bin/env python3
from tsdb import TSDBClient
import timeseries as ts

def main():
    client = TSDBClient()


    client.insert_ts('one',ts.TimeSeries([1, 2, 3],[1, 4, 9]))
    client.insert_ts('two',ts.TimeSeries([2, 3, 4],[4, 9, 16]))
    client.insert_ts('three',ts.TimeSeries([9,3,4],[4,0,16]))
    client.insert_ts('four',ts.TimeSeries([0,0,4],[1,0,4]))

    client.upsert_meta('one', {'order': 1, 'blarg': 1})
    client.upsert_meta('two', {'order': 2})
    client.upsert_meta('three', {'order': 1, 'blarg': 2})
    client.upsert_meta('four', {'order': 2, 'blarg': 2})
    client.select()
    client.select({'order': 1})
    client.select({'blarg': 1})
    bla = client.select({'order': 1, 'blarg': 2})
    print("END", bla)



if __name__=='__main__':
    main()
