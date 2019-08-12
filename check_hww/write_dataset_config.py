#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import yaml
import os
import copy

from shape_producer.cutstring import Cut, Cuts
from shape_producer.channel import *

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
    parser.add_argument("--era", required=True, help="Experiment era")
    parser.add_argument(
        "--base-path", required=True, help="Path to Artus output files")
    parser.add_argument(
        "--friend-paths", nargs='+', default=[], help="Additional paths to Artus output friend files")
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
        "--output-config", required=True, help="Output dataset config file")
    parser.add_argument(
        "--database", required=True, help="Kappa datsets database.")
    parser.add_argument(
        "--training-weight-branch",
        required=True,
        help="Branch with training weights")
    return parser.parse_args()


def main(args):
    # Write arparse arguments to YAML config
    logger.debug("Write argparse arguments to YAML config.")
    output_config = {}
    output_config["base_path"] = args.base_path
    output_config["friend_paths"] = args.friend_paths
    output_config["output_path"] = args.output_path
    output_config["output_filename"] = args.output_filename
    output_config["tree_path"] = args.tree_path
    output_config["event_branch"] = args.event_branch
    output_config["training_weight_branch"] = args.training_weight_branch

    # Define era
    if "2016" in args.era:
        from shape_producer.estimation_methods_2016 import ggHEstimation, qqHEstimation, HWWEstimation
        from shape_producer.era import Run2016
        era = Run2016(args.database)

    elif "2017" in args.era:
        from shape_producer.estimation_methods_2017 import ggHEstimation, qqHEstimation, HWWEstimation, DataEstimation
        from shape_producer.era import Run2017
        era = Run2017(args.database)
    else:
        logger.fatal("Era {} is not implemented.".format(args.era))
        raise Exception

    def estimationMethodAndClassMapGenerator():
        estimationMethodList = [
            DataEstimation(era, args.base_path, channel),
            ggHEstimation("ggH125", era, args.base_path, channel),
            qqHEstimation("qqH125", era, args.base_path, channel),
            HWWEstimation(era, args.base_path, channel),
        ]
        return(estimationMethodList)

    channelDict={}
    channelDict["2016"]={"mt":MTSM2016(),"et":ETSM2016(), "tt":TTSM2016(), "em":EMSM2016()}
    channelDict["2017"]={"mt":MTSM2017(),"et":ETSM2017(), "tt":TTSM2017(), "em":EMSM2017()}

    channel=channelDict[args.era][args.channel]

    # Set up `processes` part of config
    output_config["processes"] = {}

    # Additional cuts
    additional_cuts = Cuts()
    logger.warning("Use additional cuts for mt: %s", additional_cuts.expand())

    estimationMethodList = estimationMethodAndClassMapGenerator()

    for estimation in estimationMethodList:
        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel.cuts +
                           additional_cuts).expand(),
            "weight_string":
            estimation.get_weights().extract(),
        }

    # Write output config
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)
    logger.info("Write config to file: {}".format(args.output_config))
    yaml.dump(output_config, open(args.output_config, 'w'), default_flow_style=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
