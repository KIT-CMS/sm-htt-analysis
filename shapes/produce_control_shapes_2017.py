#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
ROOT.gErrorIgnoreLevel = ROOT.kError

from shape_producer.cutstring import Cut, Cuts
from shape_producer.systematics import Systematics, Systematic
from shape_producer.categories import Category
from shape_producer.binning import ConstantBinning, VariableBinning
from shape_producer.variable import Variable
from shape_producer.systematic_variations import Nominal, DifferentPipeline, SquareAndRemoveWeight, create_systematic_variations
from shape_producer.process import Process
from shape_producer.estimation_methods_2017 import *
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.era import Run2017
from shape_producer.channel import MTSM2017 as MT
from shape_producer.channel import ETSM2017 as ET
from shape_producer.channel import TTSM2017 as TT
from shape_producer.channel import EMSM2017 as EM
from shape_producer.channel import MMSM2017 as MM

from itertools import product

import argparse
import yaml

import logging
logger = logging.getLogger("")


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
        "--mm-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help=
        "Directories arranged as Artus output and containing a friend tree for mm."
    )
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
    parser.add_argument(
        "--QCD-extrap-fit",
        default=False,
        action='store_true',
        help="Create shapes for QCD extrapolation factor determination.")
    parser.add_argument(
        "--HIG16043",
        action="store_true",
        default=False,
        help="Create shapes of HIG16043 reference analysis.")
    parser.add_argument(
        "--num-threads",
        default=20,
        type=int,
        help="Number of threads to be used.")
    parser.add_argument(
        "--backend",
        default="classic",
        choices=["classic", "tdf"],
        type=str,
        help="Backend. Use classic or tdf.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    systematics_mt = Systematics("shapes_mt_2017.root", num_threads=args.num_threads, find_unique_objects=True)
    systematics_et = Systematics("shapes_et_2017.root", num_threads=args.num_threads, find_unique_objects=True)
    systematics_tt = Systematics("shapes_tt_2017.root", num_threads=args.num_threads, find_unique_objects=True)
    systematics_em = Systematics("shapes_em_2017.root", num_threads=args.num_threads, find_unique_objects=True)
    systematics_mm = Systematics("shapes_mm_2017.root", num_threads=args.num_threads, find_unique_objects=True)

    # Era
    era = Run2017(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory
    et_friend_directory = args.et_friend_directory
    mt_friend_directory = args.mt_friend_directory
    tt_friend_directory = args.tt_friend_directory
    em_friend_directory = args.em_friend_directory
    mm_friend_directory = args.mm_friend_directory

    ff_friend_directory = args.fake_factor_friend_directory

    mt = MT()
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
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, mt, friend_directory=mt_friend_directory)),
        "VH"    : Process("VH125",    VHEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "WH"    : Process("WH125",    WHEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZH"    : Process("ZH125",    ZHEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "ttH"   : Process("ttH125",   ttHEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "HWW"   : Process("HWW",      HWWEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        }
    mt_processes["FAKES"] = Process("jetFakes", NewFakeEstimationLT(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL"]], mt_processes["data"], friend_directory=mt_friend_directory+[ff_friend_directory]))
    mt_processes["FAKESEMB"] = Process("jetFakesEMB", NewFakeEstimationLT(era, directory, mt, [mt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], mt_processes["data"], friend_directory=mt_friend_directory+[ff_friend_directory]))

    mt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            mt_processes["data"], friend_directory=mt_friend_directory, extrapolation_factor=1.00))
    mt_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, mt,
            [mt_processes[process] for process in ["EMB", "ZL", "ZJ", "W", "TTJ", "TTL", "VVJ", "VVL"]],
            mt_processes["data"], friend_directory=mt_friend_directory, extrapolation_factor=1.00))


    et = ET()
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
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, et, friend_directory=et_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, et, friend_directory=et_friend_directory)),
        "VH"    : Process("VH125",    VHEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "WH"    : Process("WH125",    WHEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "ZH"    : Process("ZH125",    ZHEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "ttH"   : Process("ttH125",   ttHEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "HWW"   : Process("HWW",      HWWEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        }
    et_processes["FAKES"] = Process("jetFakes", NewFakeEstimationLT(era, directory, et, [et_processes[process] for process in ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL"]], et_processes["data"], friend_directory=et_friend_directory+[ff_friend_directory]))
    et_processes["FAKESEMB"] = Process("jetFakesEMB", NewFakeEstimationLT(era, directory, et, [et_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], et_processes["data"], friend_directory=et_friend_directory+[ff_friend_directory]))

    et_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, et,
            [et_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            et_processes["data"], friend_directory=et_friend_directory, extrapolation_factor=1.00))
    et_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, et,
            [et_processes[process] for process in ["EMB", "ZL", "ZJ", "W", "TTJ", "TTL", "VVJ", "VVL"]],
            et_processes["data"], friend_directory=et_friend_directory, extrapolation_factor=1.00))


    tt = TT()
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
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, tt, friend_directory=tt_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, tt, friend_directory=tt_friend_directory)),
        "VH"    : Process("VH125",    VHEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
        "WH"    : Process("WH125",    WHEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
        "ZH"    : Process("ZH125",    ZHEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
        "ttH"   : Process("ttH125",   ttHEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "HWW"   : Process("HWW",      HWWEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        }
    tt_processes["FAKESEMB"] = Process("jetFakesEMB", NewFakeEstimationTT(era, directory, tt, [tt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], tt_processes["data"], friend_directory=tt_friend_directory+[ff_friend_directory]))
    tt_processes["FAKES"] = Process("jetFakes", NewFakeEstimationTT(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL"]], tt_processes["data"], friend_directory=tt_friend_directory+[ff_friend_directory]))

    tt_processes["QCD"] = Process("QCD", QCDEstimation_ABCD_TT_ISO2(era, directory, tt,
            [tt_processes[process] for process in ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "TTL", "VVT", "VVJ", "VVL"]],
            tt_processes["data"], friend_directory=tt_friend_directory))
    tt_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_ABCD_TT_ISO2(era, directory, tt,
            [tt_processes[process] for process in ["EMB", "ZL", "ZJ", "W", "TTJ", "TTL", "VVJ", "VVL"]],
            tt_processes["data"], friend_directory=tt_friend_directory))

    em = EM()
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
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, em, friend_directory=em_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, em, friend_directory=em_friend_directory)),
        "VH"    : Process("VH125",    VHEstimation        (era, directory, em, friend_directory=em_friend_directory)),
        "WH"    : Process("WH125",    WHEstimation        (era, directory, em, friend_directory=em_friend_directory)),
        "ZH"    : Process("ZH125",    ZHEstimation        (era, directory, em, friend_directory=em_friend_directory)),
        "ttH"   : Process("ttH125",   ttHEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "HWW"   : Process("HWW",      HWWEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        }

    em_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, em, [em_processes[process] for process in ["ZTT", "ZL", "W", "TTT", "VVT", "VVL"]], em_processes["data"], extrapolation_factor=1.0, qcd_weight = Weight("em_qcd_extrap_up_Weight","qcd_weight")))
    em_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, em, [em_processes[process] for process in ["EMB", "ZL", "W", "VVL", "TTL"]], em_processes["data"], extrapolation_factor=1.0, qcd_weight = Weight("em_qcd_extrap_up_Weight","qcd_weight")))

    mm = MM()
    mm_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, mm, friend_directory=mm_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, mm, friend_directory=mm_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, mm, friend_directory=mm_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, mm, friend_directory=mm_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, mm, friend_directory=mm_friend_directory)),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, mm, friend_directory=mm_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, mm, friend_directory=mm_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, mm, friend_directory=mm_friend_directory)),
        }
    mm_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mm,
            [mm_processes[process] for process in ["ZTT", "ZL", "W", "TTT", "TTL", "VVT", "VVL"]],
            mm_processes["data"], friend_directory=mm_friend_directory, extrapolation_factor=2.0))


    # Variables and categories
    binning = yaml.load(open(args.binning))

    mt_categories = []
    et_categories = []
    tt_categories = []
    em_categories = []
    mm_categories = []

    variable_names = [
    #    "m_vis", "ptvis",
    #    "DiTauDeltaR",

    #    "m_sv", "pt_sv", "eta_sv",
    #    "m_sv_puppi", "pt_sv_puppi", "eta_sv_puppi",
    #    "m_fastmtt", "pt_fastmtt", "eta_fastmtt",
    #    "m_fastmtt_puppi", "pt_fastmtt_puppi", "eta_fastmtt_puppi",

        "ME_ggh", "ME_vbf", "ME_z2j_1", "ME_z2j_2",
        "ME_q2v1", "ME_q2v2", "ME_costheta1", "ME_costheta2", "ME_costhetastar", "ME_phi", "ME_phi1",
        "ME_ggh_vs_Z", "ME_vbf_vs_Z", "ME_vbf_vs_ggh",

    #    "pt_1", "pt_2", "eta_1", "eta_2",

    #    "mjj", "jdeta", "dijetpt",
    #    "njets", "jpt_1", "jpt_2", "jeta_1", "jeta_2",
    #    "nbtag", "bpt_1", "bpt_2", "beta_1", "beta_2",

    #   "met", "mt_1", "mt_2", "pt_tt", "pZetaMissVis", "pt_ttjj", "mt_tot", "mTdileptonMET",
    #    "puppimet", "mt_1_puppi", "mt_2_puppi", "pt_tt_puppi", "pZetaPuppiMissVis", "pt_ttjj_puppi", "mt_tot_puppi", "mTdileptonMET_puppi",
    #    "NNrecoil_pt", "nnmet", "mt_1_nn", "mt_2_nn", "pt_tt_nn", "pZetaNNMissVis", "pt_ttjj_nn", "mt_tot_nn", "mTdileptonMET_nn",

        "metParToZ", "metPerpToZ",
        "puppimetParToZ", "puppimetPerpToZ",
    ]

    if "mt" in args.channels:
        variables = [Variable(v,VariableBinning(binning["control"]["mt"][v]["bins"]), expression=binning["control"]["mt"][v]["expression"]) for v in variable_names]
        cuts = Cuts()
        for name, var in zip(variable_names, variables):
            mt_categories.append(
                Category(
                    name,
                    mt,
                    cuts,
                    variable=var))

    if "et" in args.channels:
        variables = [Variable(v,VariableBinning(binning["control"]["et"][v]["bins"]), expression=binning["control"]["et"][v]["expression"]) for v in variable_names]
        cuts = Cuts()
        for name, var in zip(variable_names, variables):
            et_categories.append(
                Category(
                    name,
                    et,
                    cuts,
                    variable=var))

    if "tt" in args.channels:
        variables = [Variable(v,VariableBinning(binning["control"]["tt"][v]["bins"]), expression=binning["control"]["tt"][v]["expression"]) for v in variable_names]
        cuts = Cuts()
        for name, var in zip(variable_names, variables):
            tt_categories.append(
                Category(
                    name,
                    tt,
                    cuts,
                    variable=var))

    if "em" in args.channels:
        variables = [Variable(v,VariableBinning(binning["control"]["em"][v]["bins"]), expression=binning["control"]["em"][v]["expression"]) for v in variable_names]
        cuts = Cuts()
        for name, var in zip(variable_names, variables):
            em_categories.append(
                Category(
                    name,
                    em,
                    cuts,
                    variable=var))

    if "mm" in args.channels:
        variables = [Variable(v,VariableBinning(binning["control"]["mm"][v]["bins"]), expression=binning["control"]["mm"][v]["expression"]) for v in variable_names]
        variables.append(Variable("m_vis_high",ConstantBinning(95,50.0,1000.0),expression="m_vis"))
        variable_names.append("m_vis_high")
        cuts = Cuts()
        for name, var in zip(variable_names, variables):
            mm_categories.append(
                Category(
                    name,
                    mm,
                    cuts,
                    variable=var))
            mm_categories.append(
                Category(
                    name+"_peak",
                    mm,
                    Cuts(Cut("m_vis > 70 && m_vis < 110","m_vis_peak")),
                    variable=var))

    # Nominal histograms
    if "mt" in args.channels:
        for process, category in product(mt_processes.values(), mt_categories):
            systematics_mt.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))

    if "et" in args.channels:
        for process, category in product(et_processes.values(), et_categories):
            systematics_et.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))

    if "tt" in args.channels:
        for process, category in product(tt_processes.values(), tt_categories):
            systematics_tt.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))

    if "em" in args.channels:
        for process, category in product(em_processes.values(), em_categories):
            systematics_em.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))

    if "mm" in args.channels:
        for process, category in product(mm_processes.values(), mm_categories):
            systematics_mm.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))


    # Produce histograms
    if "mt" in args.channels: systematics_mt.produce()
    if "et" in args.channels: systematics_et.produce()
    if "tt" in args.channels: systematics_tt.produce()
    if "em" in args.channels: systematics_em.produce()
    if "mm" in args.channels: systematics_mm.produce()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_shapes.log", logging.INFO)
    main(args)
