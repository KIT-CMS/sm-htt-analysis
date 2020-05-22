#!/usr/bin/env python
import argparse
import logging
import yaml
import json
from array import array

import ROOT as root

root.gROOT.SetBatch()
root.PyConfig.IgnoreCommandLineOptions = True

import Dumbledraw.styles as styles
import Dumbledraw.rootfile_parser as rootfile_parser


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file.")
    parser.add_argument("-o", "--output", help="Output directory.")
    parser.add_argument("-e", "--era", help="Experiment era.")
    parser.add_argument("-c", "--channel", help="Considered channel.")
    parser.add_argument("-v", "--variable", help="Variable")
    parser.add_argument("--postfit", action="store_true", help="Do plot for postfit shapes.")
    return parser.parse_args()


def create_pull_histo(fname, title, era, channel, bins=5):
    # Book histogram filled at a later stage
    histo = root.TH2F(title, title,
                      bins, array("d", range(bins + 1)),
                      bins, array("d", range(bins + 1))
                      )
    # Load histograms from root file
    fi = rootfile_parser.Rootfile_parser(fname)
    data_obs = fi.get(era, channel, 300, "data_obs")
    total_bkg = fi.get(era, channel, 300, "TotalBkg")
    if data_obs.GetNbinsX() != bins**2:
        logging.fatal(
                "Number of bins {} does not match to expactation {}.".format(
                    data_obs.GetNbinsX(), bins**2))
        logging.fatal("This is not handled at the moment.")
        raise Exception
    # Loop over data and bkg histograms and calculate normalized difference.
    # This is given as (data_obs-bkg)/sqrt(data_obs_err**2 + bkg_err**2)
    for i in xrange(1, bins + 1):
        for j in xrange(1, bins + 1):
            k = bins * (i - 1) + j
            histo.SetBinContent(j, i,
                                ((data_obs.GetBinContent(k)-total_bkg.GetBinContent(k))
                                 / root.TMath.Sqrt(data_obs.GetBinError(k)**2
                                                   + total_bkg.GetBinError(k)**2))
                                 )
    return histo


def calculate_corr_factor(fname, process, era, channel,
                          bins=5, edges=None):
    # Set the binning of the 2D histogram used in the correlation coefficient
    # calculation.
    if edges is None:
        edges = [range(bins+1), range(bins+1)]
    else:
        if len(edges[0]) != bins + 1:
            logging.fatal("Number of given x-axis bin edges %i "
                          "does not match to expected number %i.",
                          len(edges[0]), bins + 1)
            raise Exception
        elif len(edges[1]) != bins + 1:
            logging.fatal("Number of given x-axis bin edges %i "
                          "does not match to expected number %i.",
                          len(edges[1]), bins + 1)
            raise Exception
    # Create the 2D histogram used in the correlation coefficient calculation.
    histo = root.TH2F("h_Dummy", "h_Dummy",
                      bins, array("d", edges[0]),
                      bins, array("d", edges[1])
                      )
    # Load histograms from root file
    fi = rootfile_parser.Rootfile_parser(fname)
    proc_hist = fi.get(era, channel, 300, process)
    if proc_hist.GetNbinsX() != bins**2:
        logging.fatal(
                "Number of bins {} does not match to expactation {}.".format(
                    proc_hist.GetNbinsX(), bins**2))
        logging.fatal("This is not handled at the moment.")
        raise Exception
    # Loop over data and bkg histograms and calculate normalized difference.
    # This is given as (data_obs-bkg)/sqrt(data_obs_err**2 + bkg_err**2)
    for i in xrange(1, bins + 1):
        for j in xrange(1, bins + 1):
            k = bins * (i - 1) + j
            histo.SetBinContent(j, i, proc_hist.GetBinContent(k))
            histo.SetBinError(j, i, proc_hist.GetBinError(k))
    print histo.GetCovariance()
    return histo.GetCorrelationFactor()



def split_variables(varname, var_list):
    var_comps = varname.split("_")
    var1 = ""
    for i, comp in enumerate(var_comps):
        if i == 0:
            var1 = comp
        else:
            var1 = "_".join([var1, comp])
        if var1 in var_list:
            var2 = "_".join(var_comps[i+1:])
            break
    if var2 not in var_list:
        logging.fatal("Second variable %s not var_list.", var2)
        raise Exception
    return var1, var2


