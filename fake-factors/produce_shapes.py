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
from shape_producer.channel import ETSM, MTSM, TTSM

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
    if "2016" in args.era:
        from shape_producer.estimation_methods_2016 import DataEstimation, HTTEstimation, ggHEstimation, ggHEstimation_0J, ggHEstimation_1J, ggHEstimation_GE2J, ggHEstimation_VBFTOPO, qqHEstimation, qqHEstimation_VBFTOPO_JET3VETO, qqHEstimation_VBFTOPO_JET3, qqHEstimation_REST, qqHEstimation_PTJET1_GT200, VHEstimation, ZTTEstimation, ZTTEstimationTT, ZLEstimationMTSM, ZLEstimationETSM, ZLEstimationTT, ZJEstimationMT, ZJEstimationET, ZJEstimationTT, WEstimation, TTTEstimationMT, TTTEstimationET, TTTEstimationTT, TTJEstimationMT, TTJEstimationET, TTJEstimationTT, VVTEstimationLT, VVJEstimationLT, VVTEstimationTT, VVJEstimationTT, EWKZEstimation, QCDEstimationMT, QCDEstimationET, QCDEstimationTT, ZTTEmbeddedEstimation, TTLEstimationMT, TTLEstimationET, TTLEstimationTT, TTTTEstimationMT, TTTTEstimationET
        from shape_producer.era import Run2016
        era = Run2016(args.datasets)
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # Channels and processes
    # yapf: disable
    directory = args.directory
    et_friend_directory = args.et_friend_directory
    mt_friend_directory = args.mt_friend_directory
    tt_friend_directory = args.tt_friend_directory

    mt = MTSM()
    mt.cuts.remove("tau_iso")
    mt.cuts.add(Cut("(byTightIsolationMVArun2v1DBoldDMwLT_2<0.5&&byLooseIsolationMVArun2v1DBoldDMwLT_2>0.5)", "tau_anti_iso"))
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationMTSM(era, directory, mt, friend_directory=mt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationMT  (era, directory, mt, friend_directory=mt_friend_directory)),
        "W"     : Process("W",        WEstimation     (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationMT (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationMT (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimationLT (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimationLT (era, directory, mt, friend_directory=mt_friend_directory))
        #"EWKZ"  : Process("EWKZ",     EWKZEstimation  (era, directory, mt, friend_directory=mt_friend_directory))
        }

    et = ETSM()
    et.cuts.remove("tau_iso")
    et.cuts.add(Cut("(byTightIsolationMVArun2v1DBoldDMwLT_2<0.5&&byLooseIsolationMVArun2v1DBoldDMwLT_2>0.5)", "tau_anti_iso"))
    et_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, et, friend_directory=et_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, et, friend_directory=et_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationETSM(era, directory, et, friend_directory=et_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationET  (era, directory, et, friend_directory=et_friend_directory)),
        "W"     : Process("W",        WEstimation     (era, directory, et, friend_directory=et_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationET (era, directory, et, friend_directory=et_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationET (era, directory, et, friend_directory=et_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimationLT (era, directory, et, friend_directory=et_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimationLT (era, directory, et, friend_directory=et_friend_directory))
        #"EWKZ"  : Process("EWKZ",     EWKZEstimation  (era, directory, et, friend_directory=et_friend_directory))
        }

    #in tt two 'channels' are needed: antiisolated region for each tau respectively
    tt1 = TTSM()
    tt1.cuts.remove("tau_1_iso")
    tt1.cuts.add(Cut("(byTightIsolationMVArun2v1DBoldDMwLT_1<0.5&&byLooseIsolationMVArun2v1DBoldDMwLT_1>0.5)", "tau_1_anti_iso"))
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
    tt2 = TTSM()
    tt2.cuts.remove("tau_2_iso")
    tt2.cuts.add(Cut("(byTightIsolationMVArun2v1DBoldDMwLT_2<0.5&&byLooseIsolationMVArun2v1DBoldDMwLT_2>0.5)", "tau_2_anti_iso"))
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
    binning = ConstantBinning(1, 0.0, 2.0)
    count_var = Variable("1.0", binning)

    et_categories = []
    # Analysis shapes
    for i, label in enumerate(["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"]):
        et_categories.append(
            Category(
                label,
                et,
                Cuts(
                    Cut("et_max_index=={index}".format(index=i), "exclusive_score")),
                variable=count_var))
    mt_categories = []
    # Analysis shapes
    for i, label in enumerate(["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"]):
        mt_categories.append(
            Category(
                label,
                mt,
                Cuts(
                    Cut("mt_max_index=={index}".format(index=i), "exclusive_score")),
                variable=count_var))
    tt1_categories = []
    tt2_categories = []
    # Analysis shapes
    for i, label in enumerate(["ggh", "qqh", "ztt", "noniso", "misc"]):
        tt1_categories.append(
            Category(
                "tt1_"+label,
                tt1,
                Cuts(
                    Cut("tt_max_index=={index}".format(index=i), "exclusive_score")),
                variable=count_var))
        tt2_categories.append(
            Category(
                "tt2_"+label,
                tt2,
                Cuts(
                    Cut("tt_max_index=={index}".format(index=i), "exclusive_score")),
                variable=count_var))

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
