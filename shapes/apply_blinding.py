#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
import argparse
import os
import numpy as np
from array import array

import logging
import re
logger = logging.getLogger("")

ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
ROOT.gErrorIgnoreLevel = ROOT.kError


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Apply blinding on shapes based on signal expectation from Monte Carlo."
    )

    parser.add_argument("shapes", type=str, help="ROOT file with shapes.")
    parser.add_argument(
        "--threshold",
        required=True,
        type=float,
        help="Threshold on s/sqrt(s + b + (e*b)**2) expectation of a bin.")
    parser.add_argument(
        "--uncertainty",
        required=True,
        type=float,
        help="Uncertainty of background yield in term (e*b)**2.")
    parser.add_argument("--signal-processes",
                        nargs="+",
                        required=True,
                        help="Substrings to be present in signal categories.")
    parser.add_argument(
        "--exclude-categories",
        nargs="+",
        required=True,
        help="Substrings to be present in excluded categories.")
    parser.add_argument("--exclude-processes",
                        nargs="+",
                        default=["data"],
                        help="Substrings to be present in excluded processes.")
    parser.add_argument(
        "--global_blinding",
        action="store_true",
        help=
        "If set, the treshold is applied as a blinding cut on the NN Score in all signal categories"
    )
    parser.add_argument(
        "--signal-categories",
        nargs="+",
        required=False,
        help=
        "List of all signal categories to be blinded, only used when applying global_blinding"
    )

    return parser.parse_args()


