#!/usr/bin/env python3
import sys
import uproot
import re
import os
if not os.path.isfile(sys.argv[1]):
    print("No such file: "+sys.argv[1])
    exit(1)
shape = uproot.open(sys.argv[1])
key=sys.argv[2]

r=re.compile(sys.argv[2])
matchingkeys=[key for key in shape.allkeys() if r.match(key.decode())]

def printE(e):
    if str(type(e))=="<class 'uproot.rootio.TH1D'>":
        print(e.values)
        ##new uproot
        if len(e.bins[0])==2:
            print([e.bins[0][0]]+[x[1] for x in e.bins])
        #old uproot
        else:
            print(e.bins)
    else:
        print(type(e))

for key in matchingkeys:
    val=shape[key]
    print(key)
    printE(val)
