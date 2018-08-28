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
from shape_producer.estimation_methods_Fall17 import *
from shape_producer.era import Run2017ReReco31Mar
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.channel import MTMSSM2017 as MT
from shape_producer.channel import ETMSSM2017 as ET
from shape_producer.channel import TTMSSM2017 as TT

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


    # Era
    era = Run2017ReReco31Mar(args.datasets)


    # Channels and processes
    # yapf: disable
    directory = args.directory
    #~ et_friend_directory = args.et_friend_directory
    #~ mt_friend_directory = args.mt_friend_directory
    #~ tt_friend_directory = args.tt_friend_directory
    et_friend_directory = []
    mt_friend_directory = []
    tt_friend_directory = []
    mt = MT()
    mt.cuts.remove("tau_iso")
    mt.cuts.add(Cut("(byTightIsolationMVArun2017v2DBoldDMwLT2017_2<0.5&&byTightIsolationMVArun2017v2DBoldDMwLT2017_2>0.5)", "tau_anti_iso"))
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationLT  (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationLT  (era, directory, mt, friend_directory=mt_friend_directory)),
        "W"     : Process("W",        WEstimation     (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationLT (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationLT (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimationLT (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimationLT (era, directory, mt, friend_directory=mt_friend_directory))
        #"EWKZ"  : Process("EWKZ",     EWKZEstimation  (era, directory, mt, friend_directory=mt_friend_directory))
        }

    et = ET()
    et.cuts.remove("tau_iso")
    et.cuts.add(Cut("(byTightIsolationMVArun2017v2DBoldDMwLT2017_2<0.5&&byVLooseIsolationMVArun2v1DBoldDMwLT_2>0.5)", "tau_anti_iso"))
    et_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, et, friend_directory=et_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, et, friend_directory=et_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationLT(era, directory, et, friend_directory=et_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationLT  (era, directory, et, friend_directory=et_friend_directory)),
        "W"     : Process("W",        WEstimation     (era, directory, et, friend_directory=et_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationLT (era, directory, et, friend_directory=et_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationLT (era, directory, et, friend_directory=et_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimationLT (era, directory, et, friend_directory=et_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimationLT (era, directory, et, friend_directory=et_friend_directory))
        #"EWKZ"  : Process("EWKZ",     EWKZEstimation  (era, directory, et, friend_directory=et_friend_directory))
        }

    #in tt two 'channels' are needed: antiisolated region for each tau respectively
    tt1 = TT()
    tt1.cuts.remove("tau_1_iso")
    tt1.cuts.add(Cut("(byTightIsolationMVArun2017v2DBoldDMwLT2017_1<0.5&&byVLooseIsolationMVArun2v1DBoldDMwLT_1>0.5)", "tau_1_anti_iso"))
    tt1_processes = {
        "data"  : Process("data_obs", DataEstimation (era, directory, tt1, friend_directory=tt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimationTT(era, directory, tt1, friend_directory=tt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationTT (era, directory, tt1, friend_directory=tt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationTT (era, directory, tt1, friend_directory=tt_friend_directory)),
        "W"     : Process("W",        WEstimation    (era, directory, tt1, friend_directory=tt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationTT(era, directory, tt1, friend_directory=tt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationTT(era, directory, tt1, friend_directory=tt_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimationTT(era, directory, tt1, friend_directory=tt_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimationTT(era, directory, tt1, friend_directory=tt_friend_directory))
        #"EWKZ"  : Process("EWKZ",     EWKZEstimation (era, directory, tt1, friend_directory=tt_friend_directory)),
        }
    tt2 = TT()
    tt2.cuts.remove("tau_2_iso")
    tt2.cuts.add(Cut("(byTightIsolationMVArun2017v2DBoldDMwLT2017_2<0.5&&byVLooseIsolationMVArun2v1DBoldDMwLT_2>0.5)", "tau_2_anti_iso"))
    tt2_processes = {
        "data"  : Process("data_obs", DataEstimation (era, directory, tt2, friend_directory=tt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimationTT(era, directory, tt2, friend_directory=tt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationTT (era, directory, tt2, friend_directory=tt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationTT (era, directory, tt2, friend_directory=tt_friend_directory)),
        "W"     : Process("W",        WEstimation    (era, directory, tt2, friend_directory=tt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationTT(era, directory, tt2, friend_directory=tt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationTT(era, directory, tt2, friend_directory=tt_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimationTT(era, directory, tt2, friend_directory=tt_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimationTT(era, directory, tt2, friend_directory=tt_friend_directory))
        #"EWKZ"  : Process("EWKZ",     EWKZEstimation (era, directory, tt2, friend_directory=tt_friend_directory)),
        }

    # Variables and categories
    binning = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
    variable = "m_vis"
    label = "m_vis"
    config = yaml.load(open("fake-factors/config.yaml"))
    if not args.config in config.keys():
        logger.critical("Requested config key %s not available in fake-factors/config.yaml!" % args.config)
        raise Exception
    config = config[args.config]

    et_categories = []
    # Analysis shapes
    et_categories.append(
        Category(
            label,
            et,
            Cuts(),
            variable=Variable(config["et"]["expression"], VariableBinning(config["et"]["binning"]))))
    mt_categories = []
    # Analysis shapes
    mt_categories.append(
        Category(
            label,
            mt,
            Cuts(),
            variable=Variable(config["mt"]["expression"], VariableBinning(config["mt"]["binning"]))))
    tt1_categories = []
    tt2_categories = []
    # Analysis shapes
    tt1_categories.append(
        Category(
            "tt1_"+label,
            tt1,
            Cuts(),
            variable=Variable(config["tt"]["expression"], VariableBinning(config["tt"]["binning"]))))
    tt2_categories.append(
        Category(
            "tt2_"+label,
            tt2,
            Cuts(),
            variable=Variable(config["tt"]["expression"], VariableBinning(config["tt"]["binning"]))))

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
