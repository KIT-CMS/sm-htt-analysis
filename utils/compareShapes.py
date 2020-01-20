# %%
import sys,os
import uproot
import numpy as np

# %%
p1=sys.argv[0]
p2=sys.argv[1]
shape1 = uproot.open(os.path.expanduser(p1))
shape2 = uproot.open(os.path.expanduser(p2))

# %%
print("{} | {}".format(p1,p2))
print("<: key in {} but not in {} ".format(p1,p2))
print(">: key in {} but not in {} ".format(p2,p1))
diffkeys = set(shape1.allkeys()) ^ set(shape2.allkeys())
samekeys = set(shape1.allkeys()) | set(shape2.allkeys())
if len(diffkeys)==0:
    print("Keys are the same")
else:
    for key in diffkeys:
        if key in shape1.allkeys():
            print("{key} <".format(key=key))
        else:
            print("{key} >".format(key=key))

# %%
print("Analysing Histogramm content")
for key in samekeys:
    arr1,bin1=shape1[key].allnumpy()
    arr2,bin2=shape2[key].allnumpy()
    if any(arr1==arr2 ) or any(bin1!=bin2):
        if any(bin1!=bin2):
            print("{} \n binning different: \n {} \n vs. \n {}".format(key, bin1, bin2))
            print("{} \n binning different: \n {} \n vs. \n {}".format(key, bin1, bin2))
        else:
            print("{} \n contents different: \n {} \n vs. \n {}".format(key, arr1, arr2))


# %%
