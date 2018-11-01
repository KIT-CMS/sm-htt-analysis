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
from shape_producer.channel import ET_ETOTAUFAKE2017 as ET

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
    systematics_et = Systematics("shapes_et.root", num_threads=args.num_threads, find_unique_objects=True)

    # Era
    era = Run2017ReReco31Mar(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory

    et = ET()
    et_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, et, friend_directory=[])),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, et, friend_directory=[])),
        "ZL"    : Process("ZL",     ZLEstimation (era, directory, et, friend_directory=[])),
        "ZJ"    : Process("ZJ",       ZJEstimation  (era, directory, et, friend_directory=[])),
        "TT"    : Process("TT",       TTEstimation    (era, directory, et, friend_directory=[])),
        "VV"   : Process("VV",      VVEstimation (era, directory, et, friend_directory=[])),
        }
    wjets_mc_et = Process("WMC",        WEstimation     (era, directory, et, friend_directory=[]))
    et_processes["W"] = Process("W", WEstimationWithQCD(era, directory, et, [et_processes[process] for process in ["ZTT", "ZL", "ZJ", "TT", "VV"]], et_processes["data"], wjets_mc_et, friend_directory=[], qcd_ss_to_os_extrapolation_factor=1.09))
    et_processes["QCD"] = Process("QCD", QCDEstimationWithW(era, directory, et, [et_processes[process] for process in ["ZTT", "ZL", "ZJ", "TT", "VV"]], et_processes["data"], wjets_mc_et, friend_directory=[], qcd_ss_to_os_extrapolation_factor=1.09))

    # Variables and categories
    binning = yaml.load(open(args.binning))

    et_categories = []

    #variable_names = ["mt_1","mt_2", "pt_1","pt_2", "eta_1", "eta_2", "m_vis", "ptvis", "npv", "njets", "nbtag", "jpt_1", "jpt_2", "jeta_1", "jeta_2", "met", "mjj", "dijetpt", "pZetaMissVis", "m_1", "m_2", "decayMode_1", "decayMode_2", "iso_1", "iso_2", "rho", "mt_tot", "d0_1", "d0_2", "dZ_1", "dZ_2"]
    variable_names = ["m_vis", "pt_1", "pt_2", "eta_1", "eta_2", "decayMode_2", "met", "mt_1", "m_2", "iso_1", "iso_2"]
    #variable_names = ["m_vis"]

    if "et" in args.channels:
        variables = [Variable(v,VariableBinning(binning["control"]["et"][v]["bins"]), expression=binning["control"]["et"][v]["expression"]) for v in variable_names]
        for name, var in zip(variable_names, variables):
            for catcut in [("decayMode_2 == 0", "dm0"), ("decayMode_2 == 1", "dm1"), ("decayMode_2 == 10", "dm10")]:
                cuts = Cuts(Cut(catcut[0], catcut[1]))
                et_categories.append(
                    Category(
                        name+catcut[1],
                        et,
                        cuts,
                        variable=var))

    # Nominal histograms
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

    # Produce histograms
    if "et" in args.channels: systematics_et.produce()

if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_shapes.log", logging.DEBUG)
    main(args)
