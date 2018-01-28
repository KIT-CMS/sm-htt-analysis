#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

from shape_producer.era import Run2016
from shape_producer.channel import ETSM, MTSM, TTSM
from shape_producer.estimation_methods_2016 import DataEstimation

import argparse
import numpy as np
import yaml
import os

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
        description="Calculate binning of ML scores.")

    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--datasets", required=True, type=str, help="Kappa datsets database.")
    parser.add_argument(
        "--output",
        required=True,
        type=str,
        help="Output path for binning config.")
    parser.add_argument(
        "--artus-friends",
        required=True,
        type=str,
        help="Friend trees with neural network responses.")
    parser.add_argument(
        "--channel",
        required=True,
        type=str,
        help="Name of training on mt channel.")
    parser.add_argument(
        "--training-config",
        required=True,
        type=str,
        help="Name training config.")

    return parser.parse_args()


def main(args):
    # Define era and channel
    era = Run2016(args.datasets)

    if "et" in args.channel:
        channel = ETSM()
    elif "mt" in args.channel:
        channel = MTSM()
    elif "tt" in args.channel:
        channel = TTSM()
    else:
        logger.fatal("Channel %s not known.", args.channel)
        raise Exception
    logger.debug("Use channel %s.", args.channel)

    # Get cut string
    estimation = DataEstimation(era, args.directory, channel)
    cut_string = (estimation.get_cuts() + channel.cuts).expand()
    logger.debug("Data cut string: %s", cut_string)

    # Get chain
    tree_path = "{}_nominal/ntuple".format(args.channel)
    logger.debug("Use tree path %s to get tree.", tree_path)

    files = [str(f) for f in estimation.get_files()]
    chain = ROOT.TChain()
    for i, f in enumerate(files):
        base = os.path.basename(f).replace(".root", "")
        f_friend = os.path.join(args.artus_friends, base,
                                base + ".root") + "/" + tree_path
        logger.debug("Add file with scores %d: %s", i, f_friend)
        chain.Add(f_friend)
        logger.debug("Add friend with ntuple %d: %s", i, f)
        chain.AddFriend(tree_path, f)

    chain_numentries = chain.GetEntries()
    if not chain_numentries > 0:
        logger.fatal("Chain (before skimming) does not contain any events.")
        raise Exception
    logger.debug("Found %s events before skimming with cut string.",
                 chain_numentries)

    # Skim chain
    chain_skimmed = chain.CopyTree(cut_string)
    chain_skimmed_numentries = chain_skimmed.GetEntries()

    if not chain_skimmed_numentries > 0:
        logger.fatal("Chain (after skimming) does not contain any events.")
        raise Exception
    logger.debug("Found %s events after skimming with cut string.",
                 chain_skimmed_numentries)

    # Calculate binning
    logger.debug("Load classes from config %s.", args.training_config)
    classes = yaml.load(open(args.training_config))["classes"]
    logger.debug("Use classes %s.", classes)
    scores = [[] for c in classes]
    for event in chain_skimmed:
        max_score = float(getattr(event, args.channel + "_max_score"))
        max_index = int(getattr(event, args.channel + "_max_index"))
        scores[max_index].append(max_score)

    binning = {}
    percentiles = range(0, 105, 5)
    logger.debug("Use percentiles %s for binning.", percentiles)
    for i, name in enumerate(classes):
        logger.debug("Process class %s.", name)
        x = scores[i] + [1.0/float(len(classes)), 1.0]
        logger.debug("Found %s events in class %s.", len(x), name)
        binning[name] = [float(x) for x in np.percentile(x, percentiles)]

    # Write binning to output
    config = yaml.load(open(args.output))
    config["analysis"][args.channel] = binning
    logger.info("Write binning to %s.", args.output)
    yaml.dump(config, open(args.output, "w"))


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("calculate_binning.log", logging.DEBUG)
    main(args)
