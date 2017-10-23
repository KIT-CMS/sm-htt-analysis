#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shape_producer.cutstring import Cut, Cuts
from shape_producer.systematics import Systematics, Systematic
from shape_producer.categories import Category
from shape_producer.binning import ConstantBinning
from shape_producer.variable import Variable
from shape_producer.systematic_variations import Nominal, DifferentPipeline, SquareAndRemoveWeight, create_systematic_variations
from shape_producer.process import Process
from shape_producer.estimation_methods_2016 import *
from shape_producer.era import Run2016
from shape_producer.channel import MT

import argparse

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
        default="/storage/jbod/wunsch/Run2Analysis_alex",
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--datasets",
        default=
        "/portal/ekpbms3/home/wunsch/CMSSW_7_4_7/src/Kappa/Skimming/data/datasets.json",
        type=str,
        help="Kappa datsets database.")
    parser.add_argument(
        "--num-threads",
        default=8,
        type=int,
        help="Number of threads to be used.")

    return parser.parse_args()


def main(args):
    # Era
    era = Run2016(args.datasets)

    # Channels and processes
    mt = MT()
    directory = args.directory
    data = Process("data_obs", DataEstimation(era, directory, mt))
    htt = Process("Htt", HttEstimation(era, directory, mt))
    ztt = Process("Ztt", ZttEstimation(era, directory, mt))
    zll = Process("Zll", ZllEstimation(era, directory, mt))
    wjets = Process("WJets", WJetsEstimation(era, directory, mt))
    tt = Process("tt", TTEstimation(era, directory, mt))
    vv = Process("VV", VVEstimation(era, directory, mt))
    qcd = Process("QCD",
                  QCDEstimation(era, directory, mt, [ztt, zll, wjets, tt, vv],
                                data))

    # Variables and categories
    pt_1 = Variable("pt_1", ConstantBinning(12, 20, 100))
    inclusive = Category(
        "inclusive", MT(), Cuts(Cut("mt_1<50", "mt")), variable=pt_1)

    # Nominal histograms
    systematics = Systematics("shapes.root", num_threads=args.num_threads)
    for process in [data, htt, ztt, zll, wjets, tt, vv, qcd]:
        systematics.add(
            Systematic(
                category=inclusive,
                process=process,
                analysis="smhtt",
                era=era,
                variation=Nominal(),
                mass="125"))

    # Shape variations
    tau_es_3prong_variations = create_systematic_variations(
        "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "tauEsOneProngPiZeros", DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process in [htt, ztt]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)

    zpt_variations = create_systematic_variations("zPtReweightWeight",
                                                  SquareAndRemoveWeight)
    for variation in zpt_variations:
        for process in [ztt, zll]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)


    inclusive_pt_2 = Category("inclusive", MT(), Cuts(Cut("mt_1<50", "mt")), variable=Variable("pt_2", ConstantBinning(12, 20, 100)))
    inclusive_mt_1 = Category("inclusive", MT(), Cuts(), variable=Variable("mt_1", ConstantBinning(12, 0, 120)))

    systematics.add_extra_category(inclusive_pt_2, inclusive)
    systematics.add_extra_category(inclusive_mt_1, inclusive)

    # Produce histograms
    systematics.produce()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_shapes.log", logging.DEBUG)
    main(args)
