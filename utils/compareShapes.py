#!/usr/bin/env python
# %%
import sys,os
import uproot
#  import numpy as np

# %%
p1=sys.argv[1]
p2=sys.argv[2]
print(sys.argv)
shape1 = uproot.open(p1)
shape2 = uproot.open(p2)

GREEN='\x1b[6;30;42m'
RED='\x1b[0;30;41m'
END='\x1b[0m'

# %%
print("{} | {}".format(p1,p2))
print(GREEN+">"+END+": key in {} but not in {} ".format(p1,p2))
print(RED+"<"+END+": key in {} but not in {} ".format(p2,p1))
diffkeys = sorted(set(shape1.allkeys()) ^ set(shape2.allkeys()))
samekeys = sorted(set(shape1.allkeys()) & set(shape2.allkeys()))
if len(diffkeys)==0:
    print("Keys are the same")
else:
    for key in diffkeys:
        if key in shape1.allkeys():
            print(GREEN+">"+END+" {key} >".format(key=key))
        else:
            print(RED+"<"+END+" {key} <".format(key=key))
{} + []
# %%
print("Analysing Histogramm content")
for key in samekeys:
    arr1,bin1=shape1[key].allnumpy()
    arr2,bin2=shape2[key].allnumpy()
    if any(arr1==arr2 ) or any(bin1!=bin2):
        if any(bin1!=bin2):
            print("{} \n binning different: \n {} \n vs. \n {}".format(key, bin1, bin2))
        else:
            print("{} \n contents different: \n {} \n vs. \n {}".format(key, arr1, arr2))


# %%
