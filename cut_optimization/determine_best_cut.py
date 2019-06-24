import ROOT as r
import re
import math
import os
from matplotlib import pyplot as plt

def sorted_nicely(l):
    """ Sort the given iterable in the way that humans expect: alphanumeric sort (in bash, that's 'sort -V')"""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


def sorted_cats(l):
    return sorted(l,key = lambda k : [float(k.replace(k.split("-")[0],"").replace("-less-","").replace("-greater-","").replace("p","."))]  )

f = r.TFile("counts_for_soverb.root","read")
t = f.Get("output_tree")
t.GetEntry(0)

counts =  [k.GetName() for k in t.GetListOfLeaves() if "_FF" not in k.GetName() and "_ss" not in k.GetName() and "data_obs" not in k.GetName()]

variables = sorted_nicely(set([k.strip("#").split("#")[1].split("-")[0] for k in counts]))

processes = sorted_nicely(set([k.strip("#").split("#")[2] for k in counts]))

categories_less = {}
categories_greater = {}
cutvalues = {}
for var in variables:
    categories_less[var] = sorted_cats(set([k.strip("#").split("#")[1] for k in counts if "less" in k and var  == k.strip("#").split("#")[1].split("-")[0]] ))
    categories_greater[var] = sorted_cats(set([k.strip("#").split("#")[1] for k in counts if "greater" in k and var == k.strip("#").split("#")[1].split("-")[0]]))
    cutvalues[var] = [float(k.replace(k.split("-")[0],"").replace("-less-","").replace("p",".")) for k in categories_less[var]]
    print var
    for cl,cg,val in zip(categories_less[var],categories_greater[var],cutvalues[var]):
        print "\t",cl,cg,val
    print "-------------------"

backgrounds = [p for p in processes if "H125" not in p]
signals = [p for p in processes if "H125" in p]

yields_dict = {}

for c in counts:
    cat = c.strip("#").split("#")[1]
    process = c.strip("#").split("#")[2]
    yields_dict.setdefault(cat,{})
    yields_dict[cat][process] = getattr(t,c)
    if process in backgrounds:
        yields_dict[cat].setdefault("BG",0.0)
        yields_dict[cat]["BG"] += getattr(t,c)


soverb_dict = {}

for var in variables:
    for cg, cl in zip(categories_greater[var],categories_less[var]):
        soverb_dict.setdefault(var,{"greater" : [], "less" : []})
        denominator = math.sqrt(yields_dict[cg]["qqH125"] + yields_dict[cg]["BG"])
        if denominator > 0:
            soverb_greater = yields_dict[cg]["qqH125"]/denominator
        else:
            soverb_greater = 0
        denominator = math.sqrt(yields_dict[cl]["qqH125"] + yields_dict[cl]["BG"])
        if denominator > 0:
            soverb_less = yields_dict[cl]["qqH125"]/denominator
        else:
            soverb_less = 0
        soverb_dict[var]["greater"].append(soverb_greater)
        soverb_dict[var]["less"].append(soverb_less)


if not os.path.exists("cutscans"):
    os.mkdir("cutscans")

for var in soverb_dict:
    plt.clf()
    plt.plot(cutvalues[var], soverb_dict[var]["greater"], color='r',label='greater')
    plt.plot(cutvalues[var], soverb_dict[var]["less"], color='b',label='less')
    plt.legend()
    plt.savefig("cutscans/%s_soverb_cutscan.png"%var)
