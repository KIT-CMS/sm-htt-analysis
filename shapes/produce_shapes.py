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

    htt = Process("Htt", HttEstimation(era, directory, mt))
    ggh = Process("ggh", ggHEstimation(era, directory, mt))
    qqh = Process("qqh", qqHEstimation(era, directory, mt))
    #vh = Process("vh", VHEstimation(era, directory, mt)) # TODO: not yet evaluated by Keras

    ztt = Process("Ztt", ZttEstimation(era, directory, mt))
    zl = Process("Zl", ZlEstimationMT(era, directory, mt))
    zj = Process("Zj", ZjEstimationMT(era, directory, mt))
    wjets = Process("WJets", WJetsEstimation(era, directory, mt))
    ttt = Process("ttt", TTTEstimationMT(era, directory, mt))
    ttj = Process("ttj", TTJEstimationMT(era, directory, mt))
    vv = Process("VV", VVEstimation(era, directory, mt))
    qcd = Process("QCD",
                  QCDEstimation(era, directory, mt, [ztt, zj, zl, wjets, ttt, ttj, vv],
                                data))
    # Variables and categories
    probability = Variable("mt_keras3_max_score", ConstantBinning(8, 0.2, 1.0))
    mt_cut = Cut("mt_1<50", "mt")
    mt_htt = Category(
        "Htt",
        MT(),
        Cuts(mt_cut, Cut("mt_keras3_max_index==0", "exclusive_probability")),
        variable=probability)
    mt_ztt = Category(
        "Ztt",
        MT(),
        Cuts(mt_cut, Cut("mt_keras3_max_index==1", "exclusive_probability")),
        variable=probability)
    mt_zll = Category(
        "Zll",
        MT(),
        Cuts(mt_cut, Cut("mt_keras3_max_index==2", "exclusive_probability")),
        variable=probability)
    mt_wjets = Category(
        "WJets",
        MT(),
        Cuts(mt_cut, Cut("mt_keras3_max_index==3", "exclusive_probability")),
        variable=probability)
    mt_tt = Category(
        "tt",
        MT(),
        Cuts(mt_cut, Cut("mt_keras3_max_index==4", "exclusive_probability")),
        variable=probability)
    mt_qcd = Category(
        "QCD",
        MT(),
        Cuts(mt_cut, Cut("mt_keras3_max_index==5", "exclusive_probability")),
        variable=probability)

    # Nominal histograms
    systematics = Systematics("shapes.root", num_threads=args.num_threads)
    for category in [mt_htt, mt_ztt, mt_zll, mt_wjets, mt_tt, mt_qcd]:
        for process in [data, htt, ggh, qqh, ztt, zl, zj, wjets, ttt, ttj, vv, qcd]:
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
        for process in [htt, ggh, qqh, ztt]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)

    # Jet energy scale
    jet_es_variations = create_systematic_variations("CMS_scale_j", "jecUnc",
                                                     DifferentPipeline)
    for variation in jet_es_variations:
        for process in [htt, ggh, qqh, ztt, zl, zj, wjets, ttt, ttj, vv]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)

    # MET energy scale
    met_es_variations = create_systematic_variations(
        "CMS_htt_scale_met", "metUnclusteredEn", DifferentPipeline)
    for variation in met_es_variations:
        for process in [htt, ggh, qqh, ztt, zl, zj, wjets, ttt, ttj, vv]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)

    # Z pt reweighting
    zpt_variations = create_systematic_variations(
        "CMS_htt_dyShape", "zPtReweightWeight", SquareAndRemoveWeight)
    for variation in zpt_variations:
        for process in [ztt, zl, zj]:
            systematics.add_systematic_variation(
                variation=variation, process=process, channel=mt, era=era)

    # top pt reweighting
    top_pt_variations = create_systematic_variations(
        "CMS_htt_ttbarShape", "topPtReweightWeight", SquareAndRemoveWeight)
    for variation in top_pt_variations:
        for process in [ttt, ttj]:
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
