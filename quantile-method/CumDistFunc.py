#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT

import argparse
import copy
import array

import logging
logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Derive cumulative distribution function as splines from histograms."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="ROOT file with shapes")
    parser.add_argument(
        "-s",
        "--shapes",
        nargs="+",
        type=str,
        required=True,
        help="Shape names in the input ROOT file")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Output ROOT file with splines")
    parser.add_argument(
        "-c",
        "--control",
        action='store_true',
        help="Draw resulting splines to cross check")

    return parser.parse_args()

def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def main(args):
    # read inputs
    input_hists = []
    inputfile = ROOT.TFile(args.input, "READ")
    for entry in args.shapes:
        input_hists.append(copy.deepcopy(inputfile.Get(entry)))
    inputfile.Close()
    
    # derive splines of cumulative distributions and save them
    outputfile = ROOT.TFile(args.output, "RECREATE")
    canvas = ROOT.TCanvas()
    for index, hist in enumerate(input_hists):
        # derive knots of the cumulative distribution function
        npoints = hist.GetNbinsX()
        xpoints = [hist.GetBinLowEdge(1)]
        ypoints = [0.0]
        for i in range(1, npoints+1):
            xpoints.append(hist.GetBinLowEdge(i) + hist.GetBinWidth(i))
            ypoints.append(ypoints[-1] + hist.GetBinContent(i))
        ypoints_norm = [x / ypoints[-1] for x in ypoints]
        logger.debug("x-values: "+" ".join([str(x) for x in xpoints]))
        logger.debug("y-values: "+" ".join([str(x) for x in ypoints_norm]))
        
        # generate splines
        print hist.GetName()
        spline = ROOT.TSpline3(hist.GetName(), array.array('d', xpoints), array.array('d', ypoints_norm), npoints+1, "b1e1", 0.0, 0.0)
        spline.SetName(hist.GetName())
        spline.Write()
        if args.control:
            spline.SetLineColor(2+index)
            spline.SetLineWidth(3)
            spline.SetMarkerColor(2+index)
            spline.SetMarkerStyle(20)
            spline.SetMarkerSize(1.5)
            spline.Draw("lcp")# if index == 0 else "lcpsame")
            canvas.SaveAs("spline_%s.pdf"%hist.GetName())
    outputfile.Close()
    


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("cumdistfunc.log", logging.DEBUG)
    main(args)