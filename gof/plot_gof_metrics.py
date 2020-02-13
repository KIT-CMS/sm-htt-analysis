#!/usr/bin/env python

import argparse

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--era", required=True, type=str,
                        help="Experiment era")
    parser.add_argument("-g", "--gof-type", required=True,
                        choices=["AD", "KS"],
                        help="Type of goodness of fit test.")
    return parser.parse_args()


def main(args):
    filename = "higgsCombineTest.GoodnessOfFit.mH125.root"
    infile = ROOT.TFile(filename)
    directory = infile.Get("GoodnessOfFit")
    keys = [key.GetName() for key in directory.GetListOfKeys()]
    for key in keys:
        print key
        canvas = ROOT.TCanvas()
        hist = directory.Get(key)
        hist.Draw("hist")
        canvas.Print("{}_plots/{}_{}.png".format(args.era, args.gof_type, key))
        canvas.Print("{}_plots/{}_{}.pdf".format(args.era, args.gof_type, key))
    infile.Close()
    return


if __name__ == "__main__":
    args = parse_args()
    main(args)
