#!/usr/bin/env python
# -*- coding: utf-8 -*-


import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
import sys


if __name__ == "__main__":
    filename = sys.argv[1]
    print("[INFO] Print fit results from file {}.".format(filename))
    f = ROOT.TFile(filename)
    if f == None:
        raise Exception("[ERROR] File {} not found.".format(filename))

    tree = f.Get("limit")
    if tree == None:
        raise Exception("[ERROR] Tree {} not found in file {}.".format("limit", filename))
    num_entries = tree.GetEntries()

    pois = []
    for branch in tree.GetListOfBranches():
        name = branch.GetName()
        if name.startswith("r_"):
            pois.append(name)

    print
    for poi in pois:
        for i, ev in enumerate(tree):
            if i == 0:
                print("[INFO] Nominal fit: %s = %.2f"%(poi, getattr(ev, poi)))
            if i == 1:
                print("[INFO] Alternative fit: %s = %.2f"%(poi, getattr(ev, poi)))
        print

    nominal = None
    alternative = None
    for i, e in enumerate(tree):
        if i == 0:
            print("[INFO] Nominal fit: 2*deltaNLL = %.2f"%(2.0*e.deltaNLL))
            nominal = 2.0*e.deltaNLL
        if i == 1:
            print("[INFO] Alternative fit: 2*deltaNLL = %.2f"%(2.0*e.deltaNLL))
            alternative = 2.0*e.deltaNLL

    print("[INFO] Degrees of freedom: %u"%(len(pois)))
    print("[INFO] p-value taken from ROOT::Math::chisquared_cdf_c(alternative, NDOF-1): %.2f"%(ROOT.Math.chisquared_cdf_c(alternative, len(pois)-1)))
