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

    indices = {}
    count = 1
    results = {}
    for key in tree.GetListOfBranches():
        name = key.GetName()
        if name.startswith("r"):
            indices[name] = count
            count += 2
            results[name] = [-999, -999, -999]

    for i, row in enumerate(tree):
        for name in indices:
            if i == 0:
                results[name][0] = getattr(row, name)
            elif i == indices[name]:
                results[name][1] = getattr(row, name)
            elif i == indices[name]+1:
                results[name][2] = getattr(row, name)

    for name in results:
        r = results[name][0]
        d = results[name][1]
        u = results[name][2]
        print("[INFO] {0:<30}: {1:.4f} {2:.4f} +{3:.4f}".format(name, r, d-r, u-r))
