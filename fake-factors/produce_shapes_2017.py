#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
ROOT.gErrorIgnoreLevel = ROOT.kError

from shape_producer.cutstring import Cut, Cuts, Weight
from shape_producer.systematics import Systematics, Systematic
from shape_producer.categories import Category
from shape_producer.binning import ConstantBinning, VariableBinning
from shape_producer.variable import Variable
from shape_producer.systematic_variations import Nominal, DifferentPipeline, SquareAndRemoveWeight, create_systematic_variations, AddWeight, ReplaceWeight, Relabel
from shape_producer.process import Process
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.channel import ETSM2017, MTSM2017, TTSM2017

from itertools import product

import argparse
import yaml

import logging
logger = logging.getLogger()


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
        "Produce single bin histograms to determine fake factor fractions")

    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--et-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for et."
    )
    parser.add_argument(
        "--mt-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for mt."
    )
    parser.add_argument(
        "--tt-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for tt."
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        type=str,
        help="Key of desired config in yaml config file.")
    parser.add_argument(
        "--datasets", required=True, type=str, help="Kappa datsets database.")
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument(
        "--num-threads",
        default=32,
        type=int,
        help="Number of threads to be used.")
    parser.add_argument(
        "--backend",
        default="classic",
        choices=["classic", "tdf"],
        type=str,
        help="Backend. Use classic or tdf.")
    parser.add_argument(
        "--tag", default="ERA_CHANNEL", type=str, help="Tag of output files.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    logger.info("Set up shape variations.")
    systematics = Systematics(
        "fake-factors/{}_ff_yields.root".format(args.tag),
        num_threads=args.num_threads)

    # Era selection
    if "2017" in args.era:
        from shape_producer.estimation_methods_Fall17 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, ggHEstimation_0J, ggHEstimation_1J_PTH_0_60, ggHEstimation_1J_PTH_60_120, ggHEstimation_1J_PTH_120_200, ggHEstimation_1J_PTH_GT200, ggHEstimation_GE2J_PTH_0_60, ggHEstimation_GE2J_PTH_60_120, ggHEstimation_GE2J_PTH_120_200, ggHEstimation_GE2J_PTH_GT200, ggHEstimation_VBFTOPO_JET3, ggHEstimation_VBFTOPO_JET3VETO, qqHEstimation, qqHEstimation_VBFTOPO_JET3VETO, qqHEstimation_VBFTOPO_JET3, qqHEstimation_REST, qqHEstimation_VH2JET, qqHEstimation_PTJET1_GT200

        from shape_producer.era import Run2017
        era = Run2017(args.datasets)
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # Channels and processes
    # yapf: disable
    directory = args.directory
    et_friend_directory = args.et_friend_directory
    mt_friend_directory = args.mt_friend_directory
    tt_friend_directory = args.tt_friend_directory

    mt = MTSM2017()
    mt.cuts.remove("tau_iso")
    mt.cuts.add(Cut("(byTightIsolationMVArun2017v2DBoldDMwLT2017_2<0.5&&byVLooseIsolationMVArun2017v2DBoldDMwLT2017_2>0.5)", "tau_anti_iso"))
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, mt, friend_directory=mt_friend_directory))
        }

    et = ETSM2017()
    et.cuts.remove("tau_iso")
    et.cuts.add(Cut("(byTightIsolationMVArun2017v2DBoldDMwLT2017_2<0.5&&byVLooseIsolationMVArun2017v2DBoldDMwLT2017_2>0.5)", "tau_anti_iso"))
    et_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, et, friend_directory=et_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, et, friend_directory=et_friend_directory))
        }

    #in tt two 'channels' are needed: antiisolated region for each tau respectively
    tt1 = TTSM2017()
    tt1.cuts.remove("tau_1_iso")
    tt1.cuts.add(Cut("(byTightIsolationMVArun2017v2DBoldDMwLT2017_1<0.5&&byVLooseIsolationMVArun2017v2DBoldDMwLT2017_1>0.5)", "tau_1_anti_iso"))
    tt1_processes = {
        "data"  : Process("data_obs", DataEstimation	  (era, directory, tt1, friend_directory=tt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation	  (era, directory, tt1, friend_directory=tt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, tt1, friend_directory=tt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, tt1, friend_directory=tt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation	  (era, directory, tt1, friend_directory=tt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimation	  (era, directory, tt1, friend_directory=tt_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation	  (era, directory, tt1, friend_directory=tt_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation	  (era, directory, tt1, friend_directory=tt_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimation	  (era, directory, tt1, friend_directory=tt_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation	  (era, directory, tt1, friend_directory=tt_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, tt1, friend_directory=tt_friend_directory))
        }
    tt2 = TTSM2017()
    tt2.cuts.remove("tau_2_iso")
    tt2.cuts.add(Cut("(byTightIsolationMVArun2017v2DBoldDMwLT2017_2<0.5&&byVLooseIsolationMVArun2017v2DBoldDMwLT2017_2>0.5)", "tau_2_anti_iso"))
    tt2_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, tt2, friend_directory=tt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, tt2, friend_directory=tt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, tt2, friend_directory=tt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, tt2, friend_directory=tt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, tt2, friend_directory=tt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, tt2, friend_directory=tt_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, tt2, friend_directory=tt_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, tt2, friend_directory=tt_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, tt2, friend_directory=tt_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, tt2, friend_directory=tt_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, tt2, friend_directory=tt_friend_directory))
        }

    # Variables and categories
    config = yaml.load(open("fake-factors/config.yaml"))
    if not args.config in config.keys():
        logger.critical("Requested config key %s not available in fake-factors/config.yaml!" % args.config)
        raise Exception
    config = config[args.config]

    et_categories = []
    # et
    et_categories.append(
        Category(
            "inclusive",
            et,
            Cuts(),
            variable=Variable(args.config, VariableBinning(config["et"]["binning"]), config["et"]["expression"])))
    for i, label in enumerate(["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"]):
        et_categories.append(
            Category(
                label,
                et,
                Cuts(
                    Cut("et_max_index=={index}".format(index=i), "exclusive_score")),
                variable=Variable(args.config, VariableBinning(config["et"]["binning"]), config["et"]["expression"])))
    mt_categories = []
    # mt
    mt_categories.append(
        Category(
            "inclusive",
            mt,
            Cuts(),
            variable=Variable(args.config, VariableBinning(config["mt"]["binning"]), config["mt"]["expression"])))
    for i, label in enumerate(["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"]):
        mt_categories.append(
            Category(
                label,
                mt,
                Cuts(
                    Cut("mt_max_index=={index}".format(index=i), "exclusive_score")),
                variable=Variable(args.config, VariableBinning(config["mt"]["binning"]), config["mt"]["expression"])))
    tt1_categories = []
    tt2_categories = []
    # tt
    tt1_categories.append(
        Category(
            "tt1_inclusive",
            tt1,
            Cuts(),
            variable=Variable(args.config, VariableBinning(config["tt"]["binning"]), config["tt"]["expression"])))
    tt2_categories.append(
        Category(
            "tt2_inclusive",
            tt2,
            Cuts(),
            variable=Variable(args.config, VariableBinning(config["tt"]["binning"]), config["tt"]["expression"])))
    for i, label in enumerate(["ggh", "qqh", "ztt", "noniso", "misc"]):
        tt1_categories.append(
            Category(
                "tt1_"+label,
                tt1,
                Cuts(
                    Cut("tt_max_index=={index}".format(index=i), "exclusive_score")),
                variable=Variable(args.config, VariableBinning(config["tt"]["binning"]), config["tt"]["expression"])))
        tt2_categories.append(
            Category(
                "tt2_"+label,
                tt2,
                Cuts(
                    Cut("tt_max_index=={index}".format(index=i), "exclusive_score")),
                variable=Variable(args.config, VariableBinning(config["tt"]["binning"]), config["tt"]["expression"])))

    # Nominal histograms
    # yapf: enable
    for process, category in product(et_processes.values(), et_categories):
        systematics.add(
            Systematic(
                category=category,
                process=process,
                analysis="smhtt",
                era=era,
                variation=Nominal(),
                mass="125"))

    for process, category in product(mt_processes.values(), mt_categories):
        systematics.add(
            Systematic(
                category=category,
                process=process,
                analysis="smhtt",
                era=era,
                variation=Nominal(),
                mass="125"))

    for process, category in product(tt1_processes.values(), tt1_categories):
        systematics.add(
            Systematic(
                category=category,
                process=process,
                analysis="smhtt",
                era=era,
                variation=Nominal(),
                mass="125"))

    for process, category in product(tt2_processes.values(), tt2_categories):
        systematics.add(
            Systematic(
                category=category,
                process=process,
                analysis="smhtt",
                era=era,
                variation=Nominal(),
                mass="125"))

    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_produce_shapes.log".format(args.tag), logging.INFO)
    main(args)
