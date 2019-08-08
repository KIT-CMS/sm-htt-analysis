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
from shape_producer.estimation_methods_2016 import *
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.era import Run2016
from shape_producer.channel import MMSM2016 as MM

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
        "--num-threads",
        default=20,
        type=int,
        help="Number of threads to be used.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    systematics_mm = Systematics("shapes_mm_recoilunc_2016.root", num_threads=args.num_threads, find_unique_objects=True)

    # Era
    era = Run2016(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory

    mm = MM()
    mm_processes = {
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, mm, friend_directory=[])),
        }

    # Variables and categories
    binning = yaml.load(open(args.binning))
    mm_categories = []

    variable_bins = {
        "njets" : [0, 1, 2],
        "genbosonpt" : [0, 10, 20, 30, 50],
    }
    variable_names = [
        "recoilParToZ",
        "puppirecoilParToZ",
    ]

    for njets_bin in range(len(variable_bins["njets"])):
        for pt_bin in range(len(variable_bins["genbosonpt"])):
            name = "njets_bin_%s_vs_ptvis_bin_%s"%(str(njets_bin),str(pt_bin))
            category_njets = ""
            category_pt = ""
            if njets_bin == (len(variable_bins["njets"]) - 1):
                category_njets = "njets >= %s"%str(variable_bins["njets"][njets_bin])
            else:
                category_njets = "njets == %s"%str(variable_bins["njets"][njets_bin])
            if pt_bin == (len(variable_bins["genbosonpt"]) - 1):
                category_pt = "genbosonpt > %s"%str(variable_bins["genbosonpt"][pt_bin])
            else:
                category_pt= "genbosonpt > %s && genbosonpt <= %s"%(str(variable_bins["genbosonpt"][pt_bin]),str(variable_bins["genbosonpt"][pt_bin+1]))
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
                        variable=Variable("relative_%s"%v,ConstantBinning(400,-20.0,20.0), expression="-%s/genbosonpt"%v)))

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
    setup_logging("produce_shapes_recoilunc_2016.log", logging.INFO)
    main(args)
