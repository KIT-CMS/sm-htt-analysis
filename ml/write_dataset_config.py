#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import yaml
import os
import copy

from shape_producer.channel import *
from shape_producer.estimation_methods_2016 import *
from shape_producer.era import Run2016

import logging
logger = logging.getLogger("write_dataset_config")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    logger.debug("Parse arguments.")
    parser = argparse.ArgumentParser(
        description=
        "Write dataset config for creation of training dataset for a specific channel."
    )
    parser.add_argument("--channel", required=True, help="Analysis channel")
    parser.add_argument(
        "--base-path", required=True, help="Path to Artus output files")
    parser.add_argument(
        "--output-path", required=True, help="Path to output directory")
    parser.add_argument(
        "--output-filename",
        required=True,
        help="Filename postifx of output filename")
    parser.add_argument(
        "--tree-path", required=True, help="Path to tree in ROOT files")
    parser.add_argument(
        "--event-branch", required=True, help="Branch with event numbers")
    parser.add_argument(
        "--training-weight-branch",
        required=True,
        help="Branch with training weights")
    parser.add_argument(
        "--output-config", required=True, help="Output dataset config file")
    parser.add_argument(
        "--database", required=True, help="Kappa datsets database.")
    return parser.parse_args()


def main(args):
    # Write arparse arguments to YAML config
    logger.debug("Write argparse arguments to YAML config.")
    output_config = {}
    output_config["base_path"] = args.base_path
    output_config["output_path"] = args.output_path
    output_config["output_filename"] = args.output_filename
    output_config["tree_path"] = args.tree_path
    output_config["event_branch"] = args.event_branch
    output_config["training_weight_branch"] = args.training_weight_branch

    # Set up era and channel
    era = Run2016(args.database)
    if args.channel == "mt":
        channel = MT()
    else:
        logger.fatal("Channel %s is not implemented.", args.channel)
        raise Exception

    # Set up `processes` part of config
    output_config["processes"] = {}

    # MC-driven processes
    for estimation in [
            HttEstimation(era, args.base_path, channel),
            ZttEstimation(era, args.base_path, channel),
            ZllEstimation(era, args.base_path, channel),
            VVEstimation(era, args.base_path, channel),
            TTEstimation(era, args.base_path, channel),
            WJetsEstimation(era, args.base_path, channel)
    ]:
        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel.cuts).expand(),
            "weight_string":
            estimation.get_weights().extract()
        }

    # Same sign selection for data-driven QCD
    estimation = DataEstimation(era, args.base_path, channel)
    channel_ss = copy.deepcopy(channel)
    channel_ss.cuts.get("os").invert()
    output_config["processes"][estimation.name] = {
        "files": [
            str(f).replace(args.base_path + "/", "")
            for f in estimation.get_files()
        ],
        "cut_string": (estimation.get_cuts() + channel_ss.cuts).expand(),
        "weight_string":
        estimation.get_weights().extract()
    }

    # Write output config
    logger.info("Write config to file: {}".format(args.output_config))
    yaml.dump(
        output_config, open(args.output_config, 'w'), default_flow_style=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
