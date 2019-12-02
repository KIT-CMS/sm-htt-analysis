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
from shape_producer.channel import ETSM2018, MTSM2018, TTSM2018, EMSM2018

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
        description="Produce shapes for 2018 Standard Model analysis.")

    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--et-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help=
        "Directories arranged as Artus output and containing a friend tree for et."
    )
    parser.add_argument(
        "--mt-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help=
        "Directories arranged as Artus output and containing a friend tree for mt."
    )
    parser.add_argument(
        "--fake-factor-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing friend trees to data files with fake factors."
    )
    parser.add_argument(
        "--tt-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help=
        "Directories arranged as Artus output and containing a friend tree for tt."
    )
    parser.add_argument(
        "--em-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help=
        "Directories arranged as Artus output and containing a friend tree for em."
    )
    parser.add_argument(
        "--QCD-extrap-fit",
        default=False,
        action='store_true',
        help="Create shapes for QCD extrapolation factor determination.")
    parser.add_argument(
        "--datasets", required=True, type=str, help="Kappa datsets database.")
    parser.add_argument(
        "--binning", required=True, type=str, help="Binning configuration.")
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist: [channel for channel in channellist.split(',')],
        help="Channels to be considered, seperated by a comma without space")
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
        "--tag", default="ERA_CHANNEL",
        type=str,
        help="Tag of output files.")
    parser.add_argument(
        "--skip-systematic-variations",
        default=False,
        type=str,
        help="Do not produce the systematic variations.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    logger.info(str(args))
    logger.info("Set up shape variations.")
    systematics = Systematics(
        "output/shapes/{ERA}-{TAG}-{CHANNELS}-shapes.root".format(ERA=args.era, TAG=args.tag, CHANNELS=",".join(args.channels)),
        num_threads=args.num_threads,
        skip_systematic_variations=args.skip_systematic_variations)

    # Era selection
    if "2018" in args.era:
        from shape_producer.estimation_methods_2018 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, qqHEstimation, VHEstimation, WHEstimation, ZHEstimation, ttHEstimation, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, NewFakeEstimationLT, NewFakeEstimationTT

        from shape_producer.era import Run2018
        era = Run2018(args.datasets)

    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # Channels and processes
    # yapf: disable
    directory = args.directory
    et_friend_directory = args.et_friend_directory
    mt_friend_directory = args.mt_friend_directory
    tt_friend_directory = args.tt_friend_directory
    em_friend_directory = args.em_friend_directory
    ff_friend_directory = args.fake_factor_friend_directory

    mt = MTSM2018()
    if args.QCD_extrap_fit:
        mt.cuts.remove("muon_iso")
        mt.cuts.add(Cut("(iso_1<0.5)*(iso_1>=0.15)", "muon_iso_loose"))
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
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, mt, friend_directory=mt_friend_directory)),

        "VH125"    : Process("VH125",    VHEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "WH125"    : Process("WH125",    WHEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZH125"    : Process("ZH125",    ZHEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "ttH125"   : Process("ttH125",   ttHEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),

        # "ggHWW125" : Process("ggHWW125", ggHWWEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        # "qqHWW125" : Process("qqHWW125", qqHWWEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        }

    # Stage 0 and 1.1 signals for ggH & qqH
    for ggH_htxs in ggHEstimation.htxs_dict:
        mt_processes[ggH_htxs] = Process(ggH_htxs, ggHEstimation(ggH_htxs, era, directory, mt, friend_directory=mt_friend_directory))
    for qqH_htxs in qqHEstimation.htxs_dict:
        mt_processes[qqH_htxs] = Process(qqH_htxs, qqHEstimation(qqH_htxs, era, directory, mt, friend_directory=mt_friend_directory))

    mt_processes["FAKES"] = Process("jetFakes", NewFakeEstimationLT(era, directory, mt, [mt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], mt_processes["data"], friend_directory=mt_friend_directory+[ff_friend_directory]))
    mt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            mt_processes["data"], friend_directory=mt_friend_directory, extrapolation_factor=1.00))

    et = ETSM2018()
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
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, et, friend_directory=et_friend_directory)),

        "VH125"    : Process("VH125",    VHEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "WH125"    : Process("WH125",    WHEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "ZH125"    : Process("ZH125",    ZHEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "ttH125"   : Process("ttH125",   ttHEstimation       (era, directory, et, friend_directory=et_friend_directory)),

        # "ggHWW125" : Process("ggHWW125", ggHWWEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        # "qqHWW125" : Process("qqHWW125", qqHWWEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        }

    # Stage 0 and 1.1 signals for ggH & qqH
    for ggH_htxs in ggHEstimation.htxs_dict:
        et_processes[ggH_htxs] = Process(ggH_htxs, ggHEstimation(ggH_htxs, era, directory, et, friend_directory=et_friend_directory))
    for qqH_htxs in qqHEstimation.htxs_dict:
        et_processes[qqH_htxs] = Process(qqH_htxs, qqHEstimation(qqH_htxs, era, directory, et, friend_directory=et_friend_directory))

    et_processes["FAKES"] = Process("jetFakes", NewFakeEstimationLT(era, directory, et, [et_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], et_processes["data"], friend_directory=et_friend_directory+[ff_friend_directory]))
    et_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, et,
            [et_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            et_processes["data"], friend_directory=et_friend_directory, extrapolation_factor=1.00))

    tt = TTSM2018()
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
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, tt, friend_directory=tt_friend_directory)),

        "VH125"    : Process("VH125",    VHEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
        "WH125"    : Process("WH125",    WHEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
        "ZH125"    : Process("ZH125",    ZHEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
        "ttH125"   : Process("ttH125",   ttHEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),

        # "ggHWW125" : Process("ggHWW125", ggHWWEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        # "qqHWW125" : Process("qqHWW125", qqHWWEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        }

    # Stage 0 and 1.1 signals for ggH & qqH
    for ggH_htxs in ggHEstimation.htxs_dict:
        tt_processes[ggH_htxs] = Process(ggH_htxs, ggHEstimation(ggH_htxs, era, directory, tt, friend_directory=tt_friend_directory))
    for qqH_htxs in qqHEstimation.htxs_dict:
        tt_processes[qqH_htxs] = Process(qqH_htxs, qqHEstimation(qqH_htxs, era, directory, tt, friend_directory=tt_friend_directory))

    tt_processes["FAKES"] = Process("jetFakes", NewFakeEstimationTT(era, directory, tt, [tt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], tt_processes["data"], friend_directory=tt_friend_directory+[ff_friend_directory]))
    tt_processes["QCD"] = Process("QCD", QCDEstimation_ABCD_TT_ISO2(era, directory, tt,
            [tt_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            tt_processes["data"], friend_directory=tt_friend_directory))

    em = EMSM2018()
    em_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, em, friend_directory=em_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, em, friend_directory=em_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, em, friend_directory=em_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, em, friend_directory=em_friend_directory)),

        "VH125"    : Process("VH125",    VHEstimation        (era, directory, em, friend_directory=em_friend_directory)),
        "WH125"    : Process("WH125",    WHEstimation        (era, directory, em, friend_directory=em_friend_directory)),
        "ZH125"    : Process("ZH125",    ZHEstimation        (era, directory, em, friend_directory=em_friend_directory)),
        "ttH125"   : Process("ttH125",   ttHEstimation       (era, directory, em, friend_directory=em_friend_directory)),

        # "ggHWW125" : Process("ggHWW125", ggHWWEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        # "qqHWW125" : Process("qqHWW125", qqHWWEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        }

    # Stage 0 and 1.1 signals for ggH & qqH
    for ggH_htxs in ggHEstimation.htxs_dict:
        em_processes[ggH_htxs] = Process(ggH_htxs, ggHEstimation(ggH_htxs, era, directory, em, friend_directory=em_friend_directory))
    for qqH_htxs in qqHEstimation.htxs_dict:
        em_processes[qqH_htxs] = Process(qqH_htxs, qqHEstimation(qqH_htxs, era, directory, em, friend_directory=em_friend_directory))

    em_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, em, [em_processes[process] for process in ["EMB", "ZL", "W", "TTL", "VVL"]], em_processes["data"], extrapolation_factor=1.0, qcd_weight = Weight("em_qcd_extrap_up_Weight","qcd_weight")))

    # Variables and categories
    binning = yaml.load(open(args.binning), Loader=yaml.Loader)

    def readclasses(c):
        if args.tag == "":
            confFileName="output/ml/2018_{}/dataset_config.yaml".format(c,args.tag)
        else:
            confFileName="output/ml/2018_{}_{}/dataset_config.yaml".format(c,args.tag)
        logger.debug("Parse classes from "+confFileName)
        confdict= yaml.load(open(confFileName, "r"))
        logger.debug("Classes for {} loaded: {}".format(c, str(confdict["classes"])))
        return confdict["classes"]

    et_categories = []
    # Analysis shapes
    if "et" in args.channels:
        classes_et = readclasses("et")
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
                stxs = 100 if label == "ggh" else 200
                for i_e, e in enumerate(binning["stxs_stage1p1"][label]):
                    score = Variable(
                        "et_max_score",
                         VariableBinning(binning["analysis"]["et"][label]))
                    et_categories.append(
                        Category(
                            "{}_{}".format(label,str(stxs+i_e)),
                            et,
                            Cuts(Cut("et_max_index=={index}".format(index=i), "exclusive_score"),
                                 Cut(e, "stxs_stage1p1_cut")),
                            variable=score))
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
        classes_mt = readclasses("mt")
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
                stxs = 100 if label == "ggh" else 200
                for i_e, e in enumerate(binning["stxs_stage1p1"][label]):
                    score = Variable(
                        "mt_max_score",
                         VariableBinning(binning["analysis"]["mt"][label]))
                    mt_categories.append(
                        Category(
                            "{}_{}".format(label,str(stxs+i_e)),
                            mt,
                            Cuts(Cut("mt_max_index=={index}".format(index=i), "exclusive_score"),
                                 Cut(e, "stxs_stage1p1_cut")),
                            variable=score))
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
        classes_tt = readclasses("tt")
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
                stxs = 100 if label == "ggh" else 200
                for i_e, e in enumerate(binning["stxs_stage1p1"][label]):
                    score = Variable(
                        "tt_max_score",
                         VariableBinning(binning["analysis"]["tt"][label]))
                    tt_categories.append(
                        Category(
                            "{}_{}".format(label,str(stxs+i_e)),
                            tt,
                            Cuts(Cut("tt_max_index=={index}".format(index=i), "exclusive_score"),
                                 Cut(e, "stxs_stage1p1_cut")),
                            variable=score))
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

    em_categories = []
    # Analysis shapes
    if "em" in args.channels:
        classes_em = readclasses("em")
        for i, label in enumerate(classes_em):
            score = Variable(
                "em_max_score",
                 VariableBinning(binning["analysis"]["em"][label]))
            em_categories.append(
                Category(
                    label,
                    em,
                    Cuts(
                        Cut("em_max_index=={index}".format(index=i), "exclusive_score")),
                    variable=score))
            if label in ["ggh", "qqh"]:
                stxs = 100 if label == "ggh" else 200
                for i_e, e in enumerate(binning["stxs_stage1p1"][label]):
                    score = Variable(
                        "em_max_score",
                         VariableBinning(binning["analysis"]["em"][label]))
                    em_categories.append(
                        Category(
                            "{}_{}".format(label,str(stxs+i_e)),
                            em,
                            Cuts(Cut("em_max_index=={index}".format(index=i), "exclusive_score"),
                                 Cut(e, "stxs_stage1p1_cut")),
                            variable=score))
    # Goodness of fit shapes
    elif args.gof_channel == "em":
        score = Variable(
                args.gof_variable,
                VariableBinning(binning["gof"]["em"][args.gof_variable]["bins"]),
                expression=binning["gof"]["em"][args.gof_variable]["expression"])
        if "cut" in binning["gof"]["em"][args.gof_variable].keys():
            cuts=Cuts(Cut(binning["gof"]["em"][args.gof_variable]["cut"], "binning"))
        else:
            cuts=Cuts()
        em_categories.append(
            Category(
                args.gof_variable,
                em,
                cuts,
                variable=score))
    # Nominal histograms
    signal_nicks = ["WH125", "ZH125", "VH125", "ttH125"]
    ww_nicks = [] #["ggHWW125", "qqHWW125"]
    if args.gof_channel == None:
        signal_nicks += [ggH_htxs for ggH_htxs in ggHEstimation.htxs_dict] + [qqH_htxs for qqH_htxs in qqHEstimation.htxs_dict] + ww_nicks
    else:
        signal_nicks +=  ["ggH125", "qqH125"] + ww_nicks

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
    if "em" in [args.gof_channel] + args.channels:
        for process, category in product(em_processes.values(), em_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))

    # Shapes variations

    # MC tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_mc_t_3prong_Run2018", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_mc_t_1prong_Run2018", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_mc_t_1prong1pizero_Run2018", "tauEsOneProngOnePiZero",
        DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["ZTT", "TTT", "TTL", "VVL", "VVT", "FAKES"
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

    # Tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_t_3prong_Run2018", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_t_1prong_Run2018", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_t_1prong1pizero_Run2018", "tauEsOneProngOnePiZero",
        DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["ZTT", "TTT", "TTL", "VVT", "VVL", "EMB", "FAKES"
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
    
    # Tau ID 
    # in et and mt one nuisance per pT bin
    # [30., 35., 40., 500., 1000. ,$\le$ 1000.]
    for channel in ["et" , "mt"]:
        pt = [30, 35, 40, 500, 1000, "inf"]
        tau_id_variations = []
        for i, ptbin in enumerate(pt[:-1]):
            bindown = ptbin
            binup = pt[i+1]
            if binup == "inf":
                tau_id_variations.append(
                AddWeight("CMS_eff_tauid_{}-{}_{}_Run2018".format(bindown, binup, channel), "tauid_{}-{}_{}_eff_weight".format(bindown, binup, channel),
                        Weight("(((pt_2 >= {bindown})*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2*1.0/tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < {bindown})*1.0))".format(bindown=bindown), "tauid_{}-{}_{}_eff_weight".format(bindown, binup, channel)), "Up"))
                tau_id_variations.append(
                    AddWeight("CMS_eff_tauid_{}-{}_{}_Run2018".format(bindown, binup, channel), "tauid_{}-{}_{}_eff_weight".format(bindown, binup, channel),
                            Weight("(((pt_2 >= {bindown})*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2*1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < {bindown})*1.0))".format(bindown=bindown), "tauid_{}-{}_{}_eff_weight".format(bindown, binup, channel)), "Down"))
            else:
                tau_id_variations.append(
                AddWeight("CMS_eff_tauid_{}-{}_{}_Run2018".format(bindown, binup, channel), "tauid_{}-{}_{}_eff_weight".format(bindown, binup, channel),
                        Weight("(((pt_2 >= {bindown} && pt_2 < {binup})*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2*(1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))+((pt_2 < {bindown} || pt_2 > {binup})*1.0))".format(bindown=bindown, binup=binup), "tauid_{}-{}_{}_eff_weight".format(bindown, binup, channel)), "Up"))
                tau_id_variations.append(
                AddWeight("CMS_eff_tauid_{}-{}_{}_Run2018".format(bindown, binup, channel), "tauid_{}-{}_{}_eff_weight".format(bindown, binup, channel),
                        Weight("(((pt_2 >= {bindown} && pt_2 < {binup})*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2*(1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))+((pt_2 < {bindown} || pt_2 > {binup})*1.0))".format(bindown=bindown, binup=binup), "tauid_{}-{}_{}_eff_weight".format(bindown, binup, channel)), "Down"))
            
        for variation in tau_id_variations:
            for process_nick in ["ZTT", "TTT", "TTL", "VVT", "VVL", "EMB", "FAKES"
                            ] + signal_nicks:
                if "et" in [args.gof_channel] + args.channels and "et" in channel:
                    systematics.add_systematic_variation(
                        variation=variation,
                        process=et_processes[process_nick],
                        channel=et,
                        era=era)
                if "mt" in [args.gof_channel] + args.channels and "mt" in channel:
                    systematics.add_systematic_variation(
                        variation=variation,
                        process=mt_processes[process_nick],
                        channel=mt,
                        era=era)
    # for tautau, the id is split by decay mode, and each decay mode is assosicated one nuicance
    tau_id_variations = []
    for decaymode in [0,1,10,11]:
        tau_id_variations.append(
            AddWeight("CMS_eff_tauid_dm{dm}-tt_Run2018".format(dm=decaymode), "tauid_dm{dm}-tt_eff_weight".format(dm=decaymode),
                    Weight("(((decayMode_1=={dm} && decayMode_2=={dm})*(1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1)*(1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_1!={dm} && decayMode_2=={dm})*(1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_1=={dm} && decayMode_2!={dm})*(1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!={dm} && decayMode_2!={dm})*1.0))".format(dm=decaymode), "tauid_dm{dm}-tt_eff_weight".format(dm=decaymode)), "Up"))
        tau_id_variations.append(
                AddWeight("CMS_eff_tauid_dm{dm}-tt_Run2018".format(dm=decaymode), "tauid_dm{dm}-tt_eff_weight".format(dm=decaymode),
                    Weight("(((decayMode_1=={dm} && decayMode_2=={dm})*(1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1)*(1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_1!={dm} && decayMode_2=={dm})*(1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_1=={dm} && decayMode_2!={dm})*(1.0/tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!={dm} && decayMode_2!={dm})*1.0))".format(dm=decaymode), "tauid_dm{dm}-tt_eff_weight".format(dm=decaymode)), "Down"))
    for variation in tau_id_variations:
        for process_nick in ["ZTT", "TTT", "TTL", "VVT", "VVL", "EMB", "FAKES"
                        ] + signal_nicks:
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # MC ele energy scale & smear uncertainties
    ele_es_variations = create_systematic_variations(
        "CMS_scale_mc_e", "eleScale", DifferentPipeline)
    ele_es_variations += create_systematic_variations(
        "CMS_reso_mc_e", "eleSmear", DifferentPipeline)
    for variation in ele_es_variations:
        for process_nick in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVL", "VVT", "VVJ"
                            ] + signal_nicks:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
        for process_nick in ["ZTT", "ZL", "W", "TTT", "TTL",  "VVL", "VVT"
                            ] + signal_nicks:
            if "em" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # Jet energy scale

    # Inclusive JES shapes
    jet_es_variations = []
    '''jet_es_variations += create_systematic_variations(
        "CMS_scale_j_Run2018", "jecUnc", DifferentPipeline)'''

    # Splitted JES shapes
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta0to3_Run2018", "jecUncEta0to3", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta0to5_Run2018", "jecUncEta0to5", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta3to5_Run2018", "jecUncEta3to5", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeBal_Run2018", "jecUncRelativeBal",
        DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeSample_Run2018", "jecUncRelativeSample",
        DifferentPipeline)

    for variation in jet_es_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVJ", "VVL",
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
        for process_nick in ["ZTT", "ZL", "W", "TTT", "TTL", "VVL", "VVT"
                ] + signal_nicks:
            if "em" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # MET energy scale. Note: only those variations for non-resonant processes are used in the stat. inference
    met_unclustered_variations = create_systematic_variations(
        "CMS_scale_met_unclustered", "metUnclusteredEn",
        DifferentPipeline)
    for variation in met_unclustered_variations:  # + met_clustered_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVJ", "VVL"
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
        for process_nick in [
                "ZTT", "ZL", "W", "TTT", "TTL", "VVL", "VVT"
        ] + signal_nicks:
            if "em" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # Recoil correction unc
    recoil_resolution_variations = create_systematic_variations(
        "CMS_htt_boson_reso_met_Run2018", "metRecoilResolution",
        DifferentPipeline)
    recoil_response_variations = create_systematic_variations(
        "CMS_htt_boson_scale_met_Run2018", "metRecoilResponse",
        DifferentPipeline)
    for variation in recoil_resolution_variations + recoil_response_variations:
        for process_nick in ["ZTT", "ZL", "ZJ", "W"] + signal_nicks:
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
        for process_nick in ["ZTT", "ZL", "W"] + signal_nicks:
            if "em" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # Z pt reweighting
    zpt_variations = create_systematic_variations(
        "CMS_htt_dyShape_Run2018", "zPtReweightWeight", SquareAndRemoveWeight)
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
        for process_nick in ["ZTT", "ZL"]:
            if "em" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # top pt reweighting
    top_pt_variations = create_systematic_variations(
        "CMS_htt_ttbarShape", "topPtReweightWeight",
        SquareAndRemoveWeight)
    for variation in top_pt_variations:
        for process_nick in ["TTT", "TTL", "TTJ"]:
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
        for process_nick in ["TTT", "TTL"]:
            if "em" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # jet to tau fake efficiency
    jet_to_tau_fake_variations = []
    jet_to_tau_fake_variations.append(
        AddWeight("CMS_htt_jetToTauFake_Run2018", "jetToTauFake_weight",
                  Weight("max(1.0-pt_2*0.002, 0.6)", "jetToTauFake_weight"), "Up"))
    jet_to_tau_fake_variations.append(
        AddWeight("CMS_htt_jetToTauFake_Run2018", "jetToTauFake_weight",
                  Weight("min(1.0+pt_2*0.002, 1.4)", "jetToTauFake_weight"), "Down"))
    for variation in jet_to_tau_fake_variations:
        for process_nick in ["ZJ", "TTJ", "W", "VVJ"]:
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

    # ZL fakes energy scale
    ele_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_et_1prong_Run2018", "tauEleFakeEsOneProng",
        DifferentPipeline)
    ele_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_et_1prong1pizero_Run2018", "tauEleFakeEsOneProngPiZeros",
        DifferentPipeline)

    if "et" in [args.gof_channel] + args.channels:
        for process_nick in ["ZL"]:
            for variation in ele_fake_es_1prong_variations + ele_fake_es_1prong1pizero_variations:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)

    mu_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong_Run2018", "tauMuFakeEsOneProng",
        DifferentPipeline)
    mu_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong1pizero_Run2018", "tauMuFakeEsOneProngPiZeros",
        DifferentPipeline)

    if "mt" in [args.gof_channel] + args.channels:
        for process_nick in ["ZL"]:
            for variation in mu_fake_es_1prong_variations + mu_fake_es_1prong1pizero_variations:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # lepton trigger efficiency
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_mt_Run2018", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+1.02*(pt_1>25))", "trg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_mt_Run2018", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+0.98*(pt_1>25))", "trg_mt_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_mt_Run2018", "xtrg_mt_eff_weight",
                  Weight("(1.054*(pt_1<=25)+1.0*(pt_1>25))", "xtrg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_mt_Run2018", "xtrg_mt_eff_weight",
                  Weight("(0.946*(pt_1<=25)+1.0*(pt_1>25))", "xtrg_mt_eff_weight"), "Down"))
    for variation in lep_trigger_eff_variations:
        for process_nick in [
            "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVL", "VVT", "VVJ",
        ] + signal_nicks:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_emb_mt_Run2018", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+1.02*(pt_1>25))", "trg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_emb_mt_Run2018", "trg_mt_eff_weight",
                  Weight("(1.0*(pt_1<=25)+0.98*(pt_1>25))", "trg_mt_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_emb_mt_Run2018", "xtrg_mt_eff_weight",
                  Weight("(1.054*(pt_1<=25)+1.0*(pt_1>25))", "xtrg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_emb_mt_Run2018", "xtrg_mt_eff_weight",
                  Weight("(0.946*(pt_1<=25)+1.0*(pt_1>25))", "xtrg_mt_eff_weight"), "Down"))
    for variation in lep_trigger_eff_variations:
        for process_nick in ["EMB"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_et_Run2018", "trg_et_eff_weight",
                  Weight("(1.0*(pt_1<=28)+1.02*(pt_1>28))", "trg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_et_Run2018", "trg_et_eff_weight",
                  Weight("(1.0*(pt_1<=28)+0.98*(pt_1>28))", "trg_et_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_et_Run2018", "xtrg_et_eff_weight",
                  Weight("(1.054*(pt_1<=28)+1.0*(pt_1>28))", "xtrg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_et_Run2018", "xtrg_et_eff_weight",
                  Weight("(0.946*(pt_1<=28)+1.0*(pt_1>28))", "xtrg_et_eff_weight"), "Down"))
    for variation in lep_trigger_eff_variations:
        for process_nick in [
            "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVL", "VVT", "VVJ",
        ] + signal_nicks:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_emb_et_Run2018", "trg_et_eff_weight",
                  Weight("(1.0*(pt_1<=28)+1.02*(pt_1>28))", "trg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_trigger_emb_et_Run2018", "trg_et_eff_weight",
                  Weight("(1.0*(pt_1<=28)+0.98*(pt_1>28))", "trg_et_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_emb_et_Run2018", "xtrg_et_eff_weight",
                  Weight("(1.054*(pt_1<=28)+1.0*(pt_1>28))", "xtrg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight("CMS_eff_xtrigger_emb_et_Run2018", "xtrg_et_eff_weight",
                  Weight("(0.946*(pt_1<=28)+1.0*(pt_1>28))", "xtrg_et_eff_weight"), "Down"))
    for variation in lep_trigger_eff_variations:
        for process_nick in ["EMB"]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)

    # Zll reweighting !!! replaced by log normal uncertainties: CMS_eFakeTau_Run2018 16%; CMS_mFakeTau_Run2018 26%
    '''zll_et_weight_variations = []
    zll_et_weight_variations.append(
        AddWeight(
            "CMS_eFakeTau_Run2018", "eFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 1.46)*2.0/1.8) + ((abs(eta_1) >= 1.46 && abs(eta_1) < 1.558)*2.06) + ((abs(eta_1) >= 1.558)*2.13/1.53))",
                "eFakeTau_reweight"), "Up"))
    zll_et_weight_variations.append(
        AddWeight(
            "CMS_eFakeTau_Run2018", "eFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 1.46)*1.6/1.8) + ((abs(eta_1) >= 1.46 && abs(eta_1) < 1.558)*1.27) + ((abs(eta_1) >= 1.558)*0.93/1.53))",
                "eFakeTau_reweight"), "Down"))
    for variation in zll_et_weight_variations:
        for process_nick in ["ZL"]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
    zll_mt_weight_variations = []
    zll_mt_weight_variations.append(
        AddWeight(
            "CMS_mFakeTau_Run2018", "mFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 0.4)*1.29/1.17) + ((abs(eta_1) >= 0.4 && abs(eta_1) < 0.8)*1.59/1.29) + ((abs(eta_1) >= 0.8 && abs(eta_1) < 1.2)*1.19/1.14) + ((abs(eta_1) >= 1.2 && abs(eta_1) < 1.7)*1.53/0.93) + ((abs(eta_1) >= 1.7 && abs(eta_1) < 2.3)*2.21/1.61) + (abs(eta_1) >= 2.3))",
                "mFakeTau_reweight"), "Up"))
    zll_mt_weight_variations.append(
        AddWeight(
            "CMS_mFakeTau_Run2018", "mFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 0.4)*1.05/1.17) + ((abs(eta_1) >= 0.4 && abs(eta_1) < 0.8)*0.99/1.29) + ((abs(eta_1) >= 0.8 && abs(eta_1) < 1.2)*1.09/1.14) + ((abs(eta_1) >= 1.2 && abs(eta_1) < 1.7)*0.33/0.93) + ((abs(eta_1) >= 1.7 && abs(eta_1) < 2.3)*1.01/1.61) + (abs(eta_1) >= 2.3))",
                "mFakeTau_reweight"), "Down"))
    for variation in zll_mt_weight_variations:
        for process_nick in ["ZL"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)'''

    # b tagging
    btag_eff_variations = create_systematic_variations(
        "CMS_htt_eff_b_Run2018", "btagEff", DifferentPipeline)
    mistag_eff_variations = create_systematic_variations(
        "CMS_htt_mistag_b_Run2018", "btagMistag", DifferentPipeline)
    for variation in btag_eff_variations + mistag_eff_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVL", "VVJ"
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
        for process_nick in ["ZTT", "ZL", "W", "TTT", "TTL", "VVL", "VVT"
                ] + signal_nicks:
            if "em" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # Embedded event specifics
    # Tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_emb_t_3prong_Run2018", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_emb_t_1prong_Run2018", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_emb_t_1prong1pizero_Run2018", "tauEsOneProngOnePiZero",
        DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["EMB", "FAKES"]:
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

    # Ele energy scale
    ele_es_variations = create_systematic_variations(
        "CMS_scale_emb_e", "eleEs", DifferentPipeline)
    for variation in ele_es_variations:
        for process_nick in ["EMB"]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "em" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    mt_decayMode_variations = []
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2018", "decayMode_SF",
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
            "CMS_3ProngEff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2018", "decayMode_SF",
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
            "CMS_3ProngEff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2018", "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run2018", "decayMode_SF",
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
    tttautau_process_em = Process(
        "TTT",
        TTTEstimation(
            era, directory, em, friend_directory=em_friend_directory))
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
                    variation=Relabel("CMS_htt_emb_ttbar_Run2018", "Down"),
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
                    variation=Relabel("CMS_htt_emb_ttbar_Run2018", "Up"),
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
                    variation=Relabel("CMS_htt_emb_ttbar_Run2018", "Down"),
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
                    variation=Relabel("CMS_htt_emb_ttbar_Run2018", "Up"),
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
                    variation=Relabel("CMS_htt_emb_ttbar_Run2018", "Down"),
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
                    variation=Relabel("CMS_htt_emb_ttbar_Run2018", "Up"),
                    mass="125"))
    if 'em' in [args.gof_channel] + args.channels:
        for category in em_categories:
            em_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, em,
                    [em_processes["EMB"], tttautau_process_em], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=em_processes['ZTTpTTTauTauDown'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar_Run2018", "Down"),
                    mass="125"))

            em_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, em,
                    [em_processes["EMB"], tttautau_process_em], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=em_processes['ZTTpTTTauTauUp'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel("CMS_htt_emb_ttbar_Run2018", "Up"),
                    mass="125"))
    # jetfakes
    fake_factor_variations_et = []
    fake_factor_variations_mt = []
    for systematic_shift in [
            "ff_qcd{ch}_syst_Run2018{shift}",
            "ff_qcd_dm0_njet0{ch}_stat_Run2018{shift}",
            "ff_qcd_dm0_njet1{ch}_stat_Run2018{shift}",
            #"ff_qcd_dm1_njet0{ch}_stat_Run2018{shift}",
            #"ff_qcd_dm1_njet1{ch}_stat_Run2018{shift}",
            "ff_w_syst_Run2018{shift}",
            "ff_w_dm0_njet0{ch}_stat_Run2018{shift}",
            "ff_w_dm0_njet1{ch}_stat_Run2018{shift}",
            #"ff_w_dm1_njet0{ch}_stat_Run2018{shift}",
            #"ff_w_dm1_njet1{ch}_stat_Run2018{shift}",
            "ff_tt_syst_Run2018{shift}",
            "ff_tt_dm0_njet0_stat_Run2018{shift}",
            "ff_tt_dm0_njet1_stat_Run2018{shift}",
            #"ff_tt_dm1_njet0_stat_Run2018{shift}",
            #"ff_tt_dm1_njet1_stat_Run2018{shift}"
    ]:
        for shift_direction in ["Up", "Down"]:
            fake_factor_variations_et.append(
                ReplaceWeight(
                    "CMS_%s" % (systematic_shift.format(ch='_et', shift="").replace("_dm0", "")),
                    "fake_factor",
                    Weight(
                        "ff2_{syst}".format(
                            syst=systematic_shift.format(
                                ch="", shift="_%s" % shift_direction.lower())
                            .replace("_Run2018", "")),
                        "fake_factor"), shift_direction))
            fake_factor_variations_mt.append(
                ReplaceWeight(
                    "CMS_%s" % (systematic_shift.format(ch='_mt', shift="").replace("_dm0", "")),
                    "fake_factor",
                    Weight(
                        "ff2_{syst}".format(
                            syst=systematic_shift.format(
                                ch="", shift="_%s" % shift_direction.lower())
                            .replace("_Run2018", "")),
                        "fake_factor"), shift_direction))
    if "et" in [args.gof_channel] + args.channels:
        for variation in fake_factor_variations_et:
            systematics.add_systematic_variation(
                variation=variation,
                process=et_processes["FAKES"],
                channel=et,
                era=era)
    if "mt" in [args.gof_channel] + args.channels:
        for variation in fake_factor_variations_mt:
            systematics.add_systematic_variation(
                variation=variation,
                process=mt_processes["FAKES"],
                channel=mt,
                era=era)
    fake_factor_variations_tt = []
    for systematic_shift in [
            "ff_qcd{ch}_syst_Run2018{shift}",
            "ff_qcd_dm0_njet0{ch}_stat_Run2018{shift}",
            "ff_qcd_dm0_njet1{ch}_stat_Run2018{shift}",
            #"ff_qcd_dm1_njet0{ch}_stat_Run2018{shift}",
            #"ff_qcd_dm1_njet1{ch}_stat_Run2018{shift}",
            "ff_w{ch}_syst_Run2018{shift}", "ff_tt{ch}_syst_Run2018{shift}",
            "ff_w_frac{ch}_syst_Run2018{shift}",
            "ff_tt_frac{ch}_syst_Run2018{shift}"
    ]:
        for shift_direction in ["Up", "Down"]:
            fake_factor_variations_tt.append(
                ReplaceWeight(
                    "CMS_%s" % (systematic_shift.format(ch='_tt', shift="").replace("_dm0", "")),
                    "fake_factor",
                    Weight(
                        "(0.5*ff1_{syst}*(byTightDeepTau2017v2p1VSjet_1<0.5)+0.5*ff2_{syst}*(byTightDeepTau2017v2p1VSjet_2<0.5))".
                        format(
                            syst=systematic_shift.format(
                                ch="", shift="_%s" % shift_direction.lower())
                            .replace("_Run2018", "")),
                        "fake_factor"), shift_direction))
    if "tt" in [args.gof_channel] + args.channels:
        for variation in fake_factor_variations_tt:
            systematics.add_systematic_variation(
                variation=variation,
                process=tt_processes["FAKES"],
                channel=tt,
                era=era)

    # QCD for em
    qcd_variations = []
    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_0jet_rate_Run2018", "qcd_weight",
        Weight("em_qcd_osss_0jet_rateup_Weight*em_qcd_extrap_uncert_Weight", "qcd_weight"),
        "Up"))
    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_0jet_rate_Run2018", "qcd_weight",
        Weight("em_qcd_osss_0jet_ratedown_Weight*em_qcd_extrap_uncert_Weight", "qcd_weight"),
        "Down"))

    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_0jet_shape_Run2018", "qcd_weight",
        Weight("em_qcd_osss_0jet_shapeup_Weight*em_qcd_extrap_uncert_Weight", "qcd_weight"),
        "Up"))
    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_0jet_shape_Run2018", "qcd_weight",
        Weight("em_qcd_osss_0jet_shapedown_Weight*em_qcd_extrap_uncert_Weight", "qcd_weight"),
        "Down"))

    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_1jet_rate_Run2018", "qcd_weight",
        Weight("em_qcd_osss_1jet_rateup_Weight*em_qcd_extrap_uncert_Weight", "qcd_weight"),
        "Up"))
    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_1jet_rate_Run2018", "qcd_weight",
        Weight("em_qcd_osss_1jet_ratedown_Weight*em_qcd_extrap_uncert_Weight", "qcd_weight"),
        "Down"))


    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_1jet_shape_Run2018", "qcd_weight",
        Weight("em_qcd_osss_1jet_shapeup_Weight*em_qcd_extrap_uncert_Weight", "qcd_weight"),
        "Up"))
    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_1jet_shape_Run2018", "qcd_weight",
        Weight("em_qcd_osss_1jet_shapedown_Weight*em_qcd_extrap_uncert_Weight", "qcd_weight"),
        "Down"))

    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_iso_Run2018", "qcd_weight",
        Weight("em_qcd_extrap_up_Weight*em_qcd_extrap_uncert_Weight", "qcd_weight"),
        "Up"))
    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_iso_Run2018", "qcd_weight",
        Weight("em_qcd_osss_binned_Weight", "qcd_weight"),
        "Down"))
    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_iso", "qcd_weight",
        Weight("em_qcd_extrap_up_Weight*em_qcd_extrap_uncert_Weight", "qcd_weight"),
        "Up"))
    qcd_variations.append(ReplaceWeight(
        "CMS_htt_qcd_iso", "qcd_weight",
        Weight("em_qcd_osss_binned_Weight", "qcd_weight"),
        "Down"))


    for variation in qcd_variations:
        for process_nick in ["QCD"]:
            if "em" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # Gluon-fusion WG1 uncertainty scheme
    ggh_variations = []
    for unc in [
            "THU_ggH_Mig01", "THU_ggH_Mig12", "THU_ggH_Mu", "THU_ggH_PT120",
            "THU_ggH_PT60", "THU_ggH_Res", "THU_ggH_VBF2j", "THU_ggH_VBF3j",
            "THU_ggH_qmtop"
    ]:
        ggh_variations.append(
            AddWeight(unc, "{}_weight".format(unc),
                      Weight("({})".format(unc), "{}_weight".format(unc)),
                      "Up"))
        ggh_variations.append(
            AddWeight(unc, "{}_weight".format(unc),
                      Weight("(1.0/{})".format(unc), "{}_weight".format(unc)),
                      "Down"))
    for variation in ggh_variations:
        for process_nick in [nick for nick in signal_nicks if "ggH" in nick and "HWW" not in nick]:
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
            if "em" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("output/log/{}_{}_{}_shapes.log".format(args.era, args.tag, ",".join(args.channels)), logging.INFO)
    main(args)
