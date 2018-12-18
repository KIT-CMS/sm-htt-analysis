#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import numpy as np
import os
import yaml

import logging
logger = logging.getLogger("calculate_binning.py")


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
        description="Calculate binning of final discriminator.")
    parser.add_argument(
        "--era",
        required=True,
        type=str,
        help="Analysis era")
    parser.add_argument(
        "--input",
        required=True,
        type=str,
        help="Input ROOT file with prefit shapes")
    return parser.parse_args()


def get(f, name):
    x = f.Get(name)
    if x == None:
        logger.critical("Key %s does not exist in %s.", name, f.GetName())
        raise Exception
    return x


def calculate_binning(sig, bkg, min_entries, bins_per_category):
    # Number of bins (without overflow and underflow bins)
    num_bins = sig.GetNbinsX()
    if not num_bins == bkg.GetNbinsX():
        logger.critical("Signal and background histograms have different number of bins.")
        raise Exception
    # Check that number of bins is multiple of bins per category
    if not num_bins % bins_per_category == 0:
        logger.critical("Number of bins in histogram %u is not multiple of bins per category %u.",
                num_bins, bins_per_category)
        raise Exception
    # Go from right to left and merge bins if requirement not met
    bin_borders = [sig.GetBinLowEdge(num_bins+1)]
    b = 0
    for i in reversed(range(2, num_bins+1)):
        b = b+bkg.GetBinContent(i)
        if b>min_entries: # Minimum of background events expected
            bin_borders.insert(0, sig.GetBinLowEdge(i))
            b = 0
        elif (i-1) % bins_per_category == 0: # Split at unrolling border
            bin_borders.insert(0, sig.GetBinLowEdge(i))
            b = 0
    bin_borders.insert(0, sig.GetBinLowEdge(1))
    return np.array(bin_borders)


def to_yaml(x):
    s = yaml.dump([float(f) for f in x])
    return s


def main(args):
    # Find categories and channels in ROOT file (for the given era)
    if not os.path.exists(args.input):
        logger.critical("Input file %s does not exist.", args.input)
        raise Exception
    f = ROOT.TFile(args.input)
    config = {}
    for key in f.GetListOfKeys():
        name = key.GetName()
        if not args.era in name:
            continue
        channel, category = name.split("_")[1:3]
        if not channel in config:
            config[channel] = {}
        if not category in config[channel]:
            config[channel][category] = None

    for channel in config:
        logger.info("Found channel %s with categories %s.", channel, config[channel].keys())

    # Get bins used per category per channel
    bins_per_category = {}
    for channel in config:
        min_bins = 1e6
        for category in config[channel]:
            name = "htt_{}_{}_Run{}_prefit".format(channel, category, args.era)
            directory = get(f, name)
            h = get(directory, "TotalBkg")
            num_bins = h.GetNbinsX()
            if min_bins > num_bins:
                min_bins = int(num_bins)
        bins_per_category[channel] = min_bins

    for channel in config:
        logger.info("Found for channel %s %u bins per category.", channel, bins_per_category[channel])

    # Go through channel and categories and find best binning
    for channel in config:
        for category in config[channel]:
            name = "htt_{}_{}_Run{}_prefit".format(channel, category, args.era)
            directory = get(f, name)
            sig = get(directory, "TotalSig")
            bkg  = get(directory, "TotalBkg")
            binning = calculate_binning(sig=sig, bkg=bkg,
                    min_entries=5, bins_per_category=bins_per_category[channel])
            config[channel][category] = binning
            binning_str = to_yaml(binning)
            logger.info("Binning for category %s in channel %s:\n%s", category, channel, binning_str)

    # Clean-up
    f.Close()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_calculate_binning.log".format(args.era), logging.DEBUG)
    main(args)
