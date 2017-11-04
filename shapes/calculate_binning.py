#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

from shape_producer.cutstring import Cut, Cuts
from shape_producer.era import Run2016
from shape_producer.channel import ET, MT
from shape_producer.process import Process
from shape_producer.estimation_methods_2016 import DataEstimation

import argparse
import numpy as np
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
        "--et-training",
        type=str,
        default=None,
        help="Name of training on et channel.")
    parser.add_argument(
        "--mt-training",
        type=str,
        default=None,
        help="Name of training on mt channel.")
    return parser.parse_args()


def get_properties(dict_, era, channel, directory, additional_cuts):
    # Get data estimation method
    estimation = DataEstimation(era, directory, channel)

    # Extract weight string, which should be equal (1.0)
    weight_string = estimation.get_weights().extract()
    logger.debug("Data weight string: %s", weight_string)
    if weight_string != "(1.0)":
        logger.fatal("Weight string is not equal to (1.0).")
        raise Exception

    # Extract cut string
    cut_string = (
        estimation.get_cuts() + channel.cuts + additional_cuts).expand()
    logger.debug("Data cut string: %s", cut_string)
    dict_["cut_string"] = str(cut_string)

    # Get files
    files = [str(f) for f in estimation.get_files()]
    for i, f in enumerate(files):
        logger.debug("File %d: %s", i + 1, str(f).replace(directory + "/", ""))
    dict_["files"] = files

    return dict_


def build_chain(dict_):
    # Build chain
    logger.debug("Use tree path %s for chain.", dict_["tree_path"])
    chain = ROOT.TChain(dict_["tree_path"])
    for f in dict_["files"]:
        chain.AddFile(f)
    chain_numentries = chain.GetEntries()
    if not chain_numentries > 0:
        logger.fatal("Chain (before skimming) does not contain any events.")
        raise Exception
    logger.debug("Found %s events before skimming with cut string.",
                 chain_numentries)

    # Skim chain
    chain_skimmed = chain.CopyTree(dict_["cut_string"])
    chain_skimmed_numentries = chain_skimmed.GetEntries()
    if not chain_skimmed_numentries > 0:
        logger.fatal("Chain (after skimming) does not contain any events.")
        raise Exception
    logger.debug("Found %s events after skimming with cut string.",
                 chain_skimmed_numentries)

    return chain_skimmed


def get_percentiles(dict_, channel, training, chain, classes, percentiles):
    # Collect scores
    scores = [[] for c in classes]
    for event in chain:
        max_score = getattr(event, "{}_{}_max_score".format(channel, training))
        max_index = getattr(event, "{}_{}_max_index".format(channel, training))
        scores[int(max_index)].append(max_score)

    # Add minimum point 1.0/len(classes) and maximum point 1.0
    for i in range(len(classes)):
        scores[i].append(1.0 / float(len(classes)))
        scores[i].append(1.0)

    # Get bin borders by percentiles
    for i, c in enumerate(classes):
        dict_[c] = [float(x) for x in np.percentile(scores[i], percentiles[c])]
        logger.debug("Binning for class %s: %s", c, dict_[c])

    return dict_


def main(args):
    # Define era
    era = Run2016(args.datasets)

    # Write base config with given arguments
    config = {
        "era": era.name,
        "directory": args.directory,
        "datasets": args.datasets,
        "output": args.output,
        "channels": {}
    }

    # Channel: ET
    if not args.et_training == None:
        # Get properties
        channel = ET()
        logger.info("Channel: et")
        dict_ = {}
        additional_cuts = Cuts(Cut("mt_1<50", "mt"))
        logger.warning("Use additional cuts for et: %s",
                       additional_cuts.expand())
        dict_ = get_properties(dict_, era, channel, args.directory,
                               additional_cuts)
        dict_["training"] = args.et_training

        # Build chain
        dict_["tree_path"] = "et_nominal/ntuple"
        chain = build_chain(dict_)

        # Define classes
        classes = ["HTT", "ZTT", "ZLL", "W", "TT", "QCD"]
        percentiles = {
            "HTT": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 98, 99, 100],
            "ZTT": [0, 10, 20, 30, 40, 50, 60, 80, 100],
            "ZLL": [0, 10, 20, 30, 40, 50, 60, 80, 100],
            "W": [0, 10, 20, 30, 40, 50, 60, 80, 100],
            "TT": [0, 10, 20, 30, 40, 50, 60, 80, 100],
            "QCD": [0, 10, 20, 30, 40, 50, 60, 80, 100]
        }

        dict_["classes"] = classes
        dict_["percentiles"] = percentiles
        for c in classes:
            logger.debug("Percentiles for class %s: %s", c, percentiles[c])

        # Get percentiles
        dict_ = get_percentiles(dict_, "et", args.et_training, chain, classes,
                                percentiles)

        # Append dict
        config["channels"]["et"] = dict_

    # Channel: MT
    if not args.mt_training == None:
        # Get properties
        channel = MT()
        logger.info("Channel: mt")
        dict_ = {}
        additional_cuts = Cuts(Cut("mt_1<50", "mt"))
        logger.warning("Use additional cuts for mt: %s",
                       additional_cuts.expand())
        dict_ = get_properties(dict_, era, channel, args.directory,
                               additional_cuts)
        dict_["training"] = args.mt_training

        # Build chain
        dict_["tree_path"] = "mt_nominal/ntuple"
        chain = build_chain(dict_)

        # Define classes
        classes = ["HTT", "ZTT", "ZLL", "W", "TT", "QCD"]
        percentiles = {
            "HTT": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 98, 99, 100],
            "ZTT": [0, 10, 20, 30, 40, 50, 60, 80, 100],
            "ZLL": [0, 10, 20, 30, 40, 50, 60, 80, 100],
            "W": [0, 10, 20, 30, 40, 50, 60, 80, 100],
            "TT": [0, 10, 20, 30, 40, 50, 60, 80, 100],
            "QCD": [0, 10, 20, 30, 40, 50, 60, 80, 100]
        }

        dict_["classes"] = classes
        dict_["percentiles"] = percentiles
        for c in classes:
            logger.debug("Percentiles for class %s: %s", c, percentiles[c])

        # Get percentiles
        dict_ = get_percentiles(dict_, "mt", args.mt_training, chain, classes,
                                percentiles)

        # Append dict
        config["channels"]["mt"] = dict_

    # Write config
    logger.info("Write binning config to %s.", args.output)
    yaml.dump(config, open(args.output, 'w'))


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("calculate_binning.log", logging.DEBUG)
    main(args)
