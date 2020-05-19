#!/usr/bin/env python

import ROOT

ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import yaml
import copy

from shape_producer.cutstring import Weights, Weight
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
        "--training_stxs1p1",
        required=False,
        default=False,
        action='store_true',
        help="Train on stage1p1 categories"
    )
    parser.add_argument(
        "--training_inclusive",
        required=False,
        default=False,
        action="store_true",
        help="Train on inclusive categories"
    )
    parser.add_argument(
        "--training-jetfakes-estimation-method",
        required=True,
        help="Estimate the jet fakes with ff (FakeFactor) or mc (Monte Carlo) ?")
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
    logger.debug("Channel" + args.channel + " Era " + args.era)

    # Define era
    if "2016" in args.era:
        from shape_producer.estimation_methods_2016 import DataEstimation, ggHEstimation, qqHEstimation, \
            ZTTEstimation, ZLEstimation, ZJEstimation, TTTEstimation, TTJEstimation, \
            ZTTEmbeddedEstimation, TTLEstimation, \
            EWKZEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation

        from shape_producer.era import Run2016
        era = Run2016(args.database)

    elif "2017" in args.era:
        from shape_producer.estimation_methods_2017 import DataEstimation, ZTTEstimation, ZJEstimation, ZLEstimation, \
            TTLEstimation, TTJEstimation, TTTEstimation, VVTEstimation, VVJEstimation, VVLEstimation, WEstimation, \
            ggHEstimation, qqHEstimation, EWKZEstimation, ZTTEmbeddedEstimation

        from shape_producer.era import Run2017
        era = Run2017(args.database)

    elif "2018" in args.era:
        from shape_producer.estimation_methods_2018 import DataEstimation, ZTTEstimation, ZJEstimation, ZLEstimation, \
            TTLEstimation, TTJEstimation, TTTEstimation, VVTEstimation, VVJEstimation, VVLEstimation, WEstimation, \
            ggHEstimation, qqHEstimation, EWKZEstimation, ZTTEmbeddedEstimation

        from shape_producer.era import Run2018
        era = Run2018(args.database)
    else:
        logger.fatal("Era {} is not implemented.".format(args.era))
        raise Exception

    def estimationMethodAndClassMapGenerator():
        ###### common processes
        if args.training_stxs1p1:
            classes_map = {
# class1
"ggH_GG2H_PTH_200_300125": "ggh_PTH_200_300",
# class2
"ggH_GG2H_PTH_300_450125": "ggh_PTHGT300",
"ggH_GG2H_PTH_450_650125": "ggh_PTHGT300",
"ggH_GG2H_PTH_GT650125": "ggh_PTHGT300",
# class3
"ggH_GG2H_0J_PTH_0_10125": "ggh_0J_PTH_0_10",
# class4
"ggH_GG2H_0J_PTH_GT10125": "ggh_0J_PTH_GT10",
# class5
"ggH_GG2H_1J_PTH_0_60125": "ggh_1J_PTH0to60",
# class6
"ggH_GG2H_1J_PTH_60_120125": "ggh_1J_PTH60to120",
# class7
"ggH_GG2H_1J_PTH_120_200125": "ggh_1J_PTH120to200",
# class8
"ggH_GG2H_GE2J_MJJ_0_350_PTH_0_60125": "ggh_2J_PTH0to60",
# class9
"ggH_GG2H_GE2J_MJJ_0_350_PTH_60_120125": "ggh_2J_PTH60to120",
# class10
"ggH_GG2H_GE2J_MJJ_0_350_PTH_120_200125": "ggh_2J_PTH120to200",
# class11
"ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125": "ggh_vbftopo",
"ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125": "ggh_vbftopo",
"ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125": "ggh_vbftopo",
"ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125": "ggh_vbftopo",
# class12
"qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125": "qqh_vbftopo_lowmjj",
"qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125": "qqh_vbftopo_lowmjj",
# class13
"qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125": "qqh_vbftopo_highmjj",
"qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125": "qqh_vbftopo_highmjj",
# class14
"qqH_QQ2HQQ_GE2J_MJJ_0_60125": "qqh_2J",
"qqH_QQ2HQQ_GE2J_MJJ_60_120125": "qqh_2J",
"qqH_QQ2HQQ_GE2J_MJJ_120_350125": "qqh_2J",
# class15
"qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200125": "qqh_PTHGT200",
            }
            estimationMethodList = [
ggHEstimation("ggH_GG2H_PTH_200_300125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_PTH_300_450125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_PTH_450_650125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_PTH_GT650125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_0J_PTH_0_10125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_0J_PTH_GT10125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_1J_PTH_0_60125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_1J_PTH_60_120125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_1J_PTH_120_200125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_GE2J_MJJ_0_350_PTH_0_60125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_GE2J_MJJ_0_350_PTH_60_120125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_GE2J_MJJ_0_350_PTH_120_200125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125", era, args.base_path, channel),
qqHEstimation("qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125", era, args.base_path, channel),
qqHEstimation("qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125", era, args.base_path, channel),
ggHEstimation("ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125", era, args.base_path, channel),
qqHEstimation("qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125", era, args.base_path, channel),
qqHEstimation("qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125", era, args.base_path, channel),
qqHEstimation("qqH_QQ2HQQ_GE2J_MJJ_0_60125", era, args.base_path, channel),
qqHEstimation("qqH_QQ2HQQ_GE2J_MJJ_60_120125", era, args.base_path, channel),
qqHEstimation("qqH_QQ2HQQ_GE2J_MJJ_120_350125", era, args.base_path, channel),
qqHEstimation("qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200125", era, args.base_path, channel),
            ]
        elif args.training_inclusive:
            classes_map = {
                "ggH125": "xxh",
                "qqH125": "xxh",
            }
            estimationMethodList = [
                ggHEstimation("ggH125", era, args.base_path, channel),
                qqHEstimation("qqH125", era, args.base_path, channel),

            ]
        else:
            classes_map = {
                "ggH125": "ggh",
                "qqH125": "qqh",
            }
            estimationMethodList = [
                ggHEstimation("ggH125", era, args.base_path, channel),
                qqHEstimation("qqH125", era, args.base_path, channel),

            ]
        estimationMethodList.extend([
            EWKZEstimation(era, args.base_path, channel),
            VVLEstimation(era, args.base_path, channel)
        ])
        classes_map["EWKZ"]="misc"
        ##### TT* zl,zj processes
        estimationMethodList.extend([
            TTLEstimation(era, args.base_path, channel),
            ZLEstimation(era, args.base_path, channel)
        ])
        if args.channel == "tt":
            classes_map.update({
                "TTL": "misc",
                "ZL": "misc",
                "VVL": "misc"
            })
        ## not TTJ,ZJ for em
        elif args.channel == "em":
            classes_map.update({
                "TTL": "tt",
                "ZL": "misc",
                "VVL": "db"
            })
        else:
            classes_map.update({
                "TTL": "tt",
                "ZL": "zll",
                "VVL": "misc"
            })
        ######## Check for emb vs MC
        if args.training_z_estimation_method == "emb":
            classes_map["EMB"] = "emb"
            estimationMethodList.extend([
                ZTTEmbeddedEstimation(era, args.base_path, channel)])
        elif args.training_z_estimation_method == "mc":
            classes_map["ZTT"] = "ztt"
            estimationMethodList.extend([
                ZTTEstimation(era, args.base_path, channel),
                TTTEstimation(era, args.base_path, channel),
                VVTEstimation(era, args.base_path, channel)
            ])
            if args.channel == "tt":
                classes_map.update({
                    "TTT": "misc",
                    "VVT": "misc"
                })
            ## not TTJ,ZJ for em
            elif args.channel == "em":
                classes_map.update({
                    "TTT": "tt",
                    "VVT": "db"
                })
            else:
                classes_map.update({
                    "TTT": "tt",
                    "VVT": "misc"
                })

        else:
            logger.fatal("No valid training-z-estimation-method! Options are emb, mc. Argument was {}".format(
                args.training_z_estimation_method))
            raise Exception

        if args.training_jetfakes_estimation_method == "ff" and args.channel != "em":
            classes_map.update({
                "ff": "ff"
            })
        elif args.training_jetfakes_estimation_method == "mc" or args.channel == "em":
            # less data-> less categories for tt
            if args.channel == "tt":
                classes_map.update({
                    "TTJ": "misc",
                    "ZJ": "misc"
                })
            ## not TTJ,ZJ for em
            elif args.channel != "em":
                classes_map.update({
                    "TTJ": "tt",
                    "ZJ": "zll"
                })
            if args.channel != "em":
                classes_map.update({
                    "VVJ": "misc"
                })
                estimationMethodList.extend([
                    VVJEstimation(era, args.base_path, channel),
                    ZJEstimation(era, args.base_path, channel),
                    TTJEstimation(era, args.base_path, channel)
                ])
            ###w:
            estimationMethodList.extend([WEstimation(era, args.base_path, channel)])
            if args.channel in ["et", "mt"]:
                classes_map["W"] = "w"
            else:
                classes_map["W"] = "misc"
            ### QCD class
            if args.channel == "tt":
                classes_map["QCD"] = "noniso"
            else:
                classes_map["QCD"] = "ss"

        else:
            logger.fatal("No valid training-jetfakes-estimation-method! Options are ff, mc. Argument was {}".format(
                args.training_jetfakes_estimation_method))
            raise Exception
        return ([classes_map, estimationMethodList])

    channelDict = {}
    channelDict["2016"] = {"mt": MTSM2016(), "et": ETSM2016(), "tt": TTSM2016(), "em": EMSM2016()}
    channelDict["2017"] = {"mt": MTSM2017(), "et": ETSM2017(), "tt": TTSM2017(), "em": EMSM2017()}
    channelDict["2018"] = {"mt": MTSM2018(), "et": ETSM2018(), "tt": TTSM2018(), "em": EMSM2018()}

    channel = channelDict[args.era][args.channel]

    # Set up `processes` part of config
    output_config["processes"] = {}

    # Additional cuts
    additional_cuts = Cuts()
    logger.warning("Use additional cuts for mt: %s", additional_cuts.expand())

    classes_map, estimationMethodList = estimationMethodAndClassMapGenerator()

    ### disables all other estimation methods
    # classes_map={"ff":"ff"}
    # estimationMethodList=[]

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

    if args.training_jetfakes_estimation_method == "mc" or args.channel == "em":
        if args.training_jetfakes_estimation_method == "ff":
            logger.warn("ff+em: using mc for em channel")
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
                Cut("byTightDeepTau2017v2p1VSjet_2<0.5", "tau_2_iso"))
            channel_qcd.cuts.add(
                Cut("byMediumDeepTau2017v2p1VSjet_2>0.5", "tau_2_iso_loose"))

        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + channel_qcd.cuts + additional_cuts).expand(),
            "weight_string": estimation.get_weights().extract(),
            "class": classes_map[estimation.name]
        }
    else:  ## ff and not em
        estimation = DataEstimation(era, args.base_path, channel)
        estimation.name = "ff"
        aiso = copy.deepcopy(channel)
        if args.channel in ["et", "mt"]:
            aisoCut = Cut(
                "byTightDeepTau2017v2p1VSjet_2<0.5&&byVLooseDeepTau2017v2p1VSjet_2>0.5",
                "tau_aiso")
            fakeWeightstring = "ff2_nom"
            aiso.cuts.remove("tau_iso")
        elif args.channel == "tt":
            aisoCut = Cut(
                "(byTightDeepTau2017v2p1VSjet_2>0.5&&byTightDeepTau2017v2p1VSjet_1<0.5&&byVLooseDeepTau2017v2p1VSjet_1>0.5)||(byTightDeepTau2017v2p1VSjet_1>0.5&&byTightDeepTau2017v2p1VSjet_2<0.5&&byVLooseDeepTau2017v2p1VSjet_2>0.5)",
                "tau_aiso")
            fakeWeightstring = "(0.5*ff1_nom*(byTightDeepTau2017v2p1VSjet_1<0.5)+0.5*ff2_nom*(byTightDeepTau2017v2p1VSjet_2<0.5))"
            aiso.cuts.remove("tau_1_iso")
            aiso.cuts.remove("tau_2_iso")
        # self._nofake_processes = [copy.deepcopy(p) for p in nofake_processes]

        aiso.cuts.add(aisoCut)
        additionalWeights = Weights(Weight(fakeWeightstring, "fake_factor"))

        output_config["processes"][estimation.name] = {
            "files": [
                str(f).replace(args.base_path.rstrip("/") + "/", "")
                for f in estimation.get_files()
            ],
            "cut_string": (estimation.get_cuts() + aiso.cuts).expand(),
            "weight_string": (estimation.get_weights() + additionalWeights).extract(),
            "class": classes_map[estimation.name]
        }

    output_config["datasets"] = [args.output_path + "/fold" + fold + "_training_dataset.root" for fold in ["0", "1"]]
    #####################################
    # Write output config
    logger.info("Write config to file: {}".format(args.output_config))
    yaml.dump(output_config, open(args.output_config, 'w'), default_flow_style=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
