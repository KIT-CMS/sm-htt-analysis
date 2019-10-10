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
    parser.add_argument(
        "--no-dy-reweighting",
        default=False,
        action='store_true',
        help="Remove dy reweighting in the shape production.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    systematics_mt = Systematics("countshww_mt_2017.root", num_threads=args.num_threads, find_unique_objects=True)
    systematics_et = Systematics("countshww_et_2017.root", num_threads=args.num_threads, find_unique_objects=True)
    systematics_em = Systematics("countshww_em_2017.root", num_threads=args.num_threads, find_unique_objects=True)

    # Era
    era = Run2017(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory
    et_friend_directory = args.et_friend_directory
    mt_friend_directory = args.mt_friend_directory
    em_friend_directory = args.em_friend_directory

    ff_friend_directory = args.fake_factor_friend_directory

    mt = MT()
    mt_processes = {
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, mt, friend_directory=mt_friend_directory)),
        "HWW"   : Process("HWW",      HWWEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        }

    et = ET()
    et_processes = {
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, et, friend_directory=et_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, et, friend_directory=et_friend_directory)),
        "HWW"   : Process("HWW",      HWWEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        }

    em = EM()
    em_processes = {
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, em, friend_directory=em_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, em, friend_directory=em_friend_directory)),
        "HWW"   : Process("HWW",      HWWEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        }
    # Variables and categories
    binning = yaml.load(open(args.binning))
    cuts = {
        "mt" : [
            Cut("1 > 0", "inclusive"),
            Cut("m_vis >= 50 || DiTauDeltaR >= 1.2","htautau_new"),
            Cut("mt_1 < 60","htautau_old"),
            Cut("m_vis < 50 && DiTauDeltaR < 1.2","hww_new"),
            Cut("mt_1 >= 60","hww_old"),
        ],
        "et" : [
            Cut("1 > 0", "inclusive"),
            Cut("m_vis >= 50 || DiTauDeltaR >= 1.2","htautau_new"),
            Cut("mt_1 < 60","htautau_old"),
            Cut("m_vis < 50 && DiTauDeltaR < 1.2","hww_new"),
            Cut("mt_1 >= 60","hww_old"),
        ],
        "em" : [
            Cut("1 > 0", "inclusive"),
            Cut("mTdileptonMET_puppi < 60","htautau_new"),
            Cut("mTdileptonMET < 60","htautau_old"),
            Cut("mTdileptonMET_puppi >= 60","hww_new"),
            Cut("mTdileptonMET >= 60","hww_old"),
        ],
    }

    mt_categories = []
    et_categories = []
    em_categories = []


    if "mt" in args.channels:
        for cut in cuts["mt"]:
            mt_categories.append(
                Category(
                    cut.name,
                    mt,
                    Cuts(cut),
                    variable=None))

    if "et" in args.channels:
        for cut in cuts["et"]:
            et_categories.append(
                Category(
                    cut.name,
                    et,
                    Cuts(cut),
                    variable=None))

    if "em" in args.channels:
        for cut in cuts["em"]:
            em_categories.append(
                Category(
                    cut.name,
                    em,
                    Cuts(cut),
                    variable=None))


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
    if "em" in args.channels: systematics_em.produce()

if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_hww_counts.log", logging.INFO)
    main(args)