def main(args):
    # Open file with shapes
    logger.debug("Shapesfile: {}".format(args.shapes))
    if not os.path.exists(args.shapes):
        logger.fatal("File %s does not exist.", args.shapes)
        raise Exception
    file_ = ROOT.TFile(args.shapes, "UPDATE")

    # Find out channels, categories and processes of nominal shapes
    shapes = {}
    for key in file_.GetListOfKeys():
        name = key.GetName()
        if not name[-1] == "#":
            continue

        split = [x for x in name.split('#') if x != '']
        channel = split[0]
        category = split[1]
        process = split[2]

        # Check name for validity
        valid = True
        for substring in args.exclude_categories:
            if substring in category:
                valid = False
        for substring in args.exclude_processes:
            if substring in process:
                valid = False
        if not valid:
            continue

        # Append to dict
        if not channel in shapes:
            shapes[channel] = {}
        if not category in shapes[channel]:
            shapes[channel][category] = {"histograms": [], "processes": []}
        if not process in shapes[channel][category]["processes"]:
            shapes[channel][category]["processes"].append(process)
            shapes[channel][category]["histograms"].append(name)

    # Debug output
    signal_processes = {}
    for channel in shapes:
        logger.debug("Categories in channel %s: %s", channel,
                     shapes[channel].keys())

        # Check that in all categories of this channel the same processes are present
        processes = None
        for category in shapes[channel]:
            if processes == None:
                processes = sorted(shapes[channel][category]["processes"])
            if processes != sorted(shapes[channel][category]["processes"]):
                logger.fatal(
                    "Categories of channel %s do not have the same processes.",
                    channel)
                logger.fatal(shapes[channel])
                raise Exception
        logger.debug("Processes in categories of channel %s: %s", channel,
                     processes)

        # Find signal processes
        signal_processes[channel] = []
        for category in shapes[channel]:
            for process in shapes[channel][category]["processes"]:
                for substring in args.signal_processes:
                    if substring in process and not process in signal_processes[
                            channel]:
                        signal_processes[channel].append(process)
        logger.debug("Identified signal processes for channel %s: %s", channel,
                     signal_processes[channel])

    # Set bins to zero if expectation is above threshold
    for channel in shapes:
        for category in shapes[channel]:

            # Stack signals and backgrounds
            signals = None
            backgrounds = None
            for i, process in enumerate(
                    shapes[channel][category]["processes"]):
                if process in signal_processes[channel]:
                    if signals == None:
                        signals = file_.Get(shapes[channel][category]
                                            ["histograms"][i]).Clone()
                    else:
                        signals.Add(
                            file_.Get(
                                shapes[channel][category]["histograms"][i]),
                            1.0)
                else:
                    if backgrounds == None:
                        backgrounds = file_.Get(shapes[channel][category]
                                                ["histograms"][i]).Clone()
                    else:
                        backgrounds.Add(
                            file_.Get(
                                shapes[channel][category]["histograms"][i]),
                            1.0)
            # remove all bins in all signal categories above given threshold
            if args.global_blinding is not None:
                bins_contaminated = []
                logger.debug("Checking {}".format(category[3::]))
                if category[3::] not in args.signal_categories:
                    logger.debug(
                        "this is not a signal category, continuing....")
                    continue
                else:
                    binning = []

                    for i in range(1, signals.GetNbinsX() + 1):
                        binning.append(signals.GetBinLowEdge(i))
                        if signals.GetBinLowEdge(i) >= args.threshold:
                            bins_contaminated.append(i)
                    if "xxh" in category:  # special care for 2D ggh/qqh category
                        logger.debug("Special treatment for 2D category")
                        bins_contaminated = range(11, 26)
                    logger.debug("Binning for {}: {}".format(
                        category, binning))
                    logger.debug(
                        "Bins with signal contamination in category {}: {}".
                        format(category, bins_contaminated))
                good_bins = range(1, bins_contaminated[1])
                logger.debug("Keeping Bins in category {}: {}".format(
                    category, good_bins))
                nbinsx = len(good_bins) - 1
                # remove contaminated bins from the histograms --> write new histogram with limited bins
                logger.debug("Updating histograms")
                filesize = len(file_.GetListOfKeys())
                # create a static list, otherwise, the loop runs forever
                filekeys = [key for key in file_.GetListOfKeys()]
                for s, key in enumerate(filekeys):
                    if s % 10000 == 0:
                        logger.debug("Progress: {} / {}".format(s, filesize))
                    name = key.GetName()
                    if name == "output_tree":
                        continue
                    split = [x for x in name.split('#') if x != '']
                    channel_ = split[0]
                    category_ = split[1]
                    if not channel_ == channel:
                        continue
                    if not category_ == category:
                        continue
                    oldhist = file_.Get(name)
                    bin_borders = [oldhist.GetBinLowEdge(x) for x in good_bins]
                    # bin_borders.append(oldhist.GetBinLowEdge(good_bins[-1]+1))
                    newhist = ROOT.TH1D(name, name, nbinsx,
                                        array("d", bin_borders))
                    for i in good_bins:
                        newhist.SetBinContent(i, oldhist.GetBinContent(i))
                        newhist.SetBinError(i, oldhist.GetBinError(i))
                    if "xxh" in category:  # special care for ggh/qqh 2D category
                        for i in [5, 6, 7]:
                            newhist.SetBinContent(i, 0.0)
                            newhist.SetBinError(i, 0.0)
                    newhist.Write("", ROOT.TObject.kOverwrite)
            else:
                # Check for bins above threshold
                bins_contaminated = []
                for i in range(1, signals.GetNbinsX() + 1):
                    s = signals.GetBinContent(i)
                    b = backgrounds.GetBinContent(i)
                    e = args.uncertainty
                    if s + b == 0:
                        continue
                    if s / np.sqrt(s + b + (e * b)**2) > args.threshold:
                        bins_contaminated.append(i)
                logger.debug(
                    "Bins with signal contamination in category %s: %s",
                    category, bins_contaminated)
                # Set signal contaminated bins to zero for all shapes of this channel and category
                if not len(bins_contaminated) == 0:

                    for key in file_.GetListOfKeys():
                        name = key.GetName()
                        if name == "output_tree":
                            continue
                        split = [x for x in name.split('#') if x != '']
                        channel_ = split[0]
                        category_ = split[1]
                        if not channel_ == channel:
                            continue
                        if not category_ == category:
                            continue
                        hist = file_.Get(name)
                        for i in bins_contaminated:
                            hist.SetBinContent(i, 0.0)
                            hist.SetBinError(i, 0.0)
                        hist.Write()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("apply_blinding.log", logging.DEBUG)
    main(args)
