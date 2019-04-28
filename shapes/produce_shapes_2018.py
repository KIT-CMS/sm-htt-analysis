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
        description="Produce shapes for 2017 Standard Model analysis.")

    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--em-directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--et-friend-directory",
        default="",
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for et."
    )
    parser.add_argument(
        "--em-friend-directory",
        default="",
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for em."
    )
    parser.add_argument(
        "--mt-friend-directory",
        default="",
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for mt."
    )
    parser.add_argument(
        "--tt-friend-directory",
        default="",
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
    if "2018" in args.era:
        from shape_producer.estimation_methods_2018 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, ggHEstimation_0J, ggHEstimation_1J_PTH_0_60, ggHEstimation_1J_PTH_60_120, ggHEstimation_1J_PTH_120_200, ggHEstimation_1J_PTH_GT200, ggHEstimation_GE2J_PTH_0_60, ggHEstimation_GE2J_PTH_60_120, ggHEstimation_GE2J_PTH_120_200, ggHEstimation_GE2J_PTH_GT200, ggHEstimation_VBFTOPO_JET3, ggHEstimation_VBFTOPO_JET3VETO, qqHEstimation, qqHEstimation_VBFTOPO_JET3VETO, qqHEstimation_VBFTOPO_JET3, qqHEstimation_REST, qqHEstimation_VH2JET, qqHEstimation_PTJET1_GT200, VHEstimation, WHEstimation, ZHEstimation, ttHEstimation, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, FakeEstimationLT, NewFakeEstimationLT, FakeEstimationTT, NewFakeEstimationTT

        from shape_producer.era import Run2018
        era = Run2018(args.datasets)

    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # Channels and processes
    # yapf: disable
    directory = args.directory
    et_friend_directory = []#args.et_friend_directory
    em_friend_directory = []#args.em_friend_directory
    mt_friend_directory = []#args.mt_friend_directory
    tt_friend_directory = []#args.tt_friend_directory
    ff_friend_directory = []#args.fake_factor_friend_directory
    mt = MTSM2018()
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
        "ggH"   : Process("ggH125",   ggHEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_0J"               : Process("ggH_0J125",               ggHEstimation_0J              (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_1J_PTH_0_60"      : Process("ggH_1J_PTH_0_60125",      ggHEstimation_1J_PTH_0_60     (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_1J_PTH_60_120"    : Process("ggH_1J_PTH_60_120125",    ggHEstimation_1J_PTH_60_120   (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_1J_PTH_120_200"   : Process("ggH_1J_PTH_120_200125",   ggHEstimation_1J_PTH_120_200  (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_1J_PTH_GT200"     : Process("ggH_1J_PTH_GT200125",     ggHEstimation_1J_PTH_GT200    (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_GE2J_PTH_0_60"    : Process("ggH_GE2J_PTH_0_60125",    ggHEstimation_GE2J_PTH_0_60   (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_GE2J_PTH_60_120"  : Process("ggH_GE2J_PTH_60_120125",  ggHEstimation_GE2J_PTH_60_120 (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_GE2J_PTH_120_200" : Process("ggH_GE2J_PTH_120_200125", ggHEstimation_GE2J_PTH_120_200(era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_GE2J_PTH_GT200"   : Process("ggH_GE2J_PTH_GT200125",   ggHEstimation_GE2J_PTH_GT200  (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_VBFTOPO_JET3VETO" : Process("ggH_VBFTOPO_JET3VETO125", ggHEstimation_VBFTOPO_JET3VETO(era, directory, mt, friend_directory=mt_friend_directory)),
        # "ggH_VBFTOPO_JET3"     : Process("ggH_VBFTOPO_JET3125",     ggHEstimation_VBFTOPO_JET3    (era, directory, mt, friend_directory=mt_friend_directory)),
        # "qqH_VBFTOPO_JET3VETO" : Process("qqH_VBFTOPO_JET3VETO125", qqHEstimation_VBFTOPO_JET3VETO(era, directory, mt, friend_directory=mt_friend_directory)),
        # "qqH_VBFTOPO_JET3"     : Process("qqH_VBFTOPO_JET3125",     qqHEstimation_VBFTOPO_JET3    (era, directory, mt, friend_directory=mt_friend_directory)),
        # "qqH_REST"             : Process("qqH_REST125",             qqHEstimation_REST            (era, directory, mt, friend_directory=mt_friend_directory)),
        # "qqH_VH2JET"           : Process("qqH_VH2JET125",           qqHEstimation_VH2JET          (era, directory, mt, friend_directory=mt_friend_directory)),
        # "qqH_PTJET1_GT200"     : Process("qqH_PTJET1_GT200125",     qqHEstimation_PTJET1_GT200    (era, directory, mt, friend_directory=mt_friend_directory)),
        # "VH"                   : Process("VH125",                   VHEstimation                  (era, directory, mt, friend_directory=mt_friend_directory)),
        # "WH"                   : Process("WH125",                   WHEstimation                  (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ZH"                   : Process("ZH125",                   ZHEstimation                  (era, directory, mt, friend_directory=mt_friend_directory)),
        # "ttH"                  : Process("ttH125",                  ttHEstimation                 (era, directory, mt, friend_directory=mt_friend_directory)),
        }
    # mt_processes["FAKES"] = Process("jetFakes", NewFakeEstimationLT(era, directory, mt, [mt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], mt_processes["data"], friend_directory=[mt_friend_directory, ff_friend_directory]))
    #mt_fakes_for_uncs=Process("jetFakes", FakeEstimationLT(era, directory, mt, friend_directory=[mt_friend_directory, ff_friend_directory]))
    
    mt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["ZTT", "ZL", "ZJ", "TTL","TTT","TTJ", "VVT", "VVJ", "VVL","W"]],
            mt_processes["data"], friend_directory=mt_friend_directory, extrapolation_factor=1.1))
    mt_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["EMB", "ZL", "ZJ", "TTL", "TTJ", "VVJ", "VVL","W"]],
            mt_processes["data"], friend_directory=mt_friend_directory, extrapolation_factor=1.1))
    


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
        "ggH"   : Process("ggH125",   ggHEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_0J"               : Process("ggH_0J125",               ggHEstimation_0J              (era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_1J_PTH_0_60"      : Process("ggH_1J_PTH_0_60125",      ggHEstimation_1J_PTH_0_60     (era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_1J_PTH_60_120"    : Process("ggH_1J_PTH_60_120125",    ggHEstimation_1J_PTH_60_120   (era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_1J_PTH_120_200"   : Process("ggH_1J_PTH_120_200125",   ggHEstimation_1J_PTH_120_200  (era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_1J_PTH_GT200"     : Process("ggH_1J_PTH_GT200125",     ggHEstimation_1J_PTH_GT200    (era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_GE2J_PTH_0_60"    : Process("ggH_GE2J_PTH_0_60125",    ggHEstimation_GE2J_PTH_0_60   (era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_GE2J_PTH_60_120"  : Process("ggH_GE2J_PTH_60_120125",  ggHEstimation_GE2J_PTH_60_120 (era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_GE2J_PTH_120_200" : Process("ggH_GE2J_PTH_120_200125", ggHEstimation_GE2J_PTH_120_200(era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_GE2J_PTH_GT200"   : Process("ggH_GE2J_PTH_GT200125",   ggHEstimation_GE2J_PTH_GT200  (era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_VBFTOPO_JET3VETO" : Process("ggH_VBFTOPO_JET3VETO125", ggHEstimation_VBFTOPO_JET3VETO(era, directory, et, friend_directory=et_friend_directory)),
        # "ggH_VBFTOPO_JET3"     : Process("ggH_VBFTOPO_JET3125",     ggHEstimation_VBFTOPO_JET3    (era, directory, et, friend_directory=et_friend_directory)),
        # "qqH_VBFTOPO_JET3VETO" : Process("qqH_VBFTOPO_JET3VETO125", qqHEstimation_VBFTOPO_JET3VETO(era, directory, et, friend_directory=et_friend_directory)),
        # "qqH_VBFTOPO_JET3"     : Process("qqH_VBFTOPO_JET3125",     qqHEstimation_VBFTOPO_JET3    (era, directory, et, friend_directory=et_friend_directory)),
        # "qqH_REST"             : Process("qqH_REST125",             qqHEstimation_REST            (era, directory, et, friend_directory=et_friend_directory)),
        # "qqH_VH2JET"           : Process("qqH_VH2JET125",           qqHEstimation_VH2JET          (era, directory, et, friend_directory=et_friend_directory)),
        # "qqH_PTJET1_GT200"     : Process("qqH_PTJET1_GT200125",     qqHEstimation_PTJET1_GT200    (era, directory, et, friend_directory=et_friend_directory)),
        # "VH"                   : Process("VH125",                   VHEstimation                  (era, directory, et, friend_directory=et_friend_directory)),
        # "WH"                   : Process("WH125",                   WHEstimation                  (era, directory, et, friend_directory=et_friend_directory)),
        # "ZH"                   : Process("ZH125",                   ZHEstimation                  (era, directory, et, friend_directory=et_friend_directory)),
        # "ttH"                  : Process("ttH125",                  ttHEstimation                 (era, directory, et, friend_directory=et_friend_directory)),
        }
    # et_processes["FAKES"] = Process("jetFakes", NewFakeEstimationLT(era, directory, et, [et_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], et_processes["data"], friend_directory=[et_friend_directory, ff_friend_directory]))
    
    et_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, et,
            [et_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            et_processes["data"], friend_directory=et_friend_directory, extrapolation_factor=1.1))
    et_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, et,
            [et_processes[process] for process in ["EMB", "ZL", "ZJ", "W", "TTJ", "TTL", "VVJ", "VVL"]],
            et_processes["data"], friend_directory=et_friend_directory, extrapolation_factor=1.1))
    

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
        "ggH"   : Process("ggH125",   ggHEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_0J"               : Process("ggH_0J125",               ggHEstimation_0J              (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_1J_PTH_0_60"      : Process("ggH_1J_PTH_0_60125",      ggHEstimation_1J_PTH_0_60     (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_1J_PTH_60_120"    : Process("ggH_1J_PTH_60_120125",    ggHEstimation_1J_PTH_60_120   (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_1J_PTH_120_200"   : Process("ggH_1J_PTH_120_200125",   ggHEstimation_1J_PTH_120_200  (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_1J_PTH_GT200"     : Process("ggH_1J_PTH_GT200125",     ggHEstimation_1J_PTH_GT200    (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_GE2J_PTH_0_60"    : Process("ggH_GE2J_PTH_0_60125",    ggHEstimation_GE2J_PTH_0_60   (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_GE2J_PTH_60_120"  : Process("ggH_GE2J_PTH_60_120125",  ggHEstimation_GE2J_PTH_60_120 (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_GE2J_PTH_120_200" : Process("ggH_GE2J_PTH_120_200125", ggHEstimation_GE2J_PTH_120_200(era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_GE2J_PTH_GT200"   : Process("ggH_GE2J_PTH_GT200125",   ggHEstimation_GE2J_PTH_GT200  (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_VBFTOPO_JET3VETO" : Process("ggH_VBFTOPO_JET3VETO125", ggHEstimation_VBFTOPO_JET3VETO(era, directory, tt, friend_directory=tt_friend_directory)),
        # "ggH_VBFTOPO_JET3"     : Process("ggH_VBFTOPO_JET3125",     ggHEstimation_VBFTOPO_JET3    (era, directory, tt, friend_directory=tt_friend_directory)),
        # "qqH_VBFTOPO_JET3VETO" : Process("qqH_VBFTOPO_JET3VETO125", qqHEstimation_VBFTOPO_JET3VETO(era, directory, tt, friend_directory=tt_friend_directory)),
        # "qqH_VBFTOPO_JET3"     : Process("qqH_VBFTOPO_JET3125",     qqHEstimation_VBFTOPO_JET3    (era, directory, tt, friend_directory=tt_friend_directory)),
        # "qqH_REST"             : Process("qqH_REST125",             qqHEstimation_REST            (era, directory, tt, friend_directory=tt_friend_directory)),
        # "qqH_VH2JET"           : Process("qqH_VH2JET125",           qqHEstimation_VH2JET          (era, directory, tt, friend_directory=tt_friend_directory)),
        # "qqH_PTJET1_GT200"     : Process("qqH_PTJET1_GT200125",     qqHEstimation_PTJET1_GT200    (era, directory, tt, friend_directory=tt_friend_directory)),
        # "VH"                   : Process("VH125",                   VHEstimation                  (era, directory, tt, friend_directory=tt_friend_directory)),
        # "WH"                   : Process("WH125",                   WHEstimation                  (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ZH"                   : Process("ZH125",                   ZHEstimation                  (era, directory, tt, friend_directory=tt_friend_directory)),
        # "ttH"                  : Process("ttH125",                  ttHEstimation                 (era, directory, tt, friend_directory=tt_friend_directory)),
        }
    # tt_processes["FAKES"] = Process("jetFakes", NewFakeEstimationTT(era, directory, tt, [tt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], tt_processes["data"], friend_directory=[tt_friend_directory, ff_friend_directory]))
    
    tt_processes["QCD"] = Process("QCD", QCDEstimation_ABCD_TT_ISO2(era, directory, tt,
            [tt_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            tt_processes["data"], friend_directory=tt_friend_directory))
    tt_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_ABCD_TT_ISO2(era, directory, tt,
            [tt_processes[process] for process in ["EMB", "ZL", "ZJ", "W", "TTJ", "TTL", "VVJ", "VVL"]],
            tt_processes["data"], friend_directory=tt_friend_directory))

    em = EMSM2018()
    em_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, em, friend_directory=em_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, em, friend_directory=em_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimation        (era, directory, em, friend_directory=em_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, em, friend_directory=em_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "VVJ"   : Process("VVJ",      VVJEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, em, friend_directory=em_friend_directory)),
        "ggH"   : Process("ggH125",   ggHEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       (era, directory, em, friend_directory=em_friend_directory))
        }
    
    em_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, em,
            [em_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            em_processes["data"], friend_directory=em_friend_directory, extrapolation_factor=1.0, qcd_weight = Weight("em_qcd_extrap_up_Weight","qcd_weight")))
    em_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, em,
            [em_processes[process] for process in ["EMB", "ZL", "ZJ", "W", "TTJ", "TTL", "VVJ", "VVL"]],
            em_processes["data"], friend_directory=em_friend_directory, extrapolation_factor=1.0, qcd_weight = Weight("em_qcd_extrap_up_Weight","qcd_weight")))
    


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
                for i_e, e in enumerate(binning["stxs_stage1"]["lt"][label]):
                    offset = (binning["analysis"]["et"][label][-1]-binning["analysis"]["et"][label][0])*i_e
                    expression += "{STXSBIN}*(et_max_score+{OFFSET})".format(STXSBIN=e, OFFSET=offset)
                    if not e is binning["stxs_stage1"]["lt"][label][-1]:
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
                for i_e, e in enumerate(binning["stxs_stage1"]["lt"][label]):
                    offset = (binning["analysis"]["mt"][label][-1]-binning["analysis"]["mt"][label][0])*i_e
                    expression += "{STXSBIN}*(mt_max_score+{OFFSET})".format(STXSBIN=e, OFFSET=offset)
                    if not e is binning["stxs_stage1"]["lt"][label][-1]:
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
                for i_e, e in enumerate(binning["stxs_stage1"]["tt"][label]):
                    offset = (binning["analysis"]["tt"][label][-1]-binning["analysis"]["tt"][label][0])*i_e
                    expression += "{STXSBIN}*(tt_max_score+{OFFSET})".format(STXSBIN=e, OFFSET=offset)
                    if not e is binning["stxs_stage1"]["tt"][label][-1]:
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

    em_categories = []
    # Analysis shapes
    if "em" in args.channels:
        classes_em = ["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"]
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
                expression = ""
                for i_e, e in enumerate(binning["stxs_stage1"]["lt"][label]):
                    offsem = (binning["analysis"]["em"][label][-1]-binning["analysis"]["em"][label][0])*i_e
                    expression += "{STXSBIN}*(em_max_score+{OFFSem})".format(STXSBIN=e, OFFSem=offsem)
                    if not e is binning["stxs_stage1"]["lt"][label][-1]:
                        expression += " + "
                score_unrolled = Variable(
                    "em_max_score_unrolled",
                     VariableBinning(binning["analysis"]["em"][label+"_unrolled"]),
                     expression=expression)
                em_categories.append(
                    Category(
                        "{}_unrolled".format(label),
                        em,
                        Cuts(Cut("em_max_index=={index}".format(index=i), "exclusive_score"),
                             Cut("em_max_score>{}".format(1.0/len(classes_em)), "protect_unrolling")),
                        variable=score_unrolled))
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
    if args.gof_channel == None:
        signal_nicks = [
            "ggH", "qqH", "qqH_VBFTOPO_JET3VETO", "qqH_VBFTOPO_JET3",
            "qqH_REST", "qqH_PTJET1_GT200", "qqH_VH2JET", "ggH_0J",
            "ggH_1J_PTH_0_60", "ggH_1J_PTH_60_120", "ggH_1J_PTH_120_200",
            "ggH_1J_PTH_GT200", "ggH_GE2J_PTH_0_60", "ggH_GE2J_PTH_60_120",
            "ggH_GE2J_PTH_120_200", "ggH_GE2J_PTH_GT200", "ggH_VBFTOPO_JET3VETO",
            "ggH_VBFTOPO_JET3", "VH", "WH", "ZH", "ttH"
        ]
    else:
        signal_nicks = ["ggH", "qqH", "WH", "ZH", "ttH"]

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

    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_produce_shapes.log".format(args.tag), logging.INFO)
    main(args)
