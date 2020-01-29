#!/usr/bin/env python
# -*- coding: utf-8 -*-
# %%
import sys,os
import uproot
import numpy as np
import copy

# %%
p1=sys.argv[1]
p2=sys.argv[2]
print(sys.argv)

shapes=[uproot.open(p1),uproot.open(p2)]

GREEN='\x1b[6;30;42m'
RED='\x1b[0;30;41m'
END='\x1b[0m'

print("{} | {}".format(p1,p2))


###code for using renamed histogramms

replD={"htt_dyShape_Run2018":"htt_dyShape","data_obs":"data"}

keyLookUpDict=[{},{}]
def keyrep(key,shapeIdx):
    newkey=copy.deepcopy(key)
    for a,b in replD.items():
        if a in newkey:
            newkey=newkey.replace(a,b)
    keyLookUpDict[shapeIdx][newkey]=key
    return(newkey)


def lkUp(key,shapeIdx):
    return(shapes[shapeIdx][keyLookUpDict[shapeIdx][key]])


def filterhists (ks,shapeIdx):
    #ignoreS={"CMS_htt_dyShape"}
    ignoreS=set()
    ignoreS= ignoreS | {"CMS_scale_mc_t_1prong", "CMS_scale_mc_t_3prong"} # mc_tau energy scale added
    #{"CMS_eff_emb_t_","CMS_eff_t_","CMS_scale_mc_t_"}
    ## ignore double Hists
    ignoreS= ignoreS | {"Up;2","Down;2"}
    #ignoreS= ignoreS | {"Down;"} # ignore down shifts
    #ks = {key for key in ks if key.split("#")[-1]==";1"}
    ks =  {keyrep(key,shapeIdx) for key in ks if not any([pattern in key for pattern in ignoreS]) }
    return(ks)

keyset0=set(shapes[0].allkeys())
keyset1=set(shapes[1].allkeys())

keyset0 = filterhists(keyset0,0)
keyset1 = filterhists(keyset1,1)

diffkeys = sorted(set(keyset0) ^ set(keyset1))
print("[1/3] Number of differing keys {}".format(len(diffkeys)))

if len(diffkeys)!=0:
    print(GREEN+">"+END+": key in {} but not in {} ".format(p1,p2))
    print(RED+"<"+END+": key in {} but not in {} ".format(p2,p1))
    for key in sorted(diffkeys):
        if key in keyset0:
            print(GREEN+">"+END+" {key} >".format(key=key))
        else:
            print(RED+"<"+END+" {key} <".format(key=key))

samekeys = set(keyset0) & set(keyset1)





print("Nummer of identical keys: {}".format(len(samekeys)))
## check shapes for dublicate histograms
for key in sorted(samekeys):
    if key not in samekeys: continue
    for shapeIdx in [0,1]:
        if lkUp(key,shapeIdx).allvalues.sum()==0.0:continue
        samehist={ckey_ for ckey_ in samekeys if lkUp(key,shapeIdx)==lkUp(ckey_,shapeIdx) and key!=ckey_}
        if len(samehist):
            samekeys = samekeys - samehist
            print("Shape {}, Dublicate histamgrams to {} with sum {}:".format(shapeIdx, key, lkUp(key,shapeIdx).allvalues.sum()))
            for ckey_ in sorted(samehist):
                print("\t"+ckey_)
print("Dublicates removed")

print("Analysing Histogramm content")
for key in sorted(samekeys):
    arr1,bin1=lkUp(key,0).allnumpy()
    arr2,bin2=lkUp(key,1).allnumpy()
    arr1=np.round(arr1,decimals=4)
    arr2=np.round(arr2,decimals=4)
    if not np.array_equal(arr1,arr2) or not np.array_equal(bin1,bin2):
        print(RED+u"≠".encode('utf-8')+END+" {}".format(key))
        if not np.array_equal(bin1,bin2):
            print("binning different: \n {} \n vs. \n {}".format(key, bin1, bin2))
        else:
            #print("contents different: \n {} \n vs. \n {}".format(key, arr1, arr2))
            print("\tsum different: {}  vs. {}".format(arr1.sum(), arr2.sum()))
    else: print(GREEN+"="+END+" "+key)


# %%
