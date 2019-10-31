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
        description="Produce shapes for 2017 Standard Model analysis.")

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
        "--num-threads",
        default=20,
        type=int,
        help="Number of threads to be used.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    systematics_mm = Systematics("shapes_mm_recoil_2017.root", num_threads=args.num_threads, find_unique_objects=True)

    # Era
    era = Run2017(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory

    mm = MM()
    mm_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, mm, friend_directory=[])),
        "ZTT"   : Process("ZTT",      ZTTEstimation       (era, directory, mm, friend_directory=[])),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, mm, friend_directory=[])),
        "TTT"   : Process("TTT",      TTTEstimation       (era, directory, mm, friend_directory=[])),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, mm, friend_directory=[])),
        "VVT"   : Process("VVT",      VVTEstimation       (era, directory, mm, friend_directory=[])),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, mm, friend_directory=[])),
        "W"     : Process("W",        WEstimation         (era, directory, mm, friend_directory=[])),
        }
    mm_processes["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, mm,
            [mm_processes[process] for process in ["ZTT", "ZL", "W", "TTT", "TTL", "VVT", "VVL"]],
            mm_processes["data"], friend_directory=[], extrapolation_factor=2.0))

    # Variables and categories
    binning = yaml.load(open(args.binning))
    mm_categories = []

    variable_bins = {
        "njets" : [0, 1, 2],
        "ptvis" : [0, 10, 20, 30, 50],
    }
    variable_names = [
        "metParToZ", "metPerpToZ",
        "puppimetParToZ", "puppimetPerpToZ",
#        "recoilParToZ", "recoilPerpToZ",
#        "puppirecoilParToZ", "puppirecoilPerpToZ",
    ]

    for njets_bin in range(len(variable_bins["njets"])):
        for pt_bin in range(len(variable_bins["ptvis"])):
            name = "njets_bin_%s_vs_ptvis_bin_%s"%(str(njets_bin),str(pt_bin))
            category_njets = ""
            category_pt = ""
            if njets_bin == (len(variable_bins["njets"]) - 1):
                category_njets = "njets >= %s"%str(variable_bins["njets"][njets_bin])
            else:
                category_njets = "njets == %s"%str(variable_bins["njets"][njets_bin])
            if pt_bin == (len(variable_bins["ptvis"]) - 1):
                category_pt = "ptvis > %s"%str(variable_bins["ptvis"][pt_bin])
            else:
                category_pt= "ptvis > %s && ptvis <= %s"%(str(variable_bins["ptvis"][pt_bin]),str(variable_bins["ptvis"][pt_bin+1]))
            print category_njets, category_pt
            cuts = Cuts(
                Cut(category_njets,"njets_category"),
                Cut(category_pt,"ptvis_category"),
                Cut("m_vis > 70 && m_vis < 110","z_peak")
            )
            for v in variable_names:
                mm_categories.append(
                    Category(
                        name,
                        mm,
                        cuts,
                        variable=Variable(v,VariableBinning(binning["control"]["mm"][v]["bins"]), expression=binning["control"]["mm"][v]["expression"])))

    # Nominal histograms
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
    systematics_mm.produce()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_shapes_recoil_2017.log", logging.INFO)
    main(args)
