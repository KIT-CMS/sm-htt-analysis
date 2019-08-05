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
from shape_producer.estimation_methods_2018 import *
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.era import Run2018
from shape_producer.channel import MMSM2018 as MM

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
        description="Produce shapes for 2018 Standard Model analysis.")

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
        "--datasets", required=True, type=str, help="Kappa datsets database.")
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
    systematics_mm = Systematics("fitrecoil_mm_2018.root", num_threads=args.num_threads, find_unique_objects=True)

    # Era
    era = Run2018(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory
    mm_friend_directory = args.mm_friend_directory

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
    mm_categories = []

    variable_names = [

        "met", "metphi",
        "puppimet", "puppimetphi", 

        "metParToZ", "metPerpToZ",
        "puppimetParToZ", "puppimetPerpToZ",
    ]

    variables = [Variable(v,ConstantBinning(50,-100.0,100.0)) for v in variable_names]

    cuts = [
        Cut("njets == 0", "0jet"),
        Cut("njets == 1", "1jet"),
        Cut("njets >= 2", "ge2jet"),
    ]
    for cut in cuts:
        for var in variables:
            mm_categories.append(
                Category(
                    cut.name,
                    mm,
                    Cuts(Cut("m_vis > 70 && m_vis < 110","m_vis_peak"), cut),
                    variable=var))

    for process, category in product(mm_processes.values(), mm_categories):
        systematics_mm.add(
            Systematic(
                category=category,
                process=process,
                analysis="smhtt",
                era=era,
                variation=Nominal(),
                mass="125"))

    # Recoil correction unc
    recoil_resolution_variations = create_systematic_variations(
        "CMS_htt_boson_reso_met_Run2018", "metRecoilResolution",
        DifferentPipeline)
    recoil_response_variations = create_systematic_variations(
        "CMS_htt_boson_scale_met_Run2018", "metRecoilResponse",
        DifferentPipeline)
    for variation in recoil_resolution_variations + recoil_response_variations:
        systematics_mm.add_systematic_variation(
            variation=variation,
            process=mm_processes["ZL"],
            channel=mm,
            era=era)

    # Produce histograms
    systematics_mm.produce()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_fitrecoil_2018.log", logging.INFO)
    main(args)
