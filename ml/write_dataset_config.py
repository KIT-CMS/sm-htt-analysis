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
    output_config["friend_paths"] = args.friend_paths
    output_config["output_path"] = args.output_path
    output_config["output_filename"] = args.output_filename
    output_config["tree_path"] = args.tree_path
    output_config["event_branch"] = args.event_branch
    output_config["training_weight_branch"] = args.training_weight_branch

    # Define era
    if "2016" in args.era:
        from shape_producer.estimation_methods_2016 import DataEstimation, HTTEstimation, ggHEstimation, qqHEstimation, VHEstimation, ZTTEstimation, ZLEstimation, ZJEstimation, WEstimationRaw, TTTEstimation, TTJEstimation, VVEstimation, QCDEstimationMT, QCDEstimationET, QCDEstimationTT, ZTTEmbeddedEstimation, TTLEstimation, EWKWpEstimation, EWKWmEstimation, EWKZEstimation

        from shape_producer.era import Run2016
        era = Run2016(args.database)
    elif "2017" in args.era:
        from shape_producer.estimation_methods_2017 import DataEstimation, ZTTEstimation, ZJEstimation, ZLEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVTEstimation, VVJEstimation, VVLEstimation, WEstimation, ggHEstimation, qqHEstimation, EWKZEstimation

        from shape_producer.era import Run2017
        era = Run2017(args.database)
    else:
        logger.fatal("Era {} is not implemented.".format(args.era))
        raise Exception

    ############################################################################

    # Era: 2016, Channel: mt
    if "2016" in args.era and args.channel == "mt":
        channel = MTSM2016()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for mt: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH": "ggh",
            "qqH": "qqh",
            "ZTT": "ztt",
            "EMB": "ztt",
            "ZL": "zll",
            "ZJ": "zll",
            "TTT": "tt",
            "TTL": "tt",
            "TTJ": "tt",
            "W": "w",
            "EWKWp": "w",
            "EWKWm": "w",
            "VV": "misc",
            "EWKZ": "misc",
        }
        for estimation in [
                ggHEstimation(era, args.base_path, channel),
                qqHEstimation(era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel),
                ZLEstimation(era, args.base_path, channel),
                ZJEstimation(era, args.base_path, channel),
                TTTEstimation(era, args.base_path, channel),
                #TTLEstimation(era, args.base_path, channel),
                TTJEstimation(era, args.base_path, channel),
                WEstimationRaw(era, args.base_path, channel),
                EWKWpEstimation(era, args.base_path, channel),
                EWKWmEstimation(era, args.base_path, channel),
                VVEstimation(era, args.base_path, channel),
                EWKZEstimation(era, args.base_path, channel),
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path.rstrip("/") + "/", "")
                    for f in estimation.get_files()
                ],
                "cut_string": (estimation.get_cuts() + channel.cuts +
                               additional_cuts).expand(),
                "weight_string":
                estimation.get_weights().extract(),
                "class":
                classes_map[estimation.name]
            }

        # Same sign selection for data-driven QCD
        estimation = DataEstimation(era, args.base_path, channel)
        estimation.name = "QCD"
        channel_ss = copy.deepcopy(channel)
        channel_ss.cuts.get("os").invert()
        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel_ss.cuts +
                           additional_cuts).expand(),
            "weight_string":
            estimation.get_weights().extract(),
            "class":
            "ss"
        }

    ############################################################################

    # Era: 2017, Channel: mt
    if "2017" in args.era and args.channel == "mt":
        channel = MTSM2017()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for mt: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH": "ggh",
            "qqH": "qqh",
            "ZTT": "ztt",
            "ZL": "zll",
            "ZJ": "zll",
            "TTT": "tt",
            "TTL": "tt",
            "TTJ": "tt",
            "W": "w",
            "VVJ": "misc",
            "VVT": "misc",
            "VVL": "misc",
            "EWKZ": "misc"
        }
        for estimation in [
                ggHEstimation("ggH", era, args.base_path, channel),
                qqHEstimation("qqH", era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel),
                ZLEstimation(era, args.base_path, channel),
                ZJEstimation(era, args.base_path, channel),
                TTTEstimation(era, args.base_path, channel),
                TTLEstimation(era, args.base_path, channel),
                TTJEstimation(era, args.base_path, channel),
                WEstimation(era, args.base_path, channel),
                VVJEstimation(era, args.base_path, channel),
                VVTEstimation(era, args.base_path, channel),
                VVLEstimation(era, args.base_path, channel),
                EWKZEstimation(era, args.base_path, channel),
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path.rstrip("/") + "/", "")
                    for f in estimation.get_files()
                ],
                "cut_string": (estimation.get_cuts() + channel.cuts +
                               additional_cuts).expand(),
                "weight_string":
                estimation.get_weights().extract(),
                "class":
                classes_map[estimation.name]
            }

        # Same sign selection for data-driven QCD
        estimation = DataEstimation(era, args.base_path, channel)
        estimation.name = "QCD"
        channel_ss = copy.deepcopy(channel)
        channel_ss.cuts.get("os").invert()
        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel_ss.cuts +
                           additional_cuts).expand(),
            "weight_string":
            estimation.get_weights().extract(),
            "class":
            "ss"
        }

    ############################################################################

    # Era: 2016, Channel: et
    if "2016" in args.era and args.channel == "et":
        channel = ETSM2016()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for et: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH": "ggh",
            "qqH": "qqh",
            "ZTT": "ztt",
            "EMB": "ztt",
            "ZL": "zll",
            "ZJ": "zll",
            "TTT": "tt",
            "TTL": "tt",
            "TTJ": "tt",
            "W": "w",
            "EWKWp": "w",
            "EWKWm": "w",
            "VV": "misc",
            "EWKZ": "misc"
        }
        for estimation in [
                ggHEstimation(era, args.base_path, channel),
                qqHEstimation(era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel),
                ZLEstimation(era, args.base_path, channel),
                ZJEstimation(era, args.base_path, channel),
                TTTEstimation(era, args.base_path, channel),
                #TTLEstimation(era, args.base_path, channel),
                TTJEstimation(era, args.base_path, channel),
                WEstimationRaw(era, args.base_path, channel),
                EWKWpEstimation(era, args.base_path, channel),
                EWKWmEstimation(era, args.base_path, channel),
                VVEstimation(era, args.base_path, channel),
                EWKZEstimation(era, args.base_path, channel),
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path.rstrip("/") + "/", "")
                    for f in estimation.get_files()
                ],
                "cut_string": (estimation.get_cuts() + channel.cuts +
                               additional_cuts).expand(),
                "weight_string":
                estimation.get_weights().extract(),
                "class":
                classes_map[estimation.name]
            }

        # Same sign selection for data-driven QCD
        estimation = DataEstimation(era, args.base_path, channel)
        estimation.name = "QCD"
        channel_ss = copy.deepcopy(channel)
        channel_ss.cuts.get("os").invert()
        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel_ss.cuts +
                           additional_cuts).expand(),
            "weight_string":
            estimation.get_weights().extract(),
            "class":
            "ss"
        }

    ############################################################################

    # Era: 2017, Channel: et
    if "2017" in args.era and args.channel == "et":
        channel = ETSM2017()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for et: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH": "ggh",
            "qqH": "qqh",
            "ZTT": "ztt",
            "ZL": "zll",
            "ZJ": "zll",
            "TTT": "tt",
            "TTL": "tt",
            "TTJ": "tt",
            "W": "w",
            "VVJ": "misc",
            "VVT": "misc",
            "VVL": "misc",
            "EWKZ": "misc"
        }
        for estimation in [
                ggHEstimation("ggH", era, args.base_path, channel),
                qqHEstimation("qqH", era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel),
                ZLEstimation(era, args.base_path, channel),
                ZJEstimation(era, args.base_path, channel),
                TTTEstimation(era, args.base_path, channel),
                TTLEstimation(era, args.base_path, channel),
                TTJEstimation(era, args.base_path, channel),
                WEstimation(era, args.base_path, channel),
                VVJEstimation(era, args.base_path, channel),
                VVTEstimation(era, args.base_path, channel),
                VVLEstimation(era, args.base_path, channel),
                EWKZEstimation(era, args.base_path, channel),
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path.rstrip("/") + "/", "")
                    for f in estimation.get_files()
                ],
                "cut_string": (estimation.get_cuts() + channel.cuts +
                               additional_cuts).expand(),
                "weight_string":
                estimation.get_weights().extract(),
                "class":
                classes_map[estimation.name]
            }

        # Same sign selection for data-driven QCD
        estimation = DataEstimation(era, args.base_path, channel)
        estimation.name = "QCD"
        channel_ss = copy.deepcopy(channel)
        channel_ss.cuts.get("os").invert()
        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel_ss.cuts +
                           additional_cuts).expand(),
            "weight_string":
            estimation.get_weights().extract(),
            "class":
            "ss"
        }

    ############################################################################

    # Era: 2016, Channel: tt
    if "2016" in args.era and args.channel == "tt":
        channel = TTSM2016()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for tt: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH": "ggh",
            "qqH": "qqh",
            "ZTT": "ztt",
            "EMB": "ztt",
            "ZL": "misc",
            "ZJ": "misc",
            "TTT": "misc",
            "TTL": "misc",
            "TTJ": "misc",
            "W": "misc",
            "EWKWp": "misc",
            "EWKWm": "misc",
            "VV": "misc",
            "EWKZ": "misc"
        }
        for estimation in [
                ggHEstimation(era, args.base_path, channel),
                qqHEstimation(era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel),
                ZLEstimation(era, args.base_path, channel),
                ZJEstimation(era, args.base_path, channel),
                TTTEstimation(era, args.base_path, channel),
                #TTLEstimationTT(era, args.base_path, channel),
                TTJEstimation(era, args.base_path, channel),
                WEstimationRaw(era, args.base_path, channel),
                EWKWpEstimation(era, args.base_path, channel),
                EWKWmEstimation(era, args.base_path, channel),
                VVEstimation(era, args.base_path, channel),
                EWKZEstimation(era, args.base_path, channel),
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path.rstrip("/") + "/", "")
                    for f in estimation.get_files()
                ],
                "cut_string": (estimation.get_cuts() + channel.cuts +
                               additional_cuts).expand(),
                "weight_string":
                estimation.get_weights().extract(),
                "class":
                classes_map[estimation.name]
            }

        # Same sign selection for data-driven QCD
        estimation = DataEstimation(era, args.base_path, channel)
        estimation.name = "QCD"
        channel_iso = copy.deepcopy(channel)
        channel_iso.cuts.remove("tau_2_iso")
        channel_iso.cuts.add(
            Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5", "tau_2_iso"))
        channel_iso.cuts.add(
            Cut("byLooseIsolationMVArun2v1DBoldDMwLT_2>0.5",
                "tau_2_iso_loose"))
        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel_iso.cuts +
                           additional_cuts).expand(),
            "weight_string":
            estimation.get_weights().extract(),
            "class":
            "noniso"
        }

    ############################################################################

    # Era: 2017, Channel: tt
    if "2017" in args.era and args.channel == "tt":
        channel = TTSM2017()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for tt: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH": "ggh",
            "qqH": "qqh",
            "ZTT": "ztt",
            "ZJ": "misc",
            "ZL": "misc",
            "TTT": "misc",
            "TTL": "misc",
            "TTJ": "misc",
            "W": "misc",
            "VVT": "misc",
            "VVJ": "misc",
            "VVL": "misc",
            "EWKZ": "misc"
        }
        for estimation in [
                ggHEstimation("ggH", era, args.base_path, channel),
                qqHEstimation("qqH", era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel),
                ZLEstimation(era, args.base_path, channel),
                ZJEstimation(era, args.base_path, channel),
                TTTEstimation(era, args.base_path, channel),
                TTJEstimation(era, args.base_path, channel),
                TTLEstimation(era, args.base_path, channel),
                WEstimation(era, args.base_path, channel),
                VVJEstimation(era, args.base_path, channel),
                VVTEstimation(era, args.base_path, channel),
                VVLEstimation(era, args.base_path, channel),
                EWKZEstimation(era, args.base_path, channel),
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path.rstrip("/") + "/", "")
                    for f in estimation.get_files()
                ],
                "cut_string": (estimation.get_cuts() + channel.cuts +
                               additional_cuts).expand(),
                "weight_string":
                estimation.get_weights().extract(),
                "class":
                classes_map[estimation.name]
            }

        # Same sign selection for data-driven QCD
        estimation = DataEstimation(era, args.base_path, channel)
        estimation.name = "QCD"
        channel_iso = copy.deepcopy(channel)
        channel_iso.cuts.remove("tau_2_iso")
        channel_iso.cuts.add(
            Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5", "tau_2_iso"))
        channel_iso.cuts.add(
            Cut("byLooseIsolationMVArun2017v2DBoldDMwLT2017_2>0.5",
                "tau_2_iso_loose"))
        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel_iso.cuts +
                           additional_cuts).expand(),
            "weight_string":
            estimation.get_weights().extract(),
            "class":
            "noniso"
        }

    ############################################################################

    # Era: 2016, Channel: em
    if "2016" in args.era and args.channel == "em":
        channel = EMSM2016()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for em: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH": "ggh",
            "qqH": "qqh",
            "ZTT": "ztt",
            "EMB": "ztt",
            "ZL": "misc",
            "TTT": "tt",
            "TTL": "tt",
            "W": "misc",
            "VVT": "db",
            "VVL": "db",
        }
        for estimation in [
                ggHEstimation(era, args.base_path, channel),
                qqHEstimation(era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel),
                ZLEstimation(era, args.base_path, channel),
                TTTEstimation(era, args.base_path, channel),
                TTLEstimation(era, args.base_path, channel),
                WEstimation(era, args.base_path, channel),
                VVLEstimation(era, args.base_path, channel),
                VVTEstimation(era, args.base_path, channel),
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path.rstrip("/") + "/", "")
                    for f in estimation.get_files()
                ],
                "cut_string": (estimation.get_cuts() + channel.cuts +
                               additional_cuts).expand(),
                "weight_string":
                estimation.get_weights().extract(),
                "class":
                classes_map[estimation.name]
            }

        # Same sign selection for data-driven QCD
        estimation = DataEstimation(era, args.base_path, channel)
        estimation.name = "QCD"
        channel_ss = copy.deepcopy(channel)
        channel_ss.cuts.get("os").invert()
        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel_ss.cuts +
                           additional_cuts).expand(),
            "weight_string":
            estimation.get_weights().extract(),
            "class":
            "ss"
        }

    ############################################################################

    # Era: 2017, Channel: em
    if "2017" in args.era and args.channel == "em":
        channel = EMSM2017()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for em: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH": "ggh",
            "qqH": "qqh",
            "ZTT": "ztt",
            "EMB": "ztt",
            "ZL": "misc",
            "TTT": "tt",
            "TTL": "tt",
            "W": "misc",
            "VVT": "db",
            "VVL": "db",
        }
        for estimation in [
                ggHEstimation("ggH", era, args.base_path, channel),
                qqHEstimation("qqH", era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel),
                ZLEstimation(era, args.base_path, channel),
                TTTEstimation(era, args.base_path, channel),
                TTLEstimation(era, args.base_path, channel),
                WEstimation(era, args.base_path, channel),
                VVLEstimation(era, args.base_path, channel),
                VVTEstimation(era, args.base_path, channel),
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path.rstrip("/") + "/", "")
                    for f in estimation.get_files()
                ],
                "cut_string": (estimation.get_cuts() + channel.cuts +
                               additional_cuts).expand(),
                "weight_string":
                estimation.get_weights().extract(),
                "class":
                classes_map[estimation.name]
            }

        # Same sign selection for data-driven QCD
        estimation = DataEstimation(era, args.base_path, channel)
        estimation.name = "QCD"
        channel_ss = copy.deepcopy(channel)
        channel_ss.cuts.get("os").invert()
        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel_ss.cuts +
                           additional_cuts).expand(),
            "weight_string":
            estimation.get_weights().extract(),
            "class":
            "ss"
        }

    ############################################################################

    # Write output config
    logger.info("Write config to file: {}".format(args.output_config))
    yaml.dump(
        output_config, open(args.output_config, 'w'), default_flow_style=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
