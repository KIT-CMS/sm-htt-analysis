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
from shape_producer.channel import ETMSSM2017, MTMSSM2017, TTMSSM2017

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
        description="Produce shapes for 2017 Standard Model analysis.")

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
        "--fake-factor-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing friend trees to data files with fake factors."
    )
    parser.add_argument(
        "--datasets", required=True, type=str, help="Kappa datsets database.")
    parser.add_argument(
        "--binning", required=True, type=str, help="Binning configuration.")
    parser.add_argument(
        "--channels",
        default=[],
        nargs='+',
        type=str,
        help="Channels to be considered.")
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument(
        "--gof-channel",
        default=None,
        type=str,
        help="Channel for goodness of fit shapes.")
    parser.add_argument(
        "--gof-variable",
        type=str,
        help="Variable for goodness of fit shapes.")
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
    parser.add_argument(
        "--skip-systematic-variations",
        default=False,
        type=str,
        help="Do not produce the systematic variations.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    logger.info("Set up shape variations.")
    systematics = Systematics(
        "{}_shapes.root".format(args.tag),
        num_threads=args.num_threads,
        skip_systematic_variations=args.skip_systematic_variations)

    # Era selection
    if "2017" in args.era:
        from shape_producer.estimation_methods_Fall17 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, ggHEstimation_0J, ggHEstimation_1J_PTH_0_60, ggHEstimation_1J_PTH_60_120, ggHEstimation_1J_PTH_120_200, ggHEstimation_1J_PTH_GT200, ggHEstimation_GE2J_PTH_0_60, ggHEstimation_GE2J_PTH_60_120, ggHEstimation_GE2J_PTH_120_200, ggHEstimation_GE2J_PTH_GT200, ggHEstimation_VBFTOPO_JET3, ggHEstimation_VBFTOPO_JET3VETO, qqHEstimation, qqHEstimation_VBFTOPO_JET3VETO, qqHEstimation_VBFTOPO_JET3, qqHEstimation_REST, qqHEstimation_VH2JET, qqHEstimation_PTJET1_GT200, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, EWKZEstimation

        from shape_producer.era import Run2017ReReco31Mar as Run2017
        era = Run2017(args.datasets)

    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # Channels and processes
    # yapf: disable
    directory = args.directory
    # TODO: Remove dummies
    et_friend_directory = args.et_friend_directory
    mt_friend_directory = args.mt_friend_directory
    tt_friend_directory = args.tt_friend_directory
    ff_friend_directory = []#args.fake_factor_friend_directory
    mt = MTMSSM2017()
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, mt, friend_directory=mt_friend_directory)),
        "EWKZ"  : Process("EWKZ",     EWKZEstimation      (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH"   : Process("ggH125",   ggHEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_0J"               : Process("ggH_0J125",               ggHEstimation_0J              (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_1J_PTH_0_60"      : Process("ggH_1J_PTH_0_60125",      ggHEstimation_1J_PTH_0_60     (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_1J_PTH_60_120"    : Process("ggH_1J_PTH_60_120125",    ggHEstimation_1J_PTH_60_120   (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_1J_PTH_120_200"   : Process("ggH_1J_PTH_120_200125",   ggHEstimation_1J_PTH_120_200  (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_1J_PTH_GT200"     : Process("ggH_1J_PTH_GT200125",     ggHEstimation_1J_PTH_GT200    (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_GE2J_PTH_0_60"    : Process("ggH_GE2J_PTH_0_60125",    ggHEstimation_GE2J_PTH_0_60   (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_GE2J_PTH_60_120"  : Process("ggH_GE2J_PTH_60_120125",  ggHEstimation_GE2J_PTH_60_120 (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_GE2J_PTH_120_200" : Process("ggH_GE2J_PTH_120_200125", ggHEstimation_GE2J_PTH_120_200(era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_GE2J_PTH_GT200"   : Process("ggH_GE2J_PTH_GT200125",   ggHEstimation_GE2J_PTH_GT200  (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_VBFTOPO_JET3VETO" : Process("ggH_VBFTOPO_JET3VETO125", ggHEstimation_VBFTOPO_JET3VETO(era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH_VBFTOPO_JET3"     : Process("ggH_VBFTOPO_JET3125",     ggHEstimation_VBFTOPO_JET3    (era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH_VBFTOPO_JET3VETO" : Process("qqH_VBFTOPO_JET3VETO125", qqHEstimation_VBFTOPO_JET3VETO(era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH_VBFTOPO_JET3"     : Process("qqH_VBFTOPO_JET3125",     qqHEstimation_VBFTOPO_JET3    (era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH_REST"             : Process("qqH_REST125",             qqHEstimation_REST            (era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH_VH2JET"           : Process("qqH_VH2JET125",           qqHEstimation_VH2JET          (era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH_PTJET1_GT200"     : Process("qqH_PTJET1_GT200125",     qqHEstimation_PTJET1_GT200    (era, directory, mt, friend_directory=mt_friend_directory)),
        }
    mt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VVT", "VVJ", "EWKZ"]],
            mt_processes["data"], friend_directory=mt_friend_directory, extrapolation_factor=1.00))

    et = ETMSSM2017()
    et_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, et, friend_directory=et_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, et, friend_directory=et_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, et, friend_directory=et_friend_directory)),
        "EWKZ"  : Process("EWKZ",     EWKZEstimation      (era, directory, et, friend_directory=et_friend_directory)),
        "ggH"   : Process("ggH125",   ggHEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "ggH_0J"               : Process("ggH_0J125",               ggHEstimation_0J              (era, directory, et, friend_directory=et_friend_directory)),
        "ggH_1J_PTH_0_60"      : Process("ggH_1J_PTH_0_60125",      ggHEstimation_1J_PTH_0_60     (era, directory, et, friend_directory=et_friend_directory)),
        "ggH_1J_PTH_60_120"    : Process("ggH_1J_PTH_60_120125",    ggHEstimation_1J_PTH_60_120   (era, directory, et, friend_directory=et_friend_directory)),
        "ggH_1J_PTH_120_200"   : Process("ggH_1J_PTH_120_200125",   ggHEstimation_1J_PTH_120_200  (era, directory, et, friend_directory=et_friend_directory)),
        "ggH_1J_PTH_GT200"     : Process("ggH_1J_PTH_GT200125",     ggHEstimation_1J_PTH_GT200    (era, directory, et, friend_directory=et_friend_directory)),
        "ggH_GE2J_PTH_0_60"    : Process("ggH_GE2J_PTH_0_60125",    ggHEstimation_GE2J_PTH_0_60   (era, directory, et, friend_directory=et_friend_directory)),
        "ggH_GE2J_PTH_60_120"  : Process("ggH_GE2J_PTH_60_120125",  ggHEstimation_GE2J_PTH_60_120 (era, directory, et, friend_directory=et_friend_directory)),
        "ggH_GE2J_PTH_120_200" : Process("ggH_GE2J_PTH_120_200125", ggHEstimation_GE2J_PTH_120_200(era, directory, et, friend_directory=et_friend_directory)),
        "ggH_GE2J_PTH_GT200"   : Process("ggH_GE2J_PTH_GT200125",   ggHEstimation_GE2J_PTH_GT200  (era, directory, et, friend_directory=et_friend_directory)),
        "ggH_VBFTOPO_JET3VETO" : Process("ggH_VBFTOPO_JET3VETO125", ggHEstimation_VBFTOPO_JET3VETO(era, directory, et, friend_directory=et_friend_directory)),
        "ggH_VBFTOPO_JET3"     : Process("ggH_VBFTOPO_JET3125",     ggHEstimation_VBFTOPO_JET3    (era, directory, et, friend_directory=et_friend_directory)),
        "qqH_VBFTOPO_JET3VETO" : Process("qqH_VBFTOPO_JET3VETO125", qqHEstimation_VBFTOPO_JET3VETO(era, directory, et, friend_directory=et_friend_directory)),
        "qqH_VBFTOPO_JET3"     : Process("qqH_VBFTOPO_JET3125",     qqHEstimation_VBFTOPO_JET3    (era, directory, et, friend_directory=et_friend_directory)),
        "qqH_REST"             : Process("qqH_REST125",             qqHEstimation_REST            (era, directory, et, friend_directory=et_friend_directory)),
        "qqH_VH2JET"           : Process("qqH_VH2JET125",           qqHEstimation_VH2JET          (era, directory, et, friend_directory=et_friend_directory)),
        "qqH_PTJET1_GT200"     : Process("qqH_PTJET1_GT200125",     qqHEstimation_PTJET1_GT200    (era, directory, et, friend_directory=et_friend_directory)),
        }
    et_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, et,
            [et_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VVT", "VVJ", "EWKZ"]],
            et_processes["data"], friend_directory=et_friend_directory, extrapolation_factor=1.00))

    tt = TTMSSM2017()
    tt_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, tt, friend_directory=tt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, tt, friend_directory=tt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, tt, friend_directory=tt_friend_directory)),
        "EWKZ"  : Process("EWKZ",     EWKZEstimation      (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH"   : Process("ggH125",   ggHEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_0J"               : Process("ggH_0J125",               ggHEstimation_0J              (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_1J_PTH_0_60"      : Process("ggH_1J_PTH_0_60125",      ggHEstimation_1J_PTH_0_60     (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_1J_PTH_60_120"    : Process("ggH_1J_PTH_60_120125",    ggHEstimation_1J_PTH_60_120   (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_1J_PTH_120_200"   : Process("ggH_1J_PTH_120_200125",   ggHEstimation_1J_PTH_120_200  (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_1J_PTH_GT200"     : Process("ggH_1J_PTH_GT200125",     ggHEstimation_1J_PTH_GT200    (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_GE2J_PTH_0_60"    : Process("ggH_GE2J_PTH_0_60125",    ggHEstimation_GE2J_PTH_0_60   (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_GE2J_PTH_60_120"  : Process("ggH_GE2J_PTH_60_120125",  ggHEstimation_GE2J_PTH_60_120 (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_GE2J_PTH_120_200" : Process("ggH_GE2J_PTH_120_200125", ggHEstimation_GE2J_PTH_120_200(era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_GE2J_PTH_GT200"   : Process("ggH_GE2J_PTH_GT200125",   ggHEstimation_GE2J_PTH_GT200  (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_VBFTOPO_JET3VETO" : Process("ggH_VBFTOPO_JET3VETO125", ggHEstimation_VBFTOPO_JET3VETO(era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH_VBFTOPO_JET3"     : Process("ggH_VBFTOPO_JET3125",     ggHEstimation_VBFTOPO_JET3    (era, directory, tt, friend_directory=tt_friend_directory)),
        "qqH_VBFTOPO_JET3VETO" : Process("qqH_VBFTOPO_JET3VETO125", qqHEstimation_VBFTOPO_JET3VETO(era, directory, tt, friend_directory=tt_friend_directory)),
        "qqH_VBFTOPO_JET3"     : Process("qqH_VBFTOPO_JET3125",     qqHEstimation_VBFTOPO_JET3    (era, directory, tt, friend_directory=tt_friend_directory)),
        "qqH_REST"             : Process("qqH_REST125",             qqHEstimation_REST            (era, directory, tt, friend_directory=tt_friend_directory)),
        "qqH_VH2JET"           : Process("qqH_VH2JET125",           qqHEstimation_VH2JET          (era, directory, tt, friend_directory=tt_friend_directory)),
        "qqH_PTJET1_GT200"     : Process("qqH_PTJET1_GT200125",     qqHEstimation_PTJET1_GT200    (era, directory, tt, friend_directory=tt_friend_directory)),
        }
    tt_processes["QCD"] = Process("QCD", QCDEstimation_ABCD_TT_ISO2(era, directory, tt,
            [tt_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VVT", "VVJ", "EWKZ"]],
            tt_processes["data"], friend_directory=tt_friend_directory))

    # Variables and categories
    binning = yaml.load(open(args.binning))

    et_categories = []
    # Analysis shapes
    if "et" in args.channels:
        classes_et = ["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"]
        for i, label in enumerate(classes_et):
            score = Variable(
                "et_max_score",
                 VariableBinning(binning["analysis"]["et"][label]))
            et_categories.append(
                Category(
                    label,
                    et,
                    Cuts(
                        Cut("et_max_index=={index}".format(index=i), "exclusive_score")),
                    variable=score))
            if label in ["ggh", "qqh"]:
                expression = ""
                for i_e, e in enumerate(binning["stxs_stage1"][label]):
                    offset = (binning["analysis"]["et"][label][-1]-binning["analysis"]["et"][label][0])*i_e
                    expression += "{STXSBIN}*(et_max_score+{OFFSET})".format(STXSBIN=e, OFFSET=offset)
                    if not e is binning["stxs_stage1"][label][-1]:
                        expression += " + "
                score_unrolled = Variable(
                    "et_max_score_unrolled",
                     VariableBinning(binning["analysis"]["et"][label+"_unrolled"]),
                     expression=expression)
                et_categories.append(
                    Category(
                        "{}_unrolled".format(label),
                        et,
                        Cuts(Cut("et_max_index=={index}".format(index=i), "exclusive_score"),
                             Cut("et_max_score>{}".format(1.0/len(classes_et)), "protect_unrolling")),
                        variable=score_unrolled))
    # Goodness of fit shapes
    elif args.gof_channel == "et":
        score = Variable(
                args.gof_variable,
                VariableBinning(binning["gof"]["et"][args.gof_variable]["bins"]),
                expression=binning["gof"]["et"][args.gof_variable]["expression"])
        if "cut" in binning["gof"]["et"][args.gof_variable].keys():
            cuts=Cuts(Cut(binning["gof"]["et"][args.gof_variable]["cut"], "binning"))
        else:
            cuts=Cuts()
        et_categories.append(
            Category(
                args.gof_variable,
                et,
                cuts,
                variable=score))

    mt_categories = []
    # Analysis shapes
    if "mt" in args.channels:
        classes_mt = ["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"]
        for i, label in enumerate(classes_mt):
            score = Variable(
                "mt_max_score",
                 VariableBinning(binning["analysis"]["mt"][label]))
            mt_categories.append(
                Category(
                    label,
                    mt,
                    Cuts(
                        Cut("mt_max_index=={index}".format(index=i), "exclusive_score")),
                    variable=score))
            if label in ["ggh", "qqh"]:
                expression = ""
                for i_e, e in enumerate(binning["stxs_stage1"][label]):
                    offset = (binning["analysis"]["mt"][label][-1]-binning["analysis"]["mt"][label][0])*i_e
                    expression += "{STXSBIN}*(mt_max_score+{OFFSET})".format(STXSBIN=e, OFFSET=offset)
                    if not e is binning["stxs_stage1"][label][-1]:
                        expression += " + "
                score_unrolled = Variable(
                    "mt_max_score_unrolled",
                     VariableBinning(binning["analysis"]["mt"][label+"_unrolled"]),
                     expression=expression)
                mt_categories.append(
                    Category(
                        "{}_unrolled".format(label),
                        mt,
                        Cuts(Cut("mt_max_index=={index}".format(index=i), "exclusive_score"),
                             Cut("mt_max_score>{}".format(1.0/len(classes_mt)), "protect_unrolling")),
                        variable=score_unrolled))
    # Goodness of fit shapes
    elif args.gof_channel == "mt":
        score = Variable(
                args.gof_variable,
                VariableBinning(binning["gof"]["mt"][args.gof_variable]["bins"]),
                expression=binning["gof"]["mt"][args.gof_variable]["expression"])
        if "cut" in binning["gof"]["mt"][args.gof_variable].keys():
            cuts=Cuts(Cut(binning["gof"]["mt"][args.gof_variable]["cut"], "binning"))
        else:
            cuts=Cuts()
        mt_categories.append(
            Category(
                args.gof_variable,
                mt,
                cuts,
                variable=score))

    tt_categories = []
    # Analysis shapes
    if "tt" in args.channels:
        classes_tt = ["ggh", "qqh", "ztt", "noniso", "misc"]
        for i, label in enumerate(classes_tt):
            score = Variable(
                "tt_max_score",
                 VariableBinning(binning["analysis"]["tt"][label]))
            tt_categories.append(
                Category(
                    label,
                    tt,
                    Cuts(
                        Cut("tt_max_index=={index}".format(index=i), "exclusive_score")),
                    variable=score))
            if label in ["ggh", "qqh"]:
                expression = ""
                for i_e, e in enumerate(binning["stxs_stage1"][label]):
                    offset = (binning["analysis"]["tt"][label][-1]-binning["analysis"]["tt"][label][0])*i_e
                    expression += "{STXSBIN}*(tt_max_score+{OFFSET})".format(STXSBIN=e, OFFSET=offset)
                    if not e is binning["stxs_stage1"][label][-1]:
                        expression += " + "
                score_unrolled = Variable(
                    "tt_max_score_unrolled",
                     VariableBinning(binning["analysis"]["tt"][label+"_unrolled"]),
                     expression=expression)
                tt_categories.append(
                    Category(
                        "{}_unrolled".format(label),
                        tt,
                        Cuts(Cut("tt_max_index=={index}".format(index=i), "exclusive_score"),
                             Cut("tt_max_score>{}".format(1.0/len(classes_tt)), "protect_unrolling")),
                        variable=score_unrolled))

    # Goodness of fit shapes
    elif args.gof_channel == "tt":
        score = Variable(
                args.gof_variable,
                VariableBinning(binning["gof"]["tt"][args.gof_variable]["bins"]),
                expression=binning["gof"]["tt"][args.gof_variable]["expression"])
        if "cut" in binning["gof"]["tt"][args.gof_variable].keys():
            cuts=Cuts(Cut(binning["gof"]["tt"][args.gof_variable]["cut"], "binning"))
        else:
            cuts=Cuts()
        tt_categories.append(
            Category(
                args.gof_variable,
                tt,
                cuts,
                variable=score))

    # Nominal histograms
    signal_nicks = [
        "ggH", "qqH", "qqH_VBFTOPO_JET3VETO", "qqH_VBFTOPO_JET3",
        "qqH_REST", "qqH_PTJET1_GT200", "qqH_VH2JET", "ggH_0J",
        "ggH_1J_PTH_0_60", "ggH_1J_PTH_60_120", "ggH_1J_PTH_120_200",
        "ggH_1J_PTH_GT200", "ggH_GE2J_PTH_0_60", "ggH_GE2J_PTH_60_120",
        "ggH_GE2J_PTH_120_200", "ggH_GE2J_PTH_GT200", "ggH_VBFTOPO_JET3VETO",
        "ggH_VBFTOPO_JET3"
    ]

    # yapf: enable
    if "et" in [args.gof_channel] + args.channels:
        for process, category in product(et_processes.values(), et_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))
    if "mt" in [args.gof_channel] + args.channels:
        for process, category in product(mt_processes.values(), mt_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))
    if "tt" in [args.gof_channel] + args.channels:
        for process, category in product(tt_processes.values(), tt_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))

    # Shapes variations

    # Tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_t_3prong_13TeV", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_t_1prong_13TeV", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_t_1prong1pizero_13TeV", "tauEsOneProngOnePiZero",
        DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["ZTT", "TTT", "TTL", "VVT", "EWKZ", "EMB"
                             ] + signal_nicks:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # Jet energy scale

    # Inclusive JES shapes
    jet_es_variations = []
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_13TeV", "jecUnc", DifferentPipeline)

    # Splitted JES shapes
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta0to3_13TeV", "jecUncEta0to3", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta0to5_13TeV", "jecUncEta0to5", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta3to5_13TeV", "jecUncEta3to5", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeBal_13TeV", "jecUncRelativeBal",
        DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeSample_13TeV", "jecUncRelativeSample",
        DifferentPipeline)

    for variation in jet_es_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVJ",
                "EWKZ"
        ] + signal_nicks:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # MET energy scale
    # TODO

    # Z pt reweighting
    zpt_variations = create_systematic_variations(
        "CMS_htt_dyShape_13TeV", "zPtReweightWeight", SquareAndRemoveWeight)
    for variation in zpt_variations:
        for process_nick in ["ZTT", "ZL", "ZJ"]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # top pt reweighting
    # TODO

    # jet to tau fake efficiency
    # TODO

    # ZL fakes energy scale
    # TODO

    # Zll reweighting
    # TODO

    # b tagging
    # TODO

    # Embedded event specifics
    mt_decayMode_variations = []
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
            "Down"))
    for variation in mt_decayMode_variations:
        for process_nick in ["EMB"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    et_decayMode_variations = []
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
            "Down"))
    for variation in et_decayMode_variations:
        for process_nick in ["EMB"]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
    tt_decayMode_variations = []
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_13TeV", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
            "Down"))
    for variation in tt_decayMode_variations:
        for process_nick in ["EMB"]:
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)
    # 10% removed events in ttbar simulation (ttbar -> real tau tau events) will be added/subtracted to ZTT shape to use as systematic
    tttautau_process_mt = Process(
        "TTT",
        TTTEstimation(
            era, directory, mt, friend_directory=mt_friend_directory))
    tttautau_process_et = Process(
        "TTT",
        TTTEstimation(
            era, directory, et, friend_directory=et_friend_directory))
    tttautau_process_tt = Process(
        "TTT",
        TTTEstimation(
            era, directory, tt, friend_directory=tt_friend_directory))
    if 'mt' in [args.gof_channel] + args.channels:
        for category in mt_categories:
            mt_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, mt,
                    [mt_processes["EMB"], tttautau_process_mt], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=mt_processes['ZTTpTTTauTauDown'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar_13TeV", "Down"),
                    mass="125"))

            mt_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, mt,
                    [mt_processes["EMB"], tttautau_process_mt], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=mt_processes['ZTTpTTTauTauUp'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar_13TeV", "Up"),
                    mass="125"))

    if 'et' in [args.gof_channel] + args.channels:
        for category in et_categories:
            et_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, et,
                    [et_processes["EMB"], tttautau_process_et], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=et_processes['ZTTpTTTauTauDown'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar_13TeV", "Down"),
                    mass="125"))

            et_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, et,
                    [et_processes["EMB"], tttautau_process_et], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=et_processes['ZTTpTTTauTauUp'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar_13TeV", "Up"),
                    mass="125"))
    if 'tt' in [args.gof_channel] + args.channels:
        for category in tt_categories:
            tt_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "EMB", era, directory, tt,
                    [tt_processes["EMB"], tttautau_process_tt], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=tt_processes['ZTTpTTTauTauDown'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar_13TeV", "Down"),
                    mass="125"))

            tt_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, tt,
                    [tt_processes["EMB"], tttautau_process_tt], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=tt_processes['ZTTpTTTauTauUp'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar_13TeV", "Up"),
                    mass="125"))
 

    # jetfakes
    # TODO

    # Gluon-fusion WG1 uncertainty scheme
    ggh_variations = []
    for unc in [
            "THU_ggH_Mig01", "THU_ggH_Mig12", "THU_ggH_Mu", "THU_ggH_PT120",
            "THU_ggH_PT60", "THU_ggH_Res", "THU_ggH_VBF2j", "THU_ggH_VBF3j",
            "THU_ggH_qmtop"
    ]:
        ggh_variations.append(
            AddWeight("{}_13TeV".format(unc), "{}_weight".format(unc),
                      Weight("({})".format(unc), "{}_weight".format(unc)),
                      "Up"))
        ggh_variations.append(
            AddWeight("{}_13TeV".format(unc), "{}_weight".format(unc),
                      Weight("(1.0/{})".format(unc), "{}_weight".format(unc)),
                      "Down"))
    for variation in ggh_variations:
        for process_nick in [nick for nick in signal_nicks if "ggH" in nick]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_produce_shapes.log".format(args.tag), logging.INFO)
    main(args)