def setStyle():
    # Styles
    styles.SetStyle("ModTDR")
    root.gStyle.SetPadBottomMargin(0.13)
    root.gStyle.SetPadLeftMargin(0.15)
    # root.gStyle.SetPadLeftMargin(0.05)
    root.gStyle.SetPadTopMargin(0.06)
    root.gStyle.SetPadRightMargin(0.12)
    # root.gStyle.SetPadRightMargin(0.05)

    root.gStyle.SetLabelFont(42, "X")
    root.gStyle.SetLabelFont(42, "Y")
    root.gStyle.SetLabelSize(0.04, "X")
    root.gStyle.SetLabelSize(0.04, "Y")
    # root.gStyle.SetLabelOffset(0.03, "Y")
    root.gStyle.SetTickLength(0.02, "X")
    root.gStyle.SetTickLength(0.02, "Y")
    root.gStyle.SetLineWidth(1)
    root.gStyle.SetTickLength(0.02, "Z")

    root.gStyle.SetTitleSize(0.1)
    root.gStyle.SetTitleFont(42, "X")
    root.gStyle.SetTitleFont(42, "Y")
    root.gStyle.SetTitleSize(0.25, "X")
    root.gStyle.SetTitleSize(0.05, "Y")
    root.gStyle.SetTitleOffset(1.1, "X")
    root.gStyle.SetTitleOffset(1.3, "Y")
    root.gStyle.SetOptStat(0)

    root.gStyle.SetPaintTextFormat("1.2f")
    return


def SetCorrMatrixPalette():
    root.TColor.CreateGradientColorTable(3,
                                      array("d",[0.00, 0.50, 1.00]),
                                      array("d",[0.00, 1.00, 1.00]),
                                      array("d",[0.00, 1.00, 0.00]),
                                      array("d",[1.00, 1.00, 0.00]),
                                      10000,  1.0)


def main(args):
    # Load additional needed input to set the binning and separate the variable string.
    variables_list = yaml.load(open("gof/variables.yaml"))["variables"]
    binning = yaml.load(open("gof/{}_binning.yaml".format(args.era)))["gof"][args.channel]

    hist = create_pull_histo(args.input, "test", args.era, args.channel)

    setStyle()

    lumi_dict = {
            "2016": "35.9 fb^{-1} (2016, 13 TeV)",
            "2017": "41.5 fb^{-1} (2017, 13 TeV)",
            "2018": "59.7 fb^{-1} (2018, 13 TeV)",
    }
    channel_label = {
            "et": "e#tau_{h}",
            "mt": "#mu#tau_{h}",
            "tt": "#tau_{h}#tau_{h}",
            "em": "e#mu",
    }

    c = root.TCanvas("c", "c", 600, 600)
    hist.Draw("colz text MIN0")
    hist.GetZaxis().SetRangeUser(-2.5, 2.5)
    # root.gStyle.SetPalette(104)
    # root.TColor.InvertPalette()
    root.gStyle.SetNumberContours(40)
    SetCorrMatrixPalette()
    # Extract variable names from 2D binning.
    xname, yname = split_variables(args.variable, variables_list)
    if xname in styles.x_label_dict[args.channel]:
        x_label = styles.x_label_dict[args.channel][
            xname]
    else:
        x_label = xname
    if yname in styles.x_label_dict[args.channel]:
        y_label = styles.x_label_dict[args.channel][
            yname]
    else:
        y_label = yname
    hist.SetTitle("Pull; {}; {}".format(x_label, y_label))
    hist.GetXaxis().SetNdivisions(5)
    hist.GetYaxis().SetNdivisions(5)
    styles.DrawTitle(c, lumi_dict[args.era], 3)
    if channel_label is not None:
        latex2 = root.TLatex()
        latex2.SetNDC()
        latex2.SetTextAngle(0)
        latex2.SetTextColor(root.kBlack)
        latex2.SetTextSize(0.04)
        latex2.DrawLatex(0.145, 0.960, "%s, %s" % (channel_label[args.channel], "inclusive"))
    if args.postfit:
        c.Print(args.output + "{}_{}_{}_pulls_postfit.png".format(args.era, args.channel, args.variable), "png")
        c.Print(args.output + "{}_{}_{}_pulls_postfit.pdf".format(args.era, args.channel, args.variable), "pdf")
    else:
        c.Print(args.output + "{}_{}_{}_pulls_prefit.png".format(args.era, args.channel, args.variable), "png")
        c.Print(args.output + "{}_{}_{}_pulls_prefit.pdf".format(args.era, args.channel, args.variable), "pdf")

    # Calculate correlation factors for data and model and dump them to json file.
    edges = [binning[xname]["bins"][::2], binning[yname]["bins"][::2]]
    corr_coeff = {}
    for process in ["data_obs", "TotalBkg"]:
        corr_coeff[process] = calculate_corr_factor(args.input, process, args.era, args.channel, edges=edges)
    if args.postfit:
        with open(args.output + "{}_{}_{}_correlations_postfit.json".format(args.era, args.channel, args.variable), "w") as f:
            f.write(json.dumps(corr_coeff, indent=4, separators=(",", ": ")))
    else:
        with open(args.output + "{}_{}_{}_correlations_prefit.json".format(args.era, args.channel, args.variable), "w") as f:
            f.write(json.dumps(corr_coeff, indent=4, separators=(",", ": ")))
    return


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
