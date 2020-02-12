#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# %%
import sys
import os
import uproot
import numpy as np
import copy
from multiprocessing import Pool

### to use this, dont source a lcg, just use python3 and pip3 install --user uproot

nCores = 10
p1 = sys.argv[1]
p2 = sys.argv[2]

shapes = [uproot.open(p1), uproot.open(p2)]

GREEN = '\x1b[6;30;42m'
RED = '\x1b[0;30;41m'
END = '\x1b[0m'

print("{} | {}".format(p1, p2))

# code for using renamed histogramms

replD = {
    "htt_dyShape_Run2018": "htt_dyShape",
    "data_obs": "data",
    "TTTT": "TTT"
}

keyLookUpDict = [{}, {}]


def keyrep(key, shapeIdx):
    newkey = copy.deepcopy(key)
    for a, b in replD.items():
        if a in newkey:
            newkey = newkey.replace(a, b)
    keyLookUpDict[shapeIdx][newkey] = key
    return (newkey)


def lkUp(key, shapeIdx):
    k_ = keyLookUpDict[shapeIdx][key].encode()
    return (shapes[shapeIdx][k_])


def filterhists(ks, shapeIdx):
    ignoreS = {"output_tree;1"}
    ignoreS = ignoreS | {"CMS_scale_mc_t_1prong", "CMS_scale_mc_t_3prong"
                         }  # mc_tau energy scale added
    # ignore double Hists
    ignoreS = ignoreS | {"Up;2", "Down;2"}
    ## current shapes errors
    #ignoreS = ignoreS | {"CMS_prefiring", "CMS_eff_trigger", "CMS_eff_xtrigger", "_boson_", "#qqHWW125#", "#ggHWW125#"}

    # ignoreS= ignoreS | {"Down;"} # ignore down shifts
    # ks = {key for key in ks if key.split("#")[-1]==";1"}
    ks = {
        keyrep(key.decode(), shapeIdx)
        for key in ks
        if not any([pattern in key.decode() for pattern in ignoreS])
    }
    return (ks)


keyset0 = set(shapes[0].allkeys())
keyset1 = set(shapes[1].allkeys())
keyCount = [len(keyset0), len(keyset1)]
keyset0 = filterhists(keyset0, 0)
keyset1 = filterhists(keyset1, 1)
print("keycount after filtering {}".format(keyCount))

diffkeys = sorted(set(keyset0) ^ set(keyset1))
print("[1/3] Number of differing keys after renaming {}".format(len(diffkeys)))

if len(diffkeys) != 0:
    print(GREEN + ">" + END + ": key in {} but not in {} ".format(p1, p2))
    print(RED + "<" + END + ": key in {} but not in {} ".format(p2, p1))
    for key in sorted(diffkeys):
        if key in keyset0:
            print(GREEN + ">" + END + " {key} >".format(key=key))
        else:
            print(RED + "<" + END + " {key} <".format(key=key))

samekeys = set(keyset0) & set(keyset1)
keyCount = len(samekeys)
print("[1/3] DONE")

print("Computing Integral")
integrals = []


def getIntegral0(key):
    return ((key, lkUp(key, 0).allvalues.sum()))


def getIntegral1(key):
    return ((key, lkUp(key, 1).allvalues.sum()))


with Pool(nCores) as p:
    integrals.append(dict(p.map(getIntegral0, samekeys)))
    integrals.append(dict(p.map(getIntegral1, samekeys)))

# check shapes for dublicate histograms
print("Nummer of identical keys after renaming: {}. Looking for duplicates".
      format(keyCount))
print("[2/3] START Looking for duplicates".format(len(samekeys)))

for key in sorted(samekeys):
    if key not in samekeys:
        continue
    samehists = [set(), set()]
    for shapeIdx in [0, 1]:
        #prefilter the keys with calculated integrals
        samehistcandidates = {
            ckey_
            for ckey_ in samekeys
            if integrals[shapeIdx][key] == integrals[shapeIdx][ckey_]
            and key != ckey_
        }
        #check if the actuall bin contents are the same
        samehists[shapeIdx] = {
            ckey_
            for ckey_ in samehistcandidates
            if lkUp(key, shapeIdx) == lkUp(ckey_, shapeIdx)
        }
        if len(samehists[shapeIdx]):
            print("Shape {}, Dublicate histamgrams to {} with sum {}:".format(
                shapeIdx, key,
                lkUp(key, shapeIdx).allvalues.sum()))
            for ckey_ in sorted(samehists[shapeIdx]):
                print("\t" + ckey_)
        # if keys hold the same histogram duplicate for both shapes, remove them from the set of keys, that we need to compare
        samekeys = samekeys - (samehists[0] & samehists[1])

print("[2/3] DONE")
print("{} duplicates removed. Remaining:".format(keyCount - len(samekeys),
                                                 len(samekeys)))

print("[3/3] Analysing Histogramm content")


def compareHists(key):
    if isinstance(key, bytes):
        print(key)
        raise Exception
    retstr = ""
    try:
        arr1, bin1 = lkUp(key, 0).allnumpy()
        arr2, bin2 = lkUp(key, 1).allnumpy()
    except AttributeError:
        print(key)
        exit(1)
    arr1 = np.round(arr1, decimals=4)
    arr2 = np.round(arr2, decimals=4)
    if not np.array_equal(arr1, arr2) or not np.array_equal(bin1, bin2):
        retstr += RED + "≠" + END + " {}\n".format(key)
        if not np.array_equal(bin1, bin2):
            retstr += "binning different:\n {} vs. {}\n".format(
                bin1, bin2)
        else:
            retstr += "sum different: {}  vs. {}\n".format(
                arr1.sum(), arr2.sum())
    return (retstr)


with Pool(nCores) as p:
    res = p.map(compareHists, samekeys)
for r in sorted(filter(lambda x: x != "", res)):
    print(r)
print("[3/3] DONE")