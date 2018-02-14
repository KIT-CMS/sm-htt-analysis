#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shape_producer.cutstring import Cut, Cuts
from shape_producer.systematics import Systematics, Systematic
from shape_producer.categories import Category
from shape_producer.binning import ConstantBinning, VariableBinning
from shape_producer.variable import Variable
from shape_producer.systematic_variations import Nominal, DifferentPipeline, SquareAndRemoveWeight, create_systematic_variations
from shape_producer.process import Process
from shape_producer.estimation_methods_2016 import *
from shape_producer.estimation_methods import *
from shape_producer.era import Run2016
from shape_producer.channel import EESM, EMSM, MMSM, ETSM, MTSM, TTSM

from itertools import product

import argparse
import yaml
import copy

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
        "-d",
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "-f",
        "--friend-directory",
        required=True,
        type=str,
        help="Directory with friend trees containing calibrated impact parameters.")
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

    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    systematics = Systematics("impact_parameter_shapes.root", num_threads=args.num_threads)

    # Era
    era = Run2016(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory
    ee = EESM()
    ee_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, ee, friend_directory=args.friend_directory)),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, ee, friend_directory=args.friend_directory)),
        "ggH"   : Process("ggH",      ggHEstimation   (era, directory, ee, friend_directory=args.friend_directory)),
        "qqH"   : Process("qqH",      qqHEstimation   (era, directory, ee, friend_directory=args.friend_directory)),
        "VH"    : Process("VH",       VHEstimation    (era, directory, ee, friend_directory=args.friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimationLL (era, directory, ee, friend_directory=args.friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationLL  (era, directory, ee, friend_directory=args.friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationLL  (era, directory, ee, friend_directory=args.friend_directory)),
        "W"     : Process("W",        WEstimation     (era, directory, ee, friend_directory=args.friend_directory)),
        "TT"    : Process("TT",       TTEstimation    (era, directory, ee, friend_directory=args.friend_directory)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, ee, friend_directory=args.friend_directory)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, ee, friend_directory=args.friend_directory))
        }
    ee_processes["QCD"] = Process("QCD", QCDEstimationET(era, directory, ee, [ee_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TT", "VV", "EWK"]], ee_processes["data"], extrapolation_factor=1.0))
    ee_processes["MC"] = Process("MC", SumUpEstimationMethod("MC", "nominal", era, directory, ee, [ee_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TT", "VV", "EWK", "QCD", "HTT"]]))
    em = EMSM()
    em.cuts.remove("ele_iso")
    em.cuts.remove("muon_iso")
    #em.cuts.remove("diLepMetMt")
    #em.cuts.get("pzeta").invert()
    em_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, em, friend_directory=args.friend_directory)),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, em, friend_directory=args.friend_directory)),
        "ggH"   : Process("ggH",      ggHEstimation   (era, directory, em, friend_directory=args.friend_directory)),
        "qqH"   : Process("qqH",      qqHEstimation   (era, directory, em, friend_directory=args.friend_directory)),
        "VH"    : Process("VH",       VHEstimation    (era, directory, em, friend_directory=args.friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimationLL (era, directory, em, friend_directory=args.friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationLL  (era, directory, em, friend_directory=args.friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationLL  (era, directory, em, friend_directory=args.friend_directory)),
        "W"     : Process("W",        WEstimation     (era, directory, em, friend_directory=args.friend_directory)),
        "TT"    : Process("TT",       TTEstimation    (era, directory, em, friend_directory=args.friend_directory)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, em, friend_directory=args.friend_directory)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, em, friend_directory=args.friend_directory))
        }
    em_processes["QCD"] = Process("QCD", QCDEstimationMT(era, directory, em, [em_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TT", "VV", "EWK"]], em_processes["data"], extrapolation_factor=1.0))
    em_processes["MC"] = Process("MC", SumUpEstimationMethod("MC", "nominal", era, directory, em, [em_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TT", "VV", "EWK", "QCD", "HTT"]]))
    mm = MMSM()
    mm_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, mm, friend_directory=args.friend_directory)),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, mm, friend_directory=args.friend_directory)),
        "ggH"   : Process("ggH",      ggHEstimation   (era, directory, mm, friend_directory=args.friend_directory)),
        "qqH"   : Process("qqH",      qqHEstimation   (era, directory, mm, friend_directory=args.friend_directory)),
        "VH"    : Process("VH",       VHEstimation    (era, directory, mm, friend_directory=args.friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimationLL (era, directory, mm, friend_directory=args.friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationLL  (era, directory, mm, friend_directory=args.friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationLL  (era, directory, mm, friend_directory=args.friend_directory)),
        "W"     : Process("W",        WEstimation     (era, directory, mm, friend_directory=args.friend_directory)),
        "TT"    : Process("TT",       TTEstimation    (era, directory, mm, friend_directory=args.friend_directory)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, mm, friend_directory=args.friend_directory)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, mm, friend_directory=args.friend_directory))
        }
    mm_processes["QCD"] = Process("QCD", QCDEstimationMT(era, directory, mm, [mm_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TT", "VV", "EWK"]], mm_processes["data"], extrapolation_factor=1.0))
    mm_processes["MC"] = Process("MC", SumUpEstimationMethod("MC", "nominal", era, directory, mm, [mm_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TT", "VV", "EWK", "QCD", "HTT"]]))
    mt = MTSM()
    mt.cuts.remove("muon_iso")
    mt.cuts.remove("tau_iso")
    mt.cuts.remove("m_t")
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, mt, friend_directory=args.friend_directory)),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, mt, friend_directory=args.friend_directory)),
        "ggH"   : Process("ggH",      ggHEstimation   (era, directory, mt, friend_directory=args.friend_directory)),
        "qqH"   : Process("qqH",      qqHEstimation   (era, directory, mt, friend_directory=args.friend_directory)),
        "VH"    : Process("VH",       VHEstimation    (era, directory, mt, friend_directory=args.friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, mt, friend_directory=args.friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationMTSM(era, directory, mt, friend_directory=args.friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationMT  (era, directory, mt, friend_directory=args.friend_directory)),
        "WT"    : Process("WT",       WTEstimation    (era, directory, mt, friend_directory=args.friend_directory)),
        "WL"    : Process("WL",       WLEstimation    (era, directory, mt, friend_directory=args.friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationMT (era, directory, mt, friend_directory=args.friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationMT (era, directory, mt, friend_directory=args.friend_directory)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, mt, friend_directory=args.friend_directory)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, mt, friend_directory=args.friend_directory))
        }
    mt_processes["QCD"] = Process("QCD", QCDEstimationMT(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZJ", "ZL", "WT", "WL", "TTT", "TTJ", "VV", "EWK"]], mt_processes["data"], extrapolation_factor=1.17))
    mt_processes["MC"] = Process("MC", SumUpEstimationMethod("MC", "nominal", era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZJ", "ZL", "WT", "WL", "TTT", "TTJ", "VV", "EWK", "QCD", "HTT"]]))
    et = ETSM()
    et.cuts.remove("ele_iso")
    et.cuts.remove("tau_iso")
    et_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, et, friend_directory=args.friend_directory)),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, et, friend_directory=args.friend_directory)),
        "ggH"   : Process("ggH",      ggHEstimation   (era, directory, et, friend_directory=args.friend_directory)),
        "qqH"   : Process("qqH",      qqHEstimation   (era, directory, et, friend_directory=args.friend_directory)),
        "VH"    : Process("VH",       VHEstimation    (era, directory, et, friend_directory=args.friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, et, friend_directory=args.friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationETSM(era, directory, et, friend_directory=args.friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationET  (era, directory, et, friend_directory=args.friend_directory)),
        "WT"    : Process("WT",       WTEstimation    (era, directory, et, friend_directory=args.friend_directory)),
        "WL"    : Process("WL",       WLEstimation    (era, directory, et, friend_directory=args.friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationET (era, directory, et, friend_directory=args.friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationET (era, directory, et, friend_directory=args.friend_directory)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, et, friend_directory=args.friend_directory)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, et, friend_directory=args.friend_directory))
        }
    et_processes["QCD"] = Process("QCD", QCDEstimationET(era, directory, et, [et_processes[process] for process in ["ZTT", "ZJ", "ZL", "WT", "WL", "TTT", "TTJ", "VV", "EWK"]], et_processes["data"], extrapolation_factor=1.16))
    et_processes["MC"] = Process("MC", SumUpEstimationMethod("MC", "nominal", era, directory, et, [et_processes[process] for process in ["ZTT", "ZJ", "ZL", "WT", "WL", "TTT", "TTJ", "VV", "EWK", "QCD", "HTT"]]))
    tt = TTSM()
    tt.cuts.remove("tau_1_iso")
    #tt.cuts.remove("tau_2_iso")
    tt_processes = {
        "data"  : Process("data_obs", DataEstimation (era, directory, tt, friend_directory=args.friend_directory)),
        "HTT"   : Process("HTT",      HTTEstimation  (era, directory, tt, friend_directory=args.friend_directory)),
        "ggH"   : Process("ggH",      ggHEstimation  (era, directory, tt, friend_directory=args.friend_directory)),
        "qqH"   : Process("qqH",      qqHEstimation  (era, directory, tt, friend_directory=args.friend_directory)),
        "VH"    : Process("VH",       VHEstimation   (era, directory, tt, friend_directory=args.friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimationTT(era, directory, tt, friend_directory=args.friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationTT (era, directory, tt, friend_directory=args.friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationTT (era, directory, tt, friend_directory=args.friend_directory)),
        "W"     : Process("W",        WEstimation    (era, directory, tt, friend_directory=args.friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationTT(era, directory, tt, friend_directory=args.friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationTT(era, directory, tt, friend_directory=args.friend_directory)),
        "VV"    : Process("VV",       VVEstimation   (era, directory, tt, friend_directory=args.friend_directory)),
        "EWK"   : Process("EWK",      EWKEstimation  (era, directory, tt, friend_directory=args.friend_directory))
        }
    tt_processes["QCD"] = Process("QCD", QCDEstimationTT(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK"]], tt_processes["data"]))
    tt_processes["MC"] = Process("MC", SumUpEstimationMethod("MC", "nominal", era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK", "QCD", "HTT"]]))

    # Variables and categories
    #binning_ll_0 = [-0.1, -0.08, -0.06, -0.04, -0.02, -0.015, -0.01, -0.008, -0.006, -0.004, -0.003, -0.002, -0.001, 0.0, 0.001, 0.002, 0.003, 0.004, 0.006, 0.008, 0.01, 0.015, 0.02, 0.04, 0.06, 0.08, 0.1]
    #binning_ll_Z = [-0.15, -0.1, -0.08, -0.06, -0.04, -0.02, -0.015, -0.01, -0.008, -0.006, -0.004, -0.003, -0.002, -0.001, 0.0, 0.001, 0.002, 0.003, 0.004, 0.006, 0.008, 0.01, 0.015, 0.02, 0.04, 0.06, 0.08, 0.1, 0.15]
    #binning_ll_0_raw = [-0.05, -0.04, -0.03, -0.02, -0.015, -0.0125, -0.01, -0.009, -0.008, -0.007, -0.006, -0.005, -0.0045, -0.004, -0.0035, -0.003, -0.0025, -0.002, -0.0015, -0.001, -0.0006, -0.0003, 0.0, 0.0003, 0.0006, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.0125, 0.015, 0.02, 0.03, 0.04, 0.05]
    binning_ll_Z_raw = [0.0001, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.001, 0.00125, 0.0015, 0.00175, 0.002, 0.00225, 0.0025, 0.00275, 0.003, 0.00325, 0.0035, 0.00375, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.0065, 0.007, 0.0075, 0.008, 0.0085, 0.009, 0.0095, 0.01, 0.011, 0.012, 0.013, 0.014, 0.015, 0.016, 0.018, 0.02, 0.0225, 0.025, 0.0275, 0.03, 0.035, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.15, 0.2]
    binning_ll_0_raw = [0.0001, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.001, 0.00125, 0.0015, 0.00175, 0.002, 0.00225, 0.0025, 0.00275, 0.003, 0.00325, 0.0035, 0.00375, 0.004, 0.00425, 0.0045, 0.00475, 0.005, 0.0055, 0.006, 0.0065, 0.007, 0.0075, 0.008, 0.0085, 0.009, 0.0095, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045]
    binning_ll_Zerr_raw = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 30.0, 45.0, 70.0, 100.0, 150.0]
    binning_ll_0err_raw = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0, 2.25, 2.5, 2.75, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 30.0]
    binning_et_Z_raw = [0.001, 0.004, 0.01, 0.02, 0.04, 0.2]
    binning_et_0_raw = [0.0005, 0.002, 0.005, 0.045]
    binning_mt_Z_raw = [0.0003, 0.0006, 0.001, 0.0015, 0.00225, 0.003, 0.004, 0.0055, 0.0075, 0.01, 0.015, 0.02, 0.04, 0.2]
    binning_mt_0_raw = [0.0001, 0.0003, 0.0006, 0.001, 0.00175, 0.0025, 0.005, 0.01, 0.045]
    binning_em_Z_raw = [0.0003, 0.0006, 0.001, 0.0015, 0.00225, 0.003, 0.004, 0.0055, 0.0075, 0.01, 0.015, 0.02, 0.04, 0.08, 0.15, 0.2] # 0.08, 0.14 are only to keep splines in good region
    binning_em_0_raw = [0.0001, 0.0003, 0.0006, 0.001, 0.00175, 0.0025, 0.005, 0.01, 0.02, 0.032, 0.045] #0.02, 0.032 are only to keep splines in good region
    
    binning_ll_0 = []
    for i in range(len(binning_ll_0_raw)):
        binning_ll_0.append(-1*binning_ll_0_raw[-i-1])
    binning_ll_0 += [0.0] + binning_ll_0_raw
    binning_ll_Z = []
    for i in range(len(binning_ll_Z_raw)):
        binning_ll_Z.append(-1*binning_ll_Z_raw[-i-1])
    binning_ll_Z += [0.0] + binning_ll_Z_raw
    binning_ll_0err = []
    for i in range(len(binning_ll_0err_raw)):
        binning_ll_0err.append(-1*binning_ll_0err_raw[-i-1])
    binning_ll_0err += [0.0] + binning_ll_0err_raw
    binning_ll_Zerr = []
    for i in range(len(binning_ll_Zerr_raw)):
        binning_ll_Zerr.append(-1*binning_ll_Zerr_raw[-i-1])
    binning_ll_Zerr += [0.0] + binning_ll_Zerr_raw
    binning_et_0 = []
    for i in range(len(binning_et_0_raw)):
        binning_et_0.append(-1*binning_et_0_raw[-i-1])
    binning_et_0 += binning_et_0_raw
    binning_et_Z = []
    for i in range(len(binning_et_Z_raw)):
        binning_et_Z.append(-1*binning_et_Z_raw[-i-1])
    binning_et_Z += binning_et_Z_raw
    binning_et_0err = []
    binning_mt_0 = []
    for i in range(len(binning_mt_0_raw)):
        binning_mt_0.append(-1*binning_mt_0_raw[-i-1])
    binning_mt_0 += binning_mt_0_raw
    binning_mt_Z = []
    for i in range(len(binning_mt_Z_raw)):
        binning_mt_Z.append(-1*binning_mt_Z_raw[-i-1])
    binning_mt_Z += [0.0] + binning_mt_Z_raw
    binning_mt_0err = []
    binning_em_0 = []
    for i in range(len(binning_em_0_raw)):
        binning_em_0.append(-1*binning_em_0_raw[-i-1])
    binning_em_0 += binning_em_0_raw
    binning_em_Z = []
    for i in range(len(binning_em_Z_raw)):
        binning_em_Z.append(-1*binning_em_Z_raw[-i-1])
    binning_em_Z += [0.0] + binning_em_Z_raw
    binning_em_0err = []
    
    binning_tau = [-0.1, -0.08, -0.06, -0.04, -0.02, -0.015, -0.01, -0.008, -0.006, -0.004, -0.002, 0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.015, 0.02, 0.04, 0.06, 0.08, 0.1]
    d0_1 = Variable("d0_1", VariableBinning(binning_ll_0))
    d0_1_calib = Variable("d0_1_calib", VariableBinning(binning_ll_0))
    d0_1_calib_all = Variable("d0_1_calib_all", VariableBinning(binning_ll_0))
    d0_te = Variable("d0_1", VariableBinning(binning_mt_0))
    d0_te_calib = Variable("d0_1_calib", VariableBinning(binning_mt_0))
    d0_te_calib_all = Variable("d0_1_calib_all", VariableBinning(binning_mt_0))
    d0_tm = Variable("d0_1", VariableBinning(binning_mt_0))
    d0_tm_calib = Variable("d0_1_calib", VariableBinning(binning_mt_0))
    d0_tm_calib_all = Variable("d0_1_calib_all", VariableBinning(binning_mt_0))
    #d0_1 = Variable("m_vis", VariableBinning([50.+x*5. for x in range(21)]))
    d0_2 = Variable("d0_2", VariableBinning(binning_tau))
    #d0_2 = Variable("m_vis", VariableBinning([50.+x*5. for x in range(21)]))
    dZ_1 = Variable("dZ_1", VariableBinning(binning_ll_Z))
    dZ_1_calib = Variable("dZ_1_calib", VariableBinning(binning_ll_Z))
    dZ_1_calib_all = Variable("dZ_1_calib_all", VariableBinning(binning_ll_Z))
    dZ_te = Variable("dZ_1", VariableBinning(binning_mt_Z))
    dZ_te_calib = Variable("dZ_1_calib", VariableBinning(binning_mt_Z))
    dZ_te_calib_all = Variable("dZ_1_calib_all", VariableBinning(binning_mt_Z))
    dZ_tm = Variable("dZ_1", VariableBinning(binning_mt_Z))
    dZ_tm_calib = Variable("dZ_1_calib", VariableBinning(binning_mt_Z))
    dZ_tm_calib_all = Variable("dZ_1_calib_all", VariableBinning(binning_mt_Z))
    dZ_2 = Variable("dZ_2", VariableBinning(binning_tau))
    DCA0_1 = Variable("DCA0_1", VariableBinning(binning_ll_0err), "d0_1/lep1ErrD0")
    DCAZ_1 = Variable("DCAZ_1", VariableBinning(binning_ll_Zerr), "dZ_1/lep1ErrDz")
    DCA0_2 = Variable("DCA0_2", VariableBinning(binning_ll_0err), "d0_2/lep2ErrD0")
    DCAZ_2 = Variable("DCAZ_2", VariableBinning(binning_ll_Zerr), "dZ_2/lep2ErrDz")
    d0_em_te = Variable("d0_1", VariableBinning(binning_em_0))
    d0_em_te_calib_all = Variable("d0_1_calib_all", VariableBinning(binning_em_0))
    d0_em_tm = Variable("d0_2", VariableBinning(binning_em_0))
    d0_em_tm_calib_all = Variable("d0_2_calib_all", VariableBinning(binning_em_0))
    dZ_em_te = Variable("dZ_1", VariableBinning(binning_em_Z))
    dZ_em_te_calib_all = Variable("dZ_1_calib_all", VariableBinning(binning_em_Z))
    dZ_em_tm = Variable("dZ_2", VariableBinning(binning_em_Z))
    dZ_em_tm_calib_all = Variable("dZ_2_calib_all", VariableBinning(binning_em_Z))
    
    m_vis = Variable("m_vis", VariableBinning([50.+x*5. for x in range(21)]))
    mT_1 = Variable("mt_1", VariableBinning([0.+x*5. for x in range(41)]))
    mT_2 = Variable("mt_2", VariableBinning([0.+x*5. for x in range(41)]))
    met = Variable("met", VariableBinning([0.+x*5. for x in range(41)]))

    ee_categories = []
    if "ee" in args.channels:
        ee_categories.append(
            Category(
                "m_vis",
                ee,
                Cuts(),
                variable=m_vis))
        ee_categories.append(
            Category(
                "d0_e",
                ee,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=d0_1))
        ee_categories.append(
            Category(
                "dZ_e",
                ee,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=dZ_1))
        ee_categories.append(
            Category(
                "DCA0_e",
                ee,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=DCA0_1))
        ee_categories.append(
            Category(
                "DCAZ_e",
                ee,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=DCAZ_1))
        #calibrated
        '''ee_categories.append(
            Category(
                "d0_e",
                ee,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=d0_1_calib))
        ee_categories.append(
            Category(
                "dZ_e",
                ee,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=dZ_1_calib))
        ee_categories.append(
            Category(
                "d0_e",
                ee,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=d0_1_calib_all))
        ee_categories.append(
            Category(
                "dZ_e",
                ee,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=dZ_1_calib_all))
    '''
    em_categories = []
    if "em" in args.channels:
        '''em_categories.append(
            Category(
                "m_vis_te",
                em,
                Cuts(
                    Cut("iso_1<0.1", "ele_iso"),
                    Cut("iso_2>0.15&&iso_2<0.25", "muon_antiiso")),
                    #Cut("pZetaMissVis<-50.", "pzetatight")),
                variable=m_vis))
        em_categories.append(
            Category(
                "m_vis_tm",
                em,
                Cuts(
                    Cut("iso_1>0.1&&iso_1<0.2", "ele_antiiso"),
                    Cut("iso_2<0.15", "muon_iso")),
                variable=m_vis))'''
        em_categories.append(
            Category(
                "d0_em_te",
                em,
                Cuts(
                    Cut("iso_1<0.15", "ele_iso"),
                    Cut("iso_2<0.2", "muon_iso"),
                    Cut("m_vis<80", "Zpeak")),
                variable=d0_em_te))
        em_categories.append(
            Category(
                "d0_em_tm",
                em,
                Cuts(
                    Cut("iso_1<0.15", "ele_iso"),
                    Cut("iso_2<0.2", "muon_iso"),
                    Cut("m_vis<80", "Zpeak")),
                variable=d0_em_tm))
        em_categories.append(
            Category(
                "dZ_em_te",
                em,
                Cuts(
                    Cut("iso_1<0.15", "ele_iso"),
                    Cut("iso_2<0.2", "muon_iso"),
                    Cut("m_vis<80", "Zpeak")),
                variable=dZ_em_te))
        em_categories.append(
            Category(
                "dZ_em_tm",
                em,
                Cuts(
                    Cut("iso_1<0.15", "ele_iso"),
                    Cut("iso_2<0.2", "muon_iso"),
                    Cut("m_vis<80", "Zpeak")),
                variable=dZ_em_tm))
        #calibrated
        '''em_categories.append(
            Category(
                "d0_em_te",
                em,
                Cuts(
                    Cut("iso_1<0.15", "ele_iso"),
                    Cut("iso_2<0.2", "muon_iso"),
                    Cut("m_vis<80", "Zpeak")),
                variable=d0_em_te_calib_all))
        em_categories.append(
            Category(
                "d0_em_tm",
                em,
                Cuts(
                    Cut("iso_1<0.15", "ele_iso"),
                    Cut("iso_2<0.2", "muon_iso"),
                    Cut("m_vis<80", "Zpeak")),
                variable=d0_em_tm_calib_all))
        em_categories.append(
            Category(
                "dZ_em_te",
                em,
                Cuts(
                    Cut("iso_1<0.15", "ele_iso"),
                    Cut("iso_2<0.2", "muon_iso"),
                    Cut("m_vis<80", "Zpeak")),
                variable=dZ_em_te_calib_all))
        em_categories.append(
            Category(
                "dZ_em_tm",
                em,
                Cuts(
                    Cut("iso_1<0.15", "ele_iso"),
                    Cut("iso_2<0.2", "muon_iso"),
                    Cut("m_vis<80", "Zpeak")),
                variable=dZ_em_tm_calib_all))
    '''
    mm_categories = []
    if "mm" in args.channels:
        mm_categories.append(
            Category(
                "m_vis",
                mm,
                Cuts(),
                variable=m_vis))
        mm_categories.append(
            Category(
                "d0_m",
                mm,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=d0_1))
        mm_categories.append(
            Category(
                "dZ_m",
                mm,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=dZ_1))
        mm_categories.append(
            Category(
                "DCA0_m",
                mm,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=DCA0_1))
        mm_categories.append(
            Category(
                "DCAZ_m",
                mm,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=DCAZ_1))
        #calibrated
        '''mm_categories.append(
            Category(
                "d0_m",
                mm,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=d0_1_calib))
        mm_categories.append(
            Category(
                "dZ_m",
                mm,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=dZ_1_calib))
        mm_categories.append(
            Category(
                "d0_m",
                mm,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=d0_1_calib_all))
        mm_categories.append(
            Category(
                "dZ_m",
                mm,
                Cuts(
                    Cut("m_vis>80 && m_vis<100", "Zpeak")
                    ),
                variable=dZ_1_calib_all))
    '''
    et_categories = []
    if "et" in args.channels:
        et_categories.append(
            Category(
                "d0_te",
                et,
                Cuts(
                    Cut("iso_1<0.1", "ele_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=d0_te))
        et_categories.append(
            Category(
                "dZ_te",
                et,
                Cuts(
                    Cut("iso_1<0.1", "ele_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=dZ_te))
        et_categories.append(
            Category(
                "d0_te",
                et,
                Cuts(
                    Cut("iso_1<0.1", "ele_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=d0_te_calib))
        et_categories.append(
            Category(
                "dZ_te",
                et,
                Cuts(
                    Cut("iso_1<0.1", "ele_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=dZ_te_calib))
        '''
        et_categories.append(
            Category(
                "m_vis",
                et,
                Cuts(
                    #Cut("m_vis>60 && m_vis<75", "Zpeak"),
                    Cut("nbtag==0", "bveto"),
                    Cut("iso_1<0.1", "ele_iso"),
                    Cut("mt_2<100", "tau_mt"),
                    Cut("abs(eta_2)<1.0", "tau_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5 && byMediumIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_antiiso")),
                variable=m_vis))
        et_categories.append(
            Category(
                "d0_te",
                et,
                Cuts(
                    Cut("m_vis>60 && m_vis<75", "Zpeak"),
                    Cut("nbtag==0", "bveto"),
                    Cut("iso_1<0.1", "ele_iso"),
                    Cut("mt_2<100", "tau_mt"),
                    Cut("abs(eta_2)<1.0", "tau_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5 && byMediumIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_antiiso")),
                variable=d0_te))
        et_categories.append(
            Category(
                "dZ_te",
                et,
                Cuts(
                    Cut("m_vis>60 && m_vis<75", "Zpeak"),
                    Cut("nbtag==0", "bveto"),
                    Cut("iso_1<0.1", "ele_iso"),
                    Cut("mt_2<100", "tau_mt"),
                    Cut("abs(eta_2)<1.0", "tau_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5 && byMediumIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_antiiso")),
                variable=dZ_te))
        et_categories.append(
            Category(
                "d0_t",
                et,
                Cuts(
                    Cut("m_vis>60 && m_vis<75", "Zpeak"),
                    Cut("iso_1>0.1 && iso_1<0.2", "ele_antiiso"),
                    Cut("abs(eta_1)<1.0", "ele_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=d0_2))
        et_categories.append(
            Category(
                "dZ_t",
                et,
                Cuts(
                    Cut("m_vis>60 && m_vis<75", "Zpeak"),
                    Cut("iso_1>0.1 && iso_1<0.2", "ele_antiiso"),
                    Cut("abs(eta_1)<1.0", "ele_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=dZ_2))'''
    mt_categories = []
    if "mt" in args.channels:
        mt_categories.append(
            Category(
                "d0_tm",
                mt,
                Cuts(
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=d0_tm))
        mt_categories.append(
            Category(
                "dZ_tm",
                mt,
                Cuts(
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=dZ_tm))
        mt_categories.append(
            Category(
                "d0_tm",
                mt,
                Cuts(
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=d0_tm_calib))
        mt_categories.append(
            Category(
                "dZ_tm",
                mt,
                Cuts(
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=dZ_tm_calib))
        '''
        mt_categories.append(
            Category(
                "m_vis",
                mt,
                Cuts(
                    #Cut("m_vis>55 && m_vis<75", "Zpeak"),
                    Cut("nbtag==0", "bveto"),
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("mt_2<100", "tau_mt"),
                    Cut("abs(eta_2)<1.0", "tau_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5 && byMediumIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_antiiso")),
                variable=m_vis))
        mt_categories.append(
            Category(
                "d0_tm",
                mt,
                Cuts(
                    Cut("m_vis>55 && m_vis<75", "Zpeak"),
                    Cut("nbtag==0", "bveto"),
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("mt_2<100", "tau_mt"),
                    Cut("abs(eta_2)<1.0", "tau_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5 && byMediumIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_antiiso")),
                variable=d0_tm))
        mt_categories.append(
            Category(
                "dZ_tm",
                mt,
                Cuts(
                    Cut("m_vis>55 && m_vis<75", "Zpeak"),
                    Cut("nbtag==0", "bveto"),
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("mt_2<100", "tau_mt"),
                    Cut("abs(eta_2)<1.0", "tau_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5 && byMediumIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_antiiso")),
                variable=dZ_tm))
        mt_categories.append(
            Category(
                "d0_t",
                mt,
                Cuts(
                    Cut("m_vis>55 && m_vis<70", "Zpeak"),
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1>0.15 && iso_1<0.25", "muon_antiiso"),
                    Cut("abs(eta_1)<1.0", "muon_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=d0_2))
        mt_categories.append(
            Category(
                "dZ_t",
                mt,
                Cuts(
                    Cut("m_vis>55 && m_vis<70", "Zpeak"),
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1>0.15 && iso_1<0.25", "muon_antiiso"),
                    Cut("abs(eta_1)<1.0", "muon_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=dZ_2))
        mt_categories.append(
            Category(
                "d0_f",
                mt,
                Cuts(
                    #Cut("m_vis>55 && m_vis<70", "antiZpeak"),
                    Cut("mt_1>70 && mt_1 < 100", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=d0_2))
        mt_categories.append(
            Category(
                "dZ_f",
                mt,
                Cuts(
                    Cut("m_vis>95", "antiZpeak"),
                    Cut("mt_1>70 && mt_1 < 100", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=dZ_2))
        mt_categories.append(
            Category(
                "d0_tt",
                mt,
                Cuts(
                    Cut("mt_1>150", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=d0_2))
        mt_categories.append(
            Category(
                "dZ_tt",
                mt,
                Cuts(
                    Cut("mt_1>150", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_iso")),
                variable=dZ_2))'''

    tt_categories = []
    if "tt" in args.channels:
        tt_categories.append(
            Category(
                "d0_t2",
                tt,
                Cuts(
                    Cut("m_vis>60 && m_vis<80", "Zpeak"),
                    Cut("abs(eta_1)<1.0", "eta_tau_1"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_1<0.5 && byLooseIsolationMVArun2v1DBoldDMwLT_1>0.5", "tau_1_antiiso")),
                variable=d0_2))
        tt_categories.append(
            Category(
                "dZ_t2",
                tt,
                Cuts(
                    Cut("m_vis>60 && m_vis<80", "Zpeak"),
                    Cut("abs(eta_1)<1.0", "eta_tau_1"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_1<0.5 && byLooseIsolationMVArun2v1DBoldDMwLT_1>0.5", "tau_1_antiiso")),
                variable=dZ_2))
    # Nominal histograms
    # yapf: enable
    if "ee" in args.channels:
        for process, category in product(ee_processes.values(), ee_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))
    if "em" in args.channels:
        for process, category in product(em_processes.values(), em_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))
    if "mm" in args.channels:
        for process, category in product(mm_processes.values(), mm_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))
    if "et" in args.channels:
        for process, category in product(et_processes.values(), et_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))
    if "mt" in args.channels:
        for process, category in product(mt_processes.values(), mt_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))
    if "tt" in args.channels:
        for process, category in product(tt_processes.values(), tt_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))

    # Produce histograms
    systematics.produce()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_shapes.log", logging.INFO)
    main(args)
