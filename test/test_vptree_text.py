from vp_tree.simple_vp import *
import time
import pylab as plt
from vp_tree.simple_vp import VpNode, VpSearch
import sys

def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


def main(file_name):

    f = open(file_name)
    f.next()
    aset = [w.strip() for w in f]
    rad = 4.4

    distance = levenshtein

    s = time.time()
    print("\ninput set %s points" % len(aset))
    print("creating tree...")
    root = VpNode(aset, distance=distance)
    print("created: %s nodes" % VpNode.ids)
    print("done in s: %s" % (time.time() - s))
    print("searching...")
    while True:
        q = input(">>")

        s = time.time()
        se = VpSearch(root, q, rad, 10)
        out = se.knn()
        print(se.stat)
        print("founded %s results" % len(out))
        print("done in s: %s" % (time.time() - s))
        print("\n".join(out))
        print


def test_search_text():
    try:
        main('../vp_tree/README.md')
    except:
        print("usage:\nvp_searchtxt.py <filename>")
        print("file name must be a column of words")
