#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
import argparse
import numpy as np


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fix binning of unrolled em shapes.")
    parser.add_argument("input", type=str, help="Path to input shapes.")
    return parser.parse_args()


def main(args):
    f = ROOT.TFile(args.input, "UPDATE")
    for key in f.GetListOfKeys():
        dirname = key.GetName()
        d = f.Get(dirname)
        f.cd(dirname)
        if not "unrolled" in dirname:
            continue
        for key2 in d.GetListOfKeys():
            name = key2.GetName()
            title = key2.GetName()
            h = d.Get(name)
            num_bins = h.GetNbinsX()
            x = np.array(range(10, 101, 5))/100.
            x[0] = 0.125
            bins = [x[0]]
            offset = x[-1]-x[0]
            if num_bins == 18*11: # ggh (with 101 and 102)
                num_unrolling = 9 # unrolling without 101 and 102
            elif num_bins == 18*5: # qqh
                num_unrolling = 5
            else:
                raise Exception("2D binning does not match ggh or qqh.")
            for i in range(num_unrolling):
                for j in range(1,len(x)):
                    bins.append(x[j]+offset*i)
            v = ROOT.std.vector("double")(len(bins))
            for i, c in enumerate(bins):
                v[i] = c
            hnew = ROOT.TH1D(name, title, len(bins)-1, v.data())
            if num_unrolling == 9: # copy for ggh and leave out first two slices
                offset = 2*18 + 1
                for i in range(offset, num_bins+1):
                    hnew.SetBinContent(i-offset+1, h.GetBinContent(i));
                    hnew.SetBinError(i-offset+1, h.GetBinError(i));
            else: # copy for qqh
                for i in range(1, num_bins+1):
                    hnew.SetBinContent(i, h.GetBinContent(i));
                    hnew.SetBinError(i, h.GetBinError(i));
            hnew.SetEntries(h.GetEntries())
            hnew.Write()
    f.Write()
    f.Close()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
