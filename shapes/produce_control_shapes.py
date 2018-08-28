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
from shape_producer.estimation_methods_Fall17 import *
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.era import Run2017ReReco31Mar
from shape_producer.channel import MTMSSM2017 as MT
from shape_producer.channel import ETMSSM2017 as ET
from shape_producer.channel import TTMSSM2017 as TT
from shape_producer.channel import EMMSSM2017 as EM

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
        "--fake-factor-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing friend trees to data files with fake factors."
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
    systematics_mt = Systematics("shapes_mt.root", num_threads=args.num_threads, find_unique_objects=True)
    systematics_et = Systematics("shapes_et.root", num_threads=args.num_threads, find_unique_objects=True)
    systematics_tt = Systematics("shapes_tt.root", num_threads=args.num_threads, find_unique_objects=True)
    systematics_em = Systematics("shapes_em.root", num_threads=args.num_threads, find_unique_objects=True)

    # Era
    era = Run2017ReReco31Mar(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory
    susy_masses = ["250", "300", "700", "2300"]
    ff_friend_directory = args.fake_factor_friend_directory

    mt = MT()
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, mt, friend_directory=[])),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, mt, friend_directory=[])),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation   (era, directory, mt, friend_directory=[])),
        "ZLL"   : Process("ZLL",      ZLLEstimation   (era, directory, mt, friend_directory=[])),
    #    "W"     : Process("W",        WEstimation     (era, directory, mt, friend_directory=[])),
        "TT"    : Process("TT",       TTEstimation    (era, directory, mt, friend_directory=[])),
        "TTL"    : Process("TTL",       TTLEstimation    (era, directory, mt, friend_directory=[])),
        "VV"    : Process("VV",       VVEstimation    (era, directory, mt, friend_directory=[])),
        "VVL"    : Process("VVL",       VVLEstimation    (era, directory, mt, friend_directory=[])),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, mt, friend_directory=[])),
        "FAKES" : Process("jetFakes",    FakeEstimationLT(era, directory, mt, friend_directory=[ff_friend_directory])),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, mt, friend_directory=[])),
        }
    wjets_mc_mt = Process("WMC",        WEstimation     (era, directory, mt, friend_directory=[]))
    #mt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], mt_processes["data"], friend_directory=[], extrapolation_factor=1.1))
    mt_processes["W"] = Process("W", WEstimationWithQCD(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZLL", "TT", "VV", "EWK"]], mt_processes["data"], wjets_mc_mt, friend_directory=[], qcd_ss_to_os_extrapolation_factor=1.1))
    mt_processes["QCD"] = Process("QCD", QCDEstimationWithW(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZLL", "TT", "VV", "EWK"]], mt_processes["data"], wjets_mc_mt, friend_directory=[], qcd_ss_to_os_extrapolation_factor=1.1))
    for m in susy_masses:
        mt_processes["ggH_"+m] = Process("ggH_"+m, SUSYggHEstimation(era, directory, mt, m, friend_directory=[]))
        mt_processes["bbH_"+m] = Process("bbH_"+m, SUSYbbHEstimation(era, directory, mt, m, friend_directory=[]))

    em = EM()
    em_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, em, friend_directory=[])),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, em, friend_directory=[])),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation   (era, directory, em, friend_directory=[])),
        "ZLL"   : Process("ZLL",      ZLLEstimation   (era, directory, em, friend_directory=[])),
        "W"     : Process("W",        WEstimation     (era, directory, em, friend_directory=[])),
        "TT"    : Process("TT",       TTEstimation    (era, directory, em, friend_directory=[])),
        "TTL"    : Process("TTL",       TTLEstimation    (era, directory, em, friend_directory=[])),
        "VV"    : Process("VV",       VVEstimation    (era, directory, em, friend_directory=[])),
        "VVL"    : Process("VVL",       VVLEstimation    (era, directory, em, friend_directory=[])),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, em, friend_directory=[])),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, em, friend_directory=[])),
        }
    em_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, em, [em_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], em_processes["data"], friend_directory=[], extrapolation_factor=1.0))
    for m in susy_masses:
        em_processes["ggH_"+m] = Process("ggH_"+m, SUSYggHEstimation(era, directory, em, m, friend_directory=[]))
        em_processes["bbH_"+m] = Process("bbH_"+m, SUSYbbHEstimation(era, directory, em, m, friend_directory=[]))

    et = ET()
    et_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, et, friend_directory=[])),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, et, friend_directory=[])),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation   (era, directory, et, friend_directory=[])),
        "ZL"    : Process("ZL",       ZLEstimationLT(era, directory, et, friend_directory=[])),
        "ZJ"    : Process("ZJ",       ZJEstimationLT  (era, directory, et, friend_directory=[])),
    #    "W"     : Process("W",        WEstimation     (era, directory, et, friend_directory=[])),
        "TTT"   : Process("TTT",      TTTEstimationLT (era, directory, et, friend_directory=[])),
        "TTJ"   : Process("TTJ",      TTJEstimationLT (era, directory, et, friend_directory=[])),
        "VVT"   : Process("VVT",      VVTEstimationLT (era, directory, et, friend_directory=[])),
        "VVJ"   : Process("VVJ",      VVJEstimationLT (era, directory, et, friend_directory=[])),
        "TTL"    : Process("TTL",       TTLEstimation    (era, directory, et, friend_directory=[])),
        "VVL"    : Process("VVL",       VVLEstimation    (era, directory, et, friend_directory=[])),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, et, friend_directory=[])),
        "FAKES" : Process("jetFakes",    FakeEstimationLT(era, directory, et, friend_directory=[ff_friend_directory])),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, et, friend_directory=[])),
        }
    wjets_mc_et = Process("WMC",        WEstimation     (era, directory, et, friend_directory=[]))
    #et_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, et, [et_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], et_processes["data"], friend_directory=[], extrapolation_factor=1.09))
    et_processes["W"] = Process("W", WEstimationWithQCD(era, directory, et, [et_processes[process] for process in ["ZTT", "ZL", "ZJ", "TTT", "TTJ", "VVT", "VVJ", "EWK"]], et_processes["data"], wjets_mc_et, friend_directory=[], qcd_ss_to_os_extrapolation_factor=1.09))
    et_processes["QCD"] = Process("QCD", QCDEstimationWithW(era, directory, et, [et_processes[process] for process in ["ZTT", "ZL", "ZJ", "TTT", "TTJ", "VVT", "VVJ", "EWK"]], et_processes["data"], wjets_mc_et, friend_directory=[], qcd_ss_to_os_extrapolation_factor=1.09))
    for m in susy_masses:
        et_processes["ggH_"+m] = Process("ggH_"+m, SUSYggHEstimation(era, directory, et, m, friend_directory=[]))
        et_processes["bbH_"+m] = Process("bbH_"+m, SUSYbbHEstimation(era, directory, et, m, friend_directory=[]))

    tt = TT()
    tt_processes = {
        "data"  : Process("data_obs", DataEstimation (era, directory, tt, friend_directory=[])),
        "ZTT"   : Process("ZTT",      ZTTEstimation  (era, directory, tt, friend_directory=[])),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation   (era, directory, tt, friend_directory=[])),
        "ZL"    : Process("ZL",       ZLEstimationTT (era, directory, tt, friend_directory=[])),
        "ZJ"    : Process("ZJ",       ZJEstimationTT (era, directory, tt, friend_directory=[])),
        "W"     : Process("W",        WEstimation    (era, directory, tt, friend_directory=[])),
        "TTT"   : Process("TTT",      TTTEstimationTT(era, directory, tt, friend_directory=[])),
        "TTJ"   : Process("TTJ",      TTJEstimationTT(era, directory, tt, friend_directory=[])),
        "TTL"    : Process("TTL",       TTLEstimation    (era, directory, tt, friend_directory=[])),
        "VVT"   : Process("VVT",      VVTEstimationTT(era, directory, tt, friend_directory=[])),
        "VVJ"   : Process("VVJ",      VVJEstimationTT(era, directory, tt, friend_directory=[])),
        "VVL"    : Process("VVL",       VVLEstimation    (era, directory, tt, friend_directory=[])),
        "EWK"   : Process("EWK",      EWKEstimation  (era, directory, tt, friend_directory=[])),
        "FAKES" : Process("jetFakes",    FakeEstimationTT(era, directory, tt, friend_directory=[ff_friend_directory])),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, tt, friend_directory=[]))
        }
    tt_processes["QCD"] = Process("QCD", QCDEstimation_ABCD_TT_ISO2(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZL", "ZJ", "TTT", "TTJ", "VVT", "VVJ", "EWK"]], tt_processes["data"], friend_directory=[]))
    #tt_processes["QCD"] = Process("QCD", QCDEstimation_ABCD_TT_ISO2_TRANSPOSED(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], tt_processes["data"], friend_directory=[]))
    #tt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], tt_processes["data"], friend_directory=[], extrapolation_factor=1.0))
    for m in susy_masses:
        tt_processes["ggH_"+m] = Process("ggH_"+m, SUSYggHEstimation(era, directory, tt, m, friend_directory=[]))
        tt_processes["bbH_"+m] = Process("bbH_"+m, SUSYbbHEstimation(era, directory, tt, m, friend_directory=[]))

    # Variables and categories
    binning = yaml.load(open(args.binning))

    mt_categories = []
    et_categories = []
    tt_categories = []
    em_categories = []

    variable_names = ["mt_1","mt_2", "pt_1","pt_2", "eta_1", "eta_2", "m_vis", "ptvis", "npv", "njets", "nbtag", "jpt_1", "jpt_2", "jeta_1", "jeta_2", "met", "mjj", "dijetpt", "pZetaMissVis", "m_1", "m_2", "decayMode_1", "decayMode_2", "iso_1", "iso_2", "rho", "mt_tot", "d0_1", "d0_2", "dZ_1", "dZ_2"]
    if "mt" in args.channels:
        variables = [Variable(v,VariableBinning(binning["control"]["mt"][v]["bins"]), expression=binning["control"]["mt"][v]["expression"]) for v in variable_names]
        for name, var in zip(variable_names, variables):
            if name == "mt_1":
                cuts = Cuts()
            else:
                cuts=Cuts(Cut("mt_1 < 70","mt"))
            mt_categories.append(
                Category(
                    name,
                    mt,
                    cuts,
                    variable=var))
            if name == "iso_1" or name == "iso_2":
                mt_categories[-1].cuts.remove("muon_iso")
                mt_categories[-1].cuts.remove("tau_iso")

    if "et" in args.channels:
        variables = [Variable(v,VariableBinning(binning["control"]["et"][v]["bins"]), expression=binning["control"]["et"][v]["expression"]) for v in variable_names]
        for name, var in zip(variable_names, variables):
            if name == "mt_1":
                cuts = Cuts()
            else:
                cuts=Cuts(Cut("mt_1 < 70","mt"))
            et_categories.append(
                Category(
                    name,
                    et,
                    cuts,
                    variable=var))
            if name == "iso_1" or name == "iso_2":
                et_categories[-1].cuts.remove("ele_iso")
                et_categories[-1].cuts.remove("tau_iso")

    if "tt" in args.channels:
       variables = [Variable(v,VariableBinning(binning["control"]["tt"][v]["bins"]), expression=binning["control"]["tt"][v]["expression"]) for v in variable_names]
       cuts=Cuts()
       for name, var in zip(variable_names, variables):
           tt_categories.append(
               Category(
                   name,
                   tt,
                   cuts,
                   variable=var))

    if "em" in args.channels:
        variables = [Variable(v,VariableBinning(binning["control"]["em"][v]["bins"]), expression=binning["control"]["em"][v]["expression"]) for v in variable_names]
        cuts=Cuts(Cut("pZetaMissVis > -50","dzeta_cut"))
        for name, var in zip(variable_names, variables):
            if name == "pZetaMissVis":
                cuts = Cuts()
            else:
                cuts=Cuts(Cut("pZetaMissVis > -50","dzeta_cut"))
            em_categories.append(
                Category(
                    name,
                    em,
                    cuts,
                    variable=var))
            if name == "iso_1" or name == "iso_2":
                em_categories[-1].cuts.remove("ele_iso")
                em_categories[-1].cuts.remove("muon_iso")

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


    # Produce histograms
    if "mt" in args.channels: systematics_mt.produce()
    if "et" in args.channels: systematics_et.produce()
    if "tt" in args.channels: systematics_tt.produce()
    if "em" in args.channels: systematics_em.produce()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_shapes.log", logging.DEBUG)
    main(args)
