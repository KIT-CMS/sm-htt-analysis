#!/usr/bin/env python3
# %%
import sys
import uproot
import re
import os


# %%


fn="~/p/bms3/repoAtTimeOfStage1p1Studies/sm-htt/output/shapes/2018-mc_mc_balMLfix-mt-synced-ML.root"
shape = uproot.open(fn)
r=re.compile(".*dy.*Shape.*")
matchingkeys=[key for key in shape.allkeys() if r.match(key.decode())]

for key in matchingkeys:
    val=shape[key]
    keystr=key.decode()
    newkeystr=keystr.replace("_dyShape", "_dyShape_Run2018")
    newkey=newkeystr.encode()
    print(keystr+ "-> "+keystr.replace("_dyShape", "_dyShape_Run2018"))
    shape[newkey]=val
