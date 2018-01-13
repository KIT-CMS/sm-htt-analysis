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
from shape_producer.channel import ETSM, MTSM, TTSM

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
    mt = MTSM()
    mt.cuts.remove("muon_iso")
    mt.cuts.remove("tau_iso")
    mt.cuts.remove("m_t")
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, mt)),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, mt)),
        "ggH"   : Process("ggH",      ggHEstimation   (era, directory, mt)),
        "qqH"   : Process("qqH",      qqHEstimation   (era, directory, mt)),
        "VH"    : Process("VH",       VHEstimation    (era, directory, mt)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, mt)),
        "ZL"    : Process("ZL",       ZLEstimationMTSM(era, directory, mt)),
        "ZJ"    : Process("ZJ",       ZJEstimationMT  (era, directory, mt)),
        "W"     : Process("W",        WEstimation     (era, directory, mt)),
        "TTT"   : Process("TTT",      TTTEstimationMT (era, directory, mt)),
        "TTJ"   : Process("TTJ",      TTJEstimationMT (era, directory, mt)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, mt)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, mt))
        }
    mt_processes["QCD"] = Process("QCD", QCDEstimationMT(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK"]], mt_processes["data"], extrapolation_factor=1.17))
    mt_processes["MC"] = Process("MC", SumUpEstimationMethod("MC", "nominal", era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK", "QCD", "HTT"]]))
    et = ETSM()
    et.cuts.remove("ele_iso")
    et.cuts.remove("tau_iso")
    et_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, et)),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, et)),
        "ggH"   : Process("ggH",      ggHEstimation   (era, directory, et)),
        "qqH"   : Process("qqH",      qqHEstimation   (era, directory, et)),
        "VH"    : Process("VH",       VHEstimation    (era, directory, et)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, et)),
        "ZL"    : Process("ZL",       ZLEstimationETSM(era, directory, et)),
        "ZJ"    : Process("ZJ",       ZJEstimationET  (era, directory, et)),
        "W"     : Process("W",        WEstimation     (era, directory, et)),
        "TTT"   : Process("TTT",      TTTEstimationET (era, directory, et)),
        "TTJ"   : Process("TTJ",      TTJEstimationET (era, directory, et)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, et)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, et))
        }
    et_processes["QCD"] = Process("QCD", QCDEstimationET(era, directory, et, [et_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK"]], et_processes["data"], extrapolation_factor=1.16))
    et_processes["MC"] = Process("MC", SumUpEstimationMethod("MC", "nominal", era, directory, et, [et_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK", "QCD", "HTT"]]))
    tt = TTSM()
    tt.cuts.remove("tau_1_iso")
    #tt.cuts.remove("tau_2_iso")
    tt_processes = {
        "data"  : Process("data_obs", DataEstimation (era, directory, tt)),
        "HTT"   : Process("HTT",      HTTEstimation  (era, directory, tt)),
        "ggH"   : Process("ggH",      ggHEstimation  (era, directory, tt)),
        "qqH"   : Process("qqH",      qqHEstimation  (era, directory, tt)),
        "VH"    : Process("VH",       VHEstimation   (era, directory, tt)),
        "ZTT"   : Process("ZTT",      ZTTEstimation  (era, directory, tt)),
        "ZL"    : Process("ZL",       ZLEstimationTT (era, directory, tt)),
        "ZJ"    : Process("ZJ",       ZJEstimationTT (era, directory, tt)),
        "W"     : Process("W",        WEstimation    (era, directory, tt)),
        "TTT"   : Process("TTT",      TTTEstimationTT(era, directory, tt)),
        "TTJ"   : Process("TTJ",      TTJEstimationTT(era, directory, tt)),
        "VV"    : Process("VV",       VVEstimation   (era, directory, tt)),
        "EWK"   : Process("EWK",      EWKEstimation  (era, directory, tt)),
        }
    tt_processes["QCD"] = Process("QCD", QCDEstimationTT(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK"]], tt_processes["data"]))
    tt_processes["MC"] = Process("MC", SumUpEstimationMethod("MC", "nominal", era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK", "QCD", "HTT"]]))

    # Variables and categories
    binning_lepton = [-0.1, -0.08, -0.06, -0.04, -0.02, -0.015, -0.01, -0.008, -0.006, -0.004, -0.003, -0.002, -0.001, 0.0, 0.001, 0.002, 0.003, 0.004, 0.006, 0.008, 0.01, 0.015, 0.02, 0.04, 0.06, 0.08, 0.1]
    binning_tau = [-0.1, -0.08, -0.06, -0.04, -0.02, -0.015, -0.01, -0.008, -0.006, -0.004, -0.002, 0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.015, 0.02, 0.04, 0.06, 0.08, 0.1]
    d0_1 = Variable("d0_1", VariableBinning(binning_lepton))
    #d0_1 = Variable("m_vis", VariableBinning([50.+x*5. for x in range(21)]))
    d0_2 = Variable("d0_2", VariableBinning(binning_tau))
    #d0_2 = Variable("m_vis", VariableBinning([50.+x*5. for x in range(21)]))
    dZ_1 = Variable("dZ_1", VariableBinning(binning_lepton))
    dZ_2 = Variable("dZ_2", VariableBinning(binning_tau))

    et_categories = []
    if "et" in args.channels:
        et_categories.append(
            Category(
                "d0_te",
                et,
                Cuts(
                    Cut("m_vis>60 && m_vis<75", "Zpeak"),
                    Cut("iso_1<0.1", "ele_iso"),
                    Cut("mt_2<100", "tau_mt"),
                    Cut("abs(eta_2)<1.0", "tau_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5 && byLooseIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_antiiso")),
                variable=d0_1))
        et_categories.append(
            Category(
                "dZ_te",
                et,
                Cuts(
                    Cut("m_vis>60 && m_vis<75", "Zpeak"),
                    Cut("iso_1<0.1", "ele_iso"),
                    Cut("mt_2<100", "tau_mt"),
                    Cut("abs(eta_2)<1.0", "tau_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5 && byLooseIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_antiiso")),
                variable=dZ_1))
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
                variable=dZ_2))
    mt_categories = []
    if "mt" in args.channels:
        mt_categories.append(
            Category(
                "d0_tm",
                mt,
                Cuts(
                    Cut("m_vis>55 && m_vis<75", "Zpeak"),
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("mt_2<100", "tau_mt"),
                    Cut("abs(eta_2)<1.0", "tau_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5 && byLooseIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_antiiso")),
                variable=d0_1))
        mt_categories.append(
            Category(
                "dZ_tm",
                mt,
                Cuts(
                    Cut("m_vis>55 && m_vis<75", "Zpeak"),
                    Cut("mt_1<50", "m_t"),
                    Cut("iso_1<0.15", "muon_iso"),
                    Cut("mt_2<100", "tau_mt"),
                    Cut("abs(eta_2)<1.0", "tau_eta"),
                    Cut("byTightIsolationMVArun2v1DBoldDMwLT_2<0.5 && byLooseIsolationMVArun2v1DBoldDMwLT_2>0.5", "tau_antiiso")),
                variable=dZ_1))
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
                variable=dZ_2))

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
