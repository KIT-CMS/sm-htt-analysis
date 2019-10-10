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
        "--training-z-estimation-method",
        required=True,
        help="Estimate the Z bkg with emb (embedding) or mc (Monte Carlo) ?")
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
        from shape_producer.estimation_methods_2016 import DataEstimation, ggHEstimation, qqHEstimation, ZTTEstimation, ZLEstimation, ZJEstimation, WEstimation, TTTEstimation, TTJEstimation, ZTTEmbeddedEstimation, TTLEstimation, EWKZEstimation, VVLEstimation, VVJEstimation, VVEstimation, VVTEstimation
        #QCDEstimation_SStoOS_MTETEM, QCDEstimationTT, EWKWpEstimation, EWKWmEstimation, , VHEstimation, HTTEstimation,
        from shape_producer.era import Run2016
        era = Run2016(args.database)

    elif "2017" in args.era:
        from shape_producer.estimation_methods_2017 import DataEstimation, ZTTEstimation, ZJEstimation, ZLEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVTEstimation, VVJEstimation, VVLEstimation, WEstimation, ggHEstimation, qqHEstimation, EWKZEstimation, ZTTEmbeddedEstimation

        from shape_producer.era import Run2017
        era = Run2017(args.database)

    elif "2018" in args.era:
        from shape_producer.estimation_methods_2018 import DataEstimation, ZTTEstimation, ZJEstimation, ZLEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVTEstimation, VVJEstimation, VVLEstimation, WEstimation, ggHEstimation, qqHEstimation, EWKZEstimation, ZTTEmbeddedEstimation

        from shape_producer.era import Run2018
        era = Run2018(args.database)
    else:
        logger.fatal("Era {} is not implemented.".format(args.era))
        raise Exception

    def estimationMethodAndClassMapGenerator():
        ###### common processes
        classes_map = {
            "ggH": "ggh",
            "qqH": "qqh",
            "EWKZ": "misc"
        }
        estimationMethodList = [
            ggHEstimation("ggH", era, args.base_path, channel),
            qqHEstimation("qqH", era, args.base_path, channel),
            EWKZEstimation(era, args.base_path, channel),
            VVLEstimation(era, args.base_path, channel),
	    WEstimation(era, args.base_path, channel)
        ]
        ######## Check for emb vs MC
        if args.training_z_estimation_method=="emb":
            classes_map["EMB"]="ztt"
            estimationMethodList.extend([
                ZTTEmbeddedEstimation(era, args.base_path, channel)])

        elif args.training_z_estimation_method=="mc":
            classes_map["ZTT"]="ztt"
            estimationMethodList.extend([
                ZTTEstimation(era, args.base_path, channel),
                TTTEstimation(era, args.base_path, channel),
                VVTEstimation(era, args.base_path, channel)
            ])
        else:
            logger.fatal("No valid training-z-estimation-method! Options are emb, mc. Argument was {}".format(args.training_z_estimation_method))
            raise Exception


        ##### TT* zl,zj processes
        estimationMethodList.extend([
            TTLEstimation(era, args.base_path, channel),
            ZLEstimation(era, args.base_path, channel)
        ])
        # less data-> less categories for tt
        if args.channel == "tt":
            classes_map.update({
                "TTT": "misc",
                "TTL": "misc",
                "TTJ": "misc",
                "ZL": "misc",
                "ZJ": "misc"
            })
            estimationMethodList.extend([
                        ZJEstimation(era, args.base_path, channel),
                        TTJEstimation(era, args.base_path, channel)
            ])
        ## not TTJ,ZJ for em
        elif args.channel== "em":
            classes_map.update({
                "TTT": "tt",
                "TTL": "tt",
                "ZL": "misc"
            })
        else:
            classes_map.update({
                "TTT": "tt",
                "TTL": "tt",
                "TTJ": "tt",
                "ZL": "zll",
                "ZJ": "zll"
            })
            estimationMethodList.extend([
                ZJEstimation(era, args.base_path, channel),
                TTJEstimation(era, args.base_path, channel)
            ])
        ###w:
        # estimation metho already included, just different mapping fror et and mt
        if args.channel in ["et","mt"]:
            classes_map["W"]="w"
        else:
            classes_map["W"]="misc"

        #####  VV/[VVT,VVL,VVJ] split
        # VVL in common, VVT in "EMBvsMC"
        if args.channel=="em":
            classes_map.update({
                "VVT": "db",
                "VVL": "db"
            })
        else:
            classes_map.update({
                "VVT": "misc",
                "VVL": "misc",
                "VVJ": "misc"
            })
            estimationMethodList.extend([
                VVJEstimation(era, args.base_path, channel),
            ])
        ### QCD class

        if args.channel =="tt":
            classes_map["QCD"]="noniso"
        else:
            classes_map["QCD"]="ss"
        return([classes_map,estimationMethodList])


    channelDict={}
    channelDict["2016"]={"mt":MTSM2016(),"et":ETSM2016(), "tt":TTSM2016(), "em":EMSM2016()}
    channelDict["2017"]={"mt":MTSM2017(),"et":ETSM2017(), "tt":TTSM2017(), "em":EMSM2017()}
    channelDict["2018"]={"mt":MTSM2018(),"et":ETSM2018(), "tt":TTSM2018(), "em":EMSM2018()}

    channel=channelDict[args.era][args.channel]

    # Set up `processes` part of config
    output_config["processes"] = {}

    # Additional cuts
    additional_cuts = Cuts()
    logger.warning("Use additional cuts for mt: %s", additional_cuts.expand())

    classes_map,estimationMethodList = estimationMethodAndClassMapGenerator()

    ##MC+/Embedding Processes
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
            "class":
            classes_map[estimation.name]
        }
    ###
    # Same sign selection for data-driven QCD
    estimation = DataEstimation(era, args.base_path, channel)
    estimation.name = "QCD"
    channel_qcd = copy.deepcopy(channel)

    if args.channel != "tt":
        ## os= opposite sign
        channel_qcd.cuts.get("os").invert()
    # Same sign selection for data-driven QCD
    else:
        channel_qcd.cuts.remove("tau_2_iso")
        channel_qcd.cuts.add(
            Cut("byTightIsolationMVArun2017v2DBoldDMwLT2017_2<0.5", "tau_2_iso"))
        channel_qcd.cuts.add(
            Cut("byLooseIsolationMVArun2017v2DBoldDMwLT2017_2>0.5", "tau_2_iso_loose"))

    output_config["processes"][estimation.name] = {
        "files": [
            str(f).replace(args.base_path.rstrip("/") + "/", "")
            for f in estimation.get_files()
        ],
        "cut_string": (estimation.get_cuts() + channel_qcd.cuts + additional_cuts).expand(),
        "weight_string": estimation.get_weights().extract(),
        "class":classes_map[estimation.name]
    }

    #####################################
    # Write output config
    logger.info("Write config to file: {}".format(args.output_config))
    yaml.dump(output_config, open(args.output_config, 'w'), default_flow_style=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
