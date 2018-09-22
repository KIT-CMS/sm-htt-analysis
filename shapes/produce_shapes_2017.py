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
        description="Produce shapes for 2016 Standard Model analysis.")

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
        from shape_producer.estimation_methods_Fall17 import DataEstimation, ZTTEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, qqHEstimation, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, EWKZEstimation

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
        }
    mt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VVT", "VVJ", "EWKZ"]],
            mt_processes["data"], friend_directory=mt_friend_directory, extrapolation_factor=1.00))

    et = ETMSSM2017()
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
        "W"     : Process("W",        WEstimation         (era, directory, et, friend_directory=et_friend_directory)),
        "EWKZ"  : Process("EWKZ",     EWKZEstimation      (era, directory, et, friend_directory=et_friend_directory)),
        "ggH"   : Process("ggH125",   ggHEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        }
    et_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, et,
            [et_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VVT", "VVJ", "EWKZ"]],
            et_processes["data"], friend_directory=et_friend_directory, extrapolation_factor=1.00))

    tt = TTMSSM2017()
    tt_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, tt, friend_directory=tt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
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

    # Nominal histograms
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
    # TODO

    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_produce_shapes.log".format(args.tag), logging.INFO)
    main(args)
