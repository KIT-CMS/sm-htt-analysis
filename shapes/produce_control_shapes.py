#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    parser.add_argument(
        "--emb",
        action="store_true",
        default=False,
        help="Use mu->tau embedded samples as ZTT background estimation.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    systematics_mt = Systematics("shapes_mt.root", num_threads=args.num_threads)
    systematics_et = Systematics("shapes_et.root", num_threads=args.num_threads)
    systematics_tt = Systematics("shapes_tt.root", num_threads=args.num_threads)
    systematics_em = Systematics("shapes_em.root", num_threads=args.num_threads)

    # Era
    era = Run2017ReReco31Mar(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory

    mt = MT()
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, mt)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, mt)),
        "ZLL"   : Process("ZLL",      ZLLEstimation   (era, directory, mt)),
    #    "W"     : Process("W",        WEstimation     (era, directory, mt)),
        "TT"    : Process("TT",       TTEstimation    (era, directory, mt)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, mt)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, mt))
        }
    wjets_mc_mt = Process("WMC",        WEstimation     (era, directory, mt))
    #mt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], mt_processes["data"], extrapolation_factor=1.1))
    mt_processes["W"] = Process("W", WEstimationWithQCD(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZLL", "TT", "VV", "EWK"]], mt_processes["data"], wjets_mc_mt, qcd_ss_to_os_extrapolation_factor=1.1))
    mt_processes["QCD"] = Process("QCD", QCDEstimationWithW(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZLL", "TT", "VV", "EWK"]], mt_processes["data"], wjets_mc_mt, qcd_ss_to_os_extrapolation_factor=1.1))

    em = EM()
    em_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, em)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, em)),
        "ZLL"   : Process("ZLL",      ZLLEstimation   (era, directory, em)),
        "W"     : Process("W",        WEstimation     (era, directory, em)),
        "TT"    : Process("TT",       TTEstimation    (era, directory, em)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, em)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, em))
        }
    em_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, em, [em_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], em_processes["data"], extrapolation_factor=1.0))

    et = ET()
    et_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, et)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, et)),
        "ZLL"   : Process("ZLL",      ZLLEstimation   (era, directory, et)),
    #    "W"     : Process("W",        WEstimation     (era, directory, et)),
        "TT"    : Process("TT",       TTEstimation    (era, directory, et)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, et)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, et))
        }
    wjets_mc_et = Process("WMC",        WEstimation     (era, directory, et))
    #et_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, et, [et_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], et_processes["data"], extrapolation_factor=1.09))
    et_processes["W"] = Process("W", WEstimationWithQCD(era, directory, et, [et_processes[process] for process in ["ZTT", "ZLL", "TT", "VV", "EWK"]], et_processes["data"], wjets_mc_et, qcd_ss_to_os_extrapolation_factor=1.09))
    et_processes["QCD"] = Process("QCD", QCDEstimationWithW(era, directory, et, [et_processes[process] for process in ["ZTT", "ZLL", "TT", "VV", "EWK"]], et_processes["data"], wjets_mc_et, qcd_ss_to_os_extrapolation_factor=1.09))

    tt = TT()
    tt_processes = {
        "data"  : Process("data_obs", DataEstimation (era, directory, tt)),
        "ZTT"   : Process("ZTT",      ZTTEstimation  (era, directory, tt)),
        "ZLL"   : Process("ZLL",      ZLLEstimation  (era, directory, tt)),
        "W"     : Process("W",        WEstimation    (era, directory, tt)),
        "TT"    : Process("TT",       TTEstimation   (era, directory, tt)),
        "VV"    : Process("VV",       VVEstimation   (era, directory, tt)),
        "EWK"   : Process("EWK",      EWKEstimation  (era, directory, tt)),
        }
    tt_processes["QCD"] = Process("QCD", QCDEstimation_ABCD_TT_ISO2(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], tt_processes["data"]))
    #tt_processes["QCD"] = Process("QCD", QCDEstimation_ABCD_TT_ISO2_TRANSPOSED(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], tt_processes["data"]))
    #tt_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZLL", "W", "TT", "VV", "EWK"]], tt_processes["data"], extrapolation_factor=1.0))

    # Variables and categories
    binning = yaml.load(open(args.binning))

    mt_categories = []
    et_categories = []
    tt_categories = []
    em_categories = []

    variable_names = ["mt_1","mt_2", "pt_1","pt_2", "eta_1", "eta_2", "m_vis", "ptvis", "npv", "njets", "nbtag", "jpt_1", "jpt_2", "jeta_1", "jeta_2", "met", "mjj", "dijetpt", "pZetaMissVis", "m_1", "m_2", "decayMode_1", "decayMode_2", "iso_1", "iso_2", "rho"]

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
           if name == "iso_1" or name == "iso_2":
               tt_categories[-1].cuts.remove("tau_1_iso")
               tt_categories[-1].cuts.remove("tau_2_iso")

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
    if ('tt' in args.channels or 'em' in args.channels) and args.emb:
        print "Channels tt and em not yet considered for embedded background estimation."
        exit()
    setup_logging("produce_shapes.log", logging.DEBUG)
    main(args)
