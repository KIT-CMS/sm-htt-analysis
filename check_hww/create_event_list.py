import ROOT as r
import json
import numpy as np
import sys
import os

fname = sys.argv[1]
f = r.TFile.Open(fname)
channel = fname.split("/")[1].split("_")[1]

outfolder = "eventlist_hww_vs_htt"
if not os.path.exists(outfolder):
    os.makedirs(outfolder)

datatree = f.Get("data_obs")

eventlist = []

for entry in datatree:
    eventlist.append((entry.run, entry.lumi, entry.event))

eventlist = sorted(eventlist)

out = open(os.path.join(outfolder,"eventlist_%s.txt"%channel), "w")
for event in eventlist:
    out.write("{} {} {}\n".format(event[0], event[1], event[2]))
