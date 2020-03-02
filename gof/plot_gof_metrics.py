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
    parser.add_argument("-o", "--output-path", required=True, type=str,
                        help="Output path.")
    parser.add_argument("-i", "--input", required=True, type=str,
                        help="Input root file.")
    return parser.parse_args()


def main(args):
    infile = ROOT.TFile(args.input)
    directory = infile.Get("GoodnessOfFit")
    keys = [key.GetName() for key in directory.GetListOfKeys()]
    for key in keys:
        canvas = ROOT.TCanvas()
        hist = directory.Get(key)
        hist.Draw("hist")
        canvas.Print("{}/{}_{}_{}.png".format(args.output_path, args.era, args.gof_type, key))
        canvas.Print("{}/{}_{}_{}.pdf".format(args.output_path, args.era, args.gof_type, key))
    infile.Close()
    return


if __name__ == "__main__":
    args = parse_args()
    main(args)
