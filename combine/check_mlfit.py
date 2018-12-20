#!/usr/bin/env python
# -*- coding: utf-8 -*-


import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
import sys


if __name__ == "__main__":
    filename = sys.argv[1]
    print("[INFO] Check fits from file {}.".format(filename))
    f = ROOT.TFile(filename)

    for name in ["fit_s", "fit_b"]:
        fit = f.Get(name)
        if fit == None:
            raise Exception("[ERROR] {} not found in file {}.".format(name, filename))
        status = fit.status()
        if status == 0:
            print("[INFO] Fit {} from file {} is ok.".format(name, filename))
        else:
            raise Exception("[ERROR] Fit {} from file {} is invalid.".format(name, filename))
