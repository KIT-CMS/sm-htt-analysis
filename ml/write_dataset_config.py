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
    parser.add_argument(
        "--embedding",
        action="store_true",
        default=False,
        help="Use mu->tau embedded samples as ZTT background estimation.")
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

    # Define era
    if "2016" in args.era:
        from shape_producer.estimation_methods_2016 import DataEstimation, HTTEstimation, ggHEstimation, ggHEstimation_0J, ggHEstimation_1J, ggHEstimation_GE2J, ggHEstimation_VBFTOPO, qqHEstimation, qqHEstimation_VBFTOPO_JET3VETO, qqHEstimation_VBFTOPO_JET3, qqHEstimation_REST, qqHEstimation_PTJET1_GT200, VHEstimation, ZTTEstimation, ZTTEstimationTT, ZLEstimationMTSM, ZLEstimationETSM, ZLEstimationTT, ZJEstimationMT, ZJEstimationET, ZJEstimationTT, WEstimationRaw, TTTEstimationMT, TTTEstimationET, TTTEstimationTT, TTJEstimationMT, TTJEstimationET, TTJEstimationTT, VVEstimation, QCDEstimationMT, QCDEstimationET, QCDEstimationTT, ZTTEmbeddedEstimation, TTLEstimationMT, TTLEstimationET, TTLEstimationTT, TTTTEstimationMT, TTTTEstimationET, EWKWpEstimation, EWKWmEstimation, EWKZllEstimation, EWKZnnEstimation
        from shape_producer.era import Run2016
        era = Run2016(args.database)
    else:
        logger.fatal("Era {} is not implemented.".format(args.era))
        raise Exception

    ############################################################################

    # Channel: mt
    if args.channel == "mt":
        channel = MTSM()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for mt: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH_0J": "ggh",
            "ggH_1J": "ggh",
            "ggH_GE2J": "ggh",
            "ggH_VBFTOPO": "ggh",
            "qqH_VBFTOPO_JET3VETO": "qqh",
            "qqH_VBFTOPO_JET3": "qqh",
            "qqH_REST": "qqh",
            "qqH_PTJET1_GT200": "qqh",
            "ZTT": "ztt",
            "ZL": "zll",
            "ZJ": "zll",
            "TTT": "tt",
            "TTJ": "tt",
            "W": "w",
            "EWKWp": "w",
            "EWKWm": "w",
            "VV": "misc",
            "EWKZll": "misc",
            "EWKZnn": "misc"
        }
        for estimation in [
                ggHEstimation_0J(era, args.base_path, channel),
                ggHEstimation_1J(era, args.base_path, channel),
                ggHEstimation_GE2J(era, args.base_path, channel),
                ggHEstimation_VBFTOPO(era, args.base_path, channel),
                qqHEstimation_VBFTOPO_JET3VETO(era, args.base_path, channel),
                qqHEstimation_VBFTOPO_JET3(era, args.base_path, channel),
                qqHEstimation_REST(era, args.base_path, channel),
                qqHEstimation_PTJET1_GT200(era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel)
                if not args.embedding else ZTTEmbeddedEstimation(
                    era, args.base_path, channel),
                ZLEstimationMTSM(era, args.base_path, channel),
                ZJEstimationMT(era, args.base_path, channel),
                TTTEstimationMT(era, args.base_path, channel)
                if not args.embedding else TTTNoTauTauEstimationMT(
                    era, args.base_path, channel),
                TTJEstimationMT(era, args.base_path, channel),
                WEstimationRaw(era, args.base_path, channel),
                EWKWpEstimation(era, args.base_path, channel),
                EWKWmEstimation(era, args.base_path, channel),
                VVEstimation(era, args.base_path, channel),
                EWKZllEstimation(era, args.base_path, channel),
                #EWKZnnEstimation(era, args.base_path, channel)
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path + "/", "")
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
                str(f).replace(args.base_path + "/", "")
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

    # Channel: et
    if args.channel == "et":
        channel = ETSM()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for et: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH_0J": "ggh",
            "ggH_1J": "ggh",
            "ggH_GE2J": "ggh",
            "ggH_VBFTOPO": "ggh",
            "qqH_VBFTOPO_JET3VETO": "qqh",
            "qqH_VBFTOPO_JET3": "qqh",
            "qqH_REST": "qqh",
            "qqH_PTJET1_GT200": "qqh",
            "ZTT": "ztt",
            "ZL": "zll",
            "ZJ": "zll",
            "TTT": "tt",
            "TTJ": "tt",
            "W": "w",
            "EWKWp": "w",
            "EWKWm": "w",
            "VV": "misc",
            "EWKZll": "misc",
            "EWKZnn": "misc"
        }
        for estimation in [
                ggHEstimation_0J(era, args.base_path, channel),
                ggHEstimation_1J(era, args.base_path, channel),
                ggHEstimation_GE2J(era, args.base_path, channel),
                ggHEstimation_VBFTOPO(era, args.base_path, channel),
                qqHEstimation_VBFTOPO_JET3VETO(era, args.base_path, channel),
                qqHEstimation_VBFTOPO_JET3(era, args.base_path, channel),
                qqHEstimation_REST(era, args.base_path, channel),
                qqHEstimation_PTJET1_GT200(era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel)
                if not args.embedding else ZTTEmbeddedEstimation(
                    era, args.base_path, channel),
                ZLEstimationETSM(era, args.base_path, channel),
                ZJEstimationET(era, args.base_path, channel),
                TTTEstimationET(era, args.base_path, channel)
                if not args.embedding else TTTNoTauTauEstimationET(
                    era, args.base_path, channel),
                TTJEstimationET(era, args.base_path, channel),
                WEstimationRaw(era, args.base_path, channel),
                EWKWpEstimation(era, args.base_path, channel),
                EWKWmEstimation(era, args.base_path, channel),
                VVEstimation(era, args.base_path, channel),
                EWKZllEstimation(era, args.base_path, channel),
                #EWKZnnEstimation(era, args.base_path, channel)
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path + "/", "")
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
                str(f).replace(args.base_path + "/", "")
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

    # Channel: tt
    if args.channel == "tt":
        channel = TTSM()

        # Set up `processes` part of config
        output_config["processes"] = {}

        # Additional cuts
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for tt: %s",
                       additional_cuts.expand())

        # MC-driven processes
        # NOTE: Define here the mappig of the process estimations to the training classes
        classes_map = {
            "ggH_0J": "ggh",
            "ggH_1J": "ggh",
            "ggH_GE2J": "ggh",
            "ggH_VBFTOPO": "ggh",
            "qqH_VBFTOPO_JET3VETO": "qqh",
            "qqH_VBFTOPO_JET3": "qqh",
            "qqH_REST": "qqh",
            "qqH_PTJET1_GT200": "qqh",
            "ZTT": "ztt",
            "ZL": "misc",
            "ZJ": "misc",
            "TTT": "misc",
            "TTJ": "misc",
            "W": "misc",
            "EWKWp": "misc",
            "EWKWm": "misc",
            "VV": "misc",
            "EWKZll": "misc",
            "EWKZnn": "misc"
        }
        for estimation in [
                ggHEstimation_0J(era, args.base_path, channel),
                ggHEstimation_1J(era, args.base_path, channel),
                ggHEstimation_GE2J(era, args.base_path, channel),
                ggHEstimation_VBFTOPO(era, args.base_path, channel),
                qqHEstimation_VBFTOPO_JET3VETO(era, args.base_path, channel),
                qqHEstimation_VBFTOPO_JET3(era, args.base_path, channel),
                qqHEstimation_REST(era, args.base_path, channel),
                qqHEstimation_PTJET1_GT200(era, args.base_path, channel),
                ZTTEstimation(era, args.base_path, channel)
                if not args.embedding else ZTTEmbeddedEstimation(
                    era, args.base_path, channel),
                ZLEstimationTT(era, args.base_path, channel),
                ZJEstimationTT(era, args.base_path, channel),
                TTTEstimationTT(era, args.base_path, channel)
                if not args.embedding else TTTNoTauTauEstimationTT(
                    era, args.base_path, channel),
                TTJEstimationTT(era, args.base_path, channel),
                WEstimationRaw(era, args.base_path, channel),
                EWKWpEstimation(era, args.base_path, channel),
                EWKWmEstimation(era, args.base_path, channel),
                VVEstimation(era, args.base_path, channel),
                EWKZllEstimation(era, args.base_path, channel),
                #EWKZnnEstimation(era, args.base_path, channel)
        ]:
            output_config["processes"][estimation.name] = {
                "files": [
                    str(f).replace(args.base_path + "/", "")
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
                str(f).replace(args.base_path + "/", "")
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

    # Write output config
    logger.info("Write config to file: {}".format(args.output_config))
    yaml.dump(
        output_config, open(args.output_config, 'w'), default_flow_style=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
