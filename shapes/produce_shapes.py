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
        default="/storage/jbod/wunsch/Run2Analysis_alex_classified",
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
        default=20,
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

    HTT = Process("HTT", HTTEstimation(era, directory, mt))
    ggH = Process("ggH", ggHEstimation(era, directory, mt))
    qqH = Process("qqH", qqHEstimation(era, directory, mt))
    VH = Process("VH", VHEstimation(era, directory, mt))

    ZTT = Process("ZTT", ZTTEstimation(era, directory, mt))
    ZL = Process("ZL", ZLEstimationMT(era, directory, mt))
    ZJ = Process("ZJ", ZJEstimationMT(era, directory, mt))
    W = Process("W", WEstimation(era, directory, mt))
    TTT = Process("TTT", TTTEstimationMT(era, directory, mt))
    TTJ = Process("TTJ", TTJEstimationMT(era, directory, mt))
    VV = Process("VV", VVEstimation(era, directory, mt))
    QCD = Process("QCD",
                  QCDEstimation(era, directory, mt,
                                [ZTT, ZJ, ZL, W, TTT, TTJ, VV], data))
    # Variables and categories
    probability = Variable("mt_keras4_max_score", ConstantBinning(6, 0.2, 1.0))
    mt_cut = Cut("mt_1<50", "mt")
    mt_HTT = Category(
        "HTT",
        MT(),
        Cuts(mt_cut, Cut("mt_keras4_max_index==0", "exclusive_probability")),
        variable=probability)
    mt_ZTT = Category(
        "ZTT",
        MT(),
        Cuts(mt_cut, Cut("mt_keras4_max_index==1", "exclusive_probability")),
        variable=probability)
    mt_ZLL = Category(
        "ZLL",
        MT(),
        Cuts(mt_cut, Cut("mt_keras4_max_index==2", "exclusive_probability")),
        variable=probability)
    mt_W = Category(
        "W",
        MT(),
        Cuts(mt_cut, Cut("mt_keras4_max_index==3", "exclusive_probability")),
        variable=probability)
    mt_TT = Category(
        "TT",
        MT(),
        Cuts(mt_cut, Cut("mt_keras4_max_index==4", "exclusive_probability")),
        variable=probability)
    mt_QCD = Category(
        "QCD",
        MT(),
        Cuts(mt_cut, Cut("mt_keras4_max_index==5", "exclusive_probability")),
        variable=probability)

    # Nominal histograms
    systematics = Systematics("shapes.root", num_threads=args.num_threads)
    for category in [mt_HTT, mt_ZTT, mt_ZLL, mt_W, mt_TT, mt_QCD]:
        for process in [
                data, HTT, VH, ggH, qqH, ZTT, ZL, ZJ, W, TTT, TTJ, VV, QCD
        ]:
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))

    # Shapes variations

    # Tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_t_3prong0pi0", "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_t_1prong0pi0", "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_t_1prong1pi0", "tauEsOneProngPiZeros", DifferentPipeline)
    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process in [HTT, VH, ggH, qqH, ZTT]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)

    # Jet energy scale
    jet_es_variations = create_systematic_variations("CMS_scale_j", "jecUnc",
                                                     DifferentPipeline)
    for variation in jet_es_variations:
        for process in [HTT, VH, ggH, qqH, ZTT, ZL, ZJ, W, TTT, TTJ, VV]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)

    # MET energy scale
    met_es_variations = create_systematic_variations(
        "CMS_htt_scale_met", "metUnclusteredEn", DifferentPipeline)
    for variation in met_es_variations:
        for process in [HTT, VH, ggH, qqH, ZTT, ZL, ZJ, W, TTT, TTJ, VV]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)

    # Z pt reweighting
    zpt_variations = create_systematic_variations(
        "CMS_htt_dyShape", "zPtReweightWeight", SquareAndRemoveWeight)
    for variation in zpt_variations:
        for process in [ZTT, ZL, ZJ]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)

    # top pt reweighting
    top_pt_variations = create_systematic_variations(
        "CMS_htt_ttbarShape", "topPtReweightWeight", SquareAndRemoveWeight)
    for variation in top_pt_variations:
        for process in [TTT, TTJ]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)

    # TODO: Example for replacing weights
    """
    # Zll reweighting
    zll_weight_variations = []
    zll_weight_variations.append(
        ReplaceWeight(
            "CMS_some_zll_systematic", "decay_mode_reweight",
            Weight(
                "(((decayMode_2 == 0)*1.0) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.0) + ((decayMode_2 == 10)*1.03))",
                "decay_mode_reweight"), "Up"))
    zll_weight_variations.append(
        ReplaceWeight(
            "CMS_some_zll_systematic", "decay_mode_reweight",
            Weight(
                "(((decayMode_2 == 0)*1.0) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.0) + ((decayMode_2 == 10)*0.97))",
                "decay_mode_reweight"), "Down"))
    for variation in zll_weight_variations:
        for process in [zll]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)
    """

    # Produce histograms
    systematics.produce()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_shapes.log", logging.DEBUG)
    main(args)
