#!/usr/bin/env python
import sys
import uproot
import re
# %%

shape = uproot.open(sys.argv[1])
key=sys.argv[2]

r=re.compile(sys.argv[2])
matchingkeys=[key for key in shape.allkeys() if r.match(key) or r.match(key.encode())]

for key in matchingkeys:
    hist=shape[key]
    print(key)
    print(hist.values)
    ##new uproot
    if len(hist.bins[0])==2:
        print([hist.bins[0][0]]+[x[1] for x in hist.bins])
    #old uproot
    else:
        print(hist.bins)
