#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
import argparse
import glob
import os
import re
import json

def sorted_nicely(l):
    """ Sort the given iterable in the way that humans expect: alphanumeric sort (in bash, that's 'sort -V')"""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Script to check the normalization of ggH contributions reweighted to NLO; (h,H,A) x (t,b,tb) x mass and to determine normalization correction weights.")

    parser.add_argument(
        "--input-directory",
        required=True,
        type=str,
        help="Input directory of ggH samples with NLO contribution weights, which aren't selected in any way.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    samples = sorted_nicely(glob.glob(os.path.join(args.input_directory,"SUSYGluGluToHToTauTau*","*.root")))
    year_dict = {
        "Summer16" : 2016,
        "Fall17" : 2017,
        "Autumn18" : 2018,
    }
    output_dict = {
        2016 : {},
        2017 : {},
        2018 : {},
    }
    weights = [
        "ggA_b_weight",
        "ggA_i_weight",
        "ggA_t_weight",
        "ggH_b_weight",
        "ggH_i_weight",
        "ggH_t_weight",
        "ggh_b_weight",
        "ggh_i_weight",
        "ggh_t_weight",
    ]
    for s in samples:
        nick = os.path.basename(s).replace(".root","")
        year = year_dict[re.search("("+"|".join(year_dict.keys())+")",nick).groups()[0]]
        mass = int(re.search("(M[1-9][0-9]*)",nick).groups()[0].replace("M",""))
        F = ROOT.TFile.Open(s,"read")
        tree = F.Get("pu_nominal/ntuple")
        entries = tree.GetEntries()
        print nick, year, mass, entries
        output_dict[year][mass] = {}
        h = ROOT.TH1D("h","h",1,0.0,2.0)
        for weight in weights:
            tree.Draw("(generatorWeight >= 0)>>h","%s"%weight,"goff")
            ratio = float(entries)/h.Integral()
            output_dict[year][mass][weight.replace("_weight","")] = ratio
            h.Reset()
        F.Close()

    with open("ggphi_contirbution_weights.json","w") as f:
        f.write(json.dumps(output_dict, sort_keys=True, indent=4))
        f.close()

if __name__ == "__main__":
    main()
