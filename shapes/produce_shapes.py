#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from shape_producer.channel import ETSM, MTSM, TTSM

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
        "--gof-channel",
        default=None,
        type=str,
        help="Channel for goodness of fit shapes.")
    parser.add_argument(
        "--QCD-extrap-fit",
        default=False,
        action='store_true',
        help="Create shapes for QCD extrapolation factor determination.")
    parser.add_argument(
        "--gof-variable",
        type=str,
        help="Variable for goodness of fit shapes.")
    parser.add_argument(
        "--HIG16043",
        action="store_true",
        default=False,
        help="Create shapes of HIG16043 reference analysis.")
    parser.add_argument(
        "--num-threads",
        default=32,
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
    systematics = Systematics("shapes.root", num_threads=args.num_threads)

    # Era
    era = Run2016(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory
    et_friend_directory = args.et_friend_directory
    mt_friend_directory = args.mt_friend_directory
    tt_friend_directory = args.tt_friend_directory
    mt = MTSM()
    if args.QCD_extrap_fit:
        mt.cuts.remove("muon_iso")
        mt.cuts.add(Cut("(iso_1<0.5)*(iso_1>=0.15)", "muon_iso_loose"))
    if args.emb:
        mt.cuts.remove("trg_singlemuoncross")
        mt.cuts.add(Cut("(trg_singlemuon==1 && pt_1>23 && pt_2>30)", "trg_singlemuon"))
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, mt, friend_directory=mt_friend_directory)),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH"   : Process("ggH",      ggHEstimation   (era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH"   : Process("qqH",      qqHEstimation   (era, directory, mt, friend_directory=mt_friend_directory)),
        "VH"    : Process("VH",       VHEstimation    (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationMTSM(era, directory, mt, friend_directory=mt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationMT  (era, directory, mt, friend_directory=mt_friend_directory)),
        "W"     : Process("W",        WEstimation     (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationMT (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationMT (era, directory, mt, friend_directory=mt_friend_directory)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, mt, friend_directory=mt_friend_directory)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, mt, friend_directory=mt_friend_directory))
        }
    if args.emb:
        mt_processes["ZTT"] = Process("ZTT", ZTTEmbeddedEstimation(era, directory, mt, friend_directory=mt_friend_directory))
        mt_processes["TTT"] = Process("TTT", TTLEstimationMT (era, directory, mt, friend_directory=mt_friend_directory))
    mt_processes["QCD"] = Process("QCD", QCDEstimationMT(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK"]], mt_processes["data"], extrapolation_factor=1.17))
    et = ETSM()
    if args.QCD_extrap_fit:
        et.cuts.remove("ele_iso")
        et.cuts.add(Cut("(iso_1<0.5)*(iso_1>=0.1)", "ele_iso_loose"))
    et_processes = {
        "data"  : Process("data_obs", DataEstimation  (era, directory, et, friend_directory=et_friend_directory)),
        "HTT"   : Process("HTT",      HTTEstimation   (era, directory, et, friend_directory=et_friend_directory)),
        "ggH"   : Process("ggH",      ggHEstimation   (era, directory, et, friend_directory=et_friend_directory)),
        "qqH"   : Process("qqH",      qqHEstimation   (era, directory, et, friend_directory=et_friend_directory)),
        "VH"    : Process("VH",       VHEstimation    (era, directory, et, friend_directory=et_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimation   (era, directory, et, friend_directory=et_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationETSM(era, directory, et, friend_directory=et_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationET  (era, directory, et, friend_directory=et_friend_directory)),
        "W"     : Process("W",        WEstimation     (era, directory, et, friend_directory=et_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationET (era, directory, et, friend_directory=et_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationET (era, directory, et, friend_directory=et_friend_directory)),
        "VV"    : Process("VV",       VVEstimation    (era, directory, et, friend_directory=et_friend_directory)),
        "EWK"   : Process("EWK",      EWKEstimation   (era, directory, et, friend_directory=et_friend_directory))
        }
    if args.emb:
        et_processes["ZTT"] = Process("ZTT", ZTTEmbeddedEstimation(era, directory, et, friend_directory=et_friend_directory))
        et_processes["TTT"] = Process("TTT", TTLEstimationET (era, directory, et, friend_directory=et_friend_directory))
    et_processes["QCD"] = Process("QCD", QCDEstimationET(era, directory, et, [et_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK"]], et_processes["data"], extrapolation_factor=1.16))
    tt = TTSM()
    if args.QCD_extrap_fit:
        tt.cuts.get("os").invert()
    if args.HIG16043:
        tt.cuts.remove("pt_h")
    tt_processes = {
        "data"  : Process("data_obs", DataEstimation (era, directory, tt, friend_directory=tt_friend_directory)),
        "HTT"   : Process("HTT",      HTTEstimation  (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH"   : Process("ggH",      ggHEstimation  (era, directory, tt, friend_directory=tt_friend_directory)),
        "qqH"   : Process("qqH",      qqHEstimation  (era, directory, tt, friend_directory=tt_friend_directory)),
        "VH"    : Process("VH",       VHEstimation   (era, directory, tt, friend_directory=tt_friend_directory)),
        "ZTT"   : Process("ZTT",      ZTTEstimationTT(era, directory, tt, friend_directory=tt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimationTT (era, directory, tt, friend_directory=tt_friend_directory)),
        "ZJ"    : Process("ZJ",       ZJEstimationTT (era, directory, tt, friend_directory=tt_friend_directory)),
        "W"     : Process("W",        WEstimation    (era, directory, tt, friend_directory=tt_friend_directory)),
        "TTT"   : Process("TTT",      TTTEstimationTT(era, directory, tt, friend_directory=tt_friend_directory)),
        "TTJ"   : Process("TTJ",      TTJEstimationTT(era, directory, tt, friend_directory=tt_friend_directory)),
        "VV"    : Process("VV",       VVEstimation   (era, directory, tt, friend_directory=tt_friend_directory)),
        "EWK"   : Process("EWK",      EWKEstimation  (era, directory, tt, friend_directory=tt_friend_directory)),
        }
    if args.emb:
        tt_processes["ZTT"] = Process("ZTT", ZTTEmbeddedEstimation(era, directory, tt, friend_directory=tt_friend_directory))
        tt_processes["TTT"] = Process("TTT", TTLEstimationTT (era, directory, tt, friend_directory=tt_friend_directory))

    tt_processes["QCD"] = Process("QCD", QCDEstimationTT(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWK"]], tt_processes["data"]))

    # Variables and categories
    binning = yaml.load(open(args.binning))

    et_categories = []
    # HIG16043 shapes
    if "et" in args.channels and args.HIG16043:
        for category in ["0jet", "vbf", "boosted"]:
            variable = Variable(
                    binning["HIG16043"]["et"][category]["variable"],
                    VariableBinning(binning["HIG16043"]["et"][category]["binning"]),
                    expression=binning["HIG16043"]["et"][category]["expression"])
            et_categories.append(
                Category(
                    category,
                    et,
                    Cuts(
                        Cut(binning["HIG16043"]["et"][category]["cut_unrolling"],
                            "et_cut_unrolling_{}".format(category)),
                        Cut(binning["HIG16043"]["et"][category]["cut_category"],
                            "et_cut_category_{}".format(category))
                        ),
                    variable=variable))
    # Analysis shapes
    elif "et" in args.channels:
        for i, label in enumerate(["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"]):
            score = Variable(
                "et_max_score",
                 VariableBinning(binning["analysis"]["et"][label]))
            et_categories.append(
                Category(
                    label,
                    et,
                    Cuts(
                        Cut("et_max_index=={index}".format(index=i), "exclusive_score")),
                    variable=score))
    # Goodness of fit shapes
    elif "et" == args.gof_channel:
        score = Variable(
                args.gof_variable,
                VariableBinning(binning["gof"]["et"][args.gof_variable]["bins"]),
                expression=binning["gof"]["et"][args.gof_variable]["expression"])
        if "cut" in binning["gof"]["et"][args.gof_variable].keys():
            cuts=Cuts(Cut(binning["gof"]["et"][args.gof_variable]["cut"], "binning"))
        else:
            cuts=Cuts()
        et_categories.append(
            Category(
                args.gof_variable,
                et,
                cuts,
                variable=score))

    mt_categories = []
    # HIG16043 shapes
    if "mt" in args.channels and args.HIG16043:
        for category in ["0jet", "vbf", "boosted"]:
            variable = Variable(
                    binning["HIG16043"]["mt"][category]["variable"],
                    VariableBinning(binning["HIG16043"]["mt"][category]["binning"]),
                    expression=binning["HIG16043"]["mt"][category]["expression"])
            mt_categories.append(
                Category(
                    category,
                    mt,
                    Cuts(
                        Cut(binning["HIG16043"]["mt"][category]["cut_unrolling"],
                            "mt_cut_unrolling_{}".format(category)),
                        Cut(binning["HIG16043"]["mt"][category]["cut_category"],
                            "mt_cut_category_{}".format(category))
                        ),
                    variable=variable))
    # Analysis shapes
    elif "mt" in args.channels:
        for i, label in enumerate(["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"]):
            score = Variable(
                "mt_max_score",
                 VariableBinning(binning["analysis"]["mt"][label]))
            mt_categories.append(
                Category(
                    label,
                    mt,
                    Cuts(
                        Cut("mt_max_index=={index}".format(index=i), "exclusive_score")),
                    variable=score))
    # Goodness of fit shapes
    elif args.gof_channel == "mt":
        score = Variable(
                args.gof_variable,
                VariableBinning(binning["gof"]["mt"][args.gof_variable]["bins"]),
                expression=binning["gof"]["mt"][args.gof_variable]["expression"])
        if "cut" in binning["gof"]["mt"][args.gof_variable].keys():
            cuts=Cuts(Cut(binning["gof"]["mt"][args.gof_variable]["cut"], "binning"))
        else:
            cuts=Cuts()
        mt_categories.append(
            Category(
                args.gof_variable,
                mt,
                cuts,
                variable=score))

    tt_categories = []
    # HIG16043 shapes
    if "tt" in args.channels and args.HIG16043:
        for category in ["0jet", "vbf", "boosted"]:
            variable = Variable(
                    binning["HIG16043"]["tt"][category]["variable"],
                    VariableBinning(binning["HIG16043"]["tt"][category]["binning"]),
                    expression=binning["HIG16043"]["tt"][category]["expression"])
            tt_categories.append(
                Category(
                    category,
                    tt,
                    Cuts(
                        Cut(binning["HIG16043"]["tt"][category]["cut_unrolling"],
                            "tt_cut_unrolling_{}".format(category)),
                        Cut(binning["HIG16043"]["tt"][category]["cut_category"],
                            "tt_cut_category_{}".format(category))
                        ),
                    variable=variable))
    # Analysis shapes
    elif "tt" in args.channels:
        for i, label in enumerate(["ggh", "qqh", "ztt", "noniso", "misc"]):
            score = Variable(
                "tt_max_score",
                 VariableBinning(binning["analysis"]["tt"][label]))
            tt_categories.append(
                Category(
                    label,
                    tt,
                    Cuts(
                        Cut("tt_max_index=={index}".format(index=i), "exclusive_score")),
                    variable=score))
    # Goodness of fit shapes
    elif args.gof_channel == "tt":
        score = Variable(
                args.gof_variable,
                VariableBinning(binning["gof"]["tt"][args.gof_variable]["bins"]),
                expression=binning["gof"]["tt"][args.gof_variable]["expression"])
        if "cut" in binning["gof"]["tt"][args.gof_variable].keys():
            cuts=Cuts(Cut(binning["gof"]["tt"][args.gof_variable]["cut"], "binning"))
        else:
            cuts=Cuts()
        tt_categories.append(
            Category(
                args.gof_variable,
                tt,
                cuts,
                variable=score))

    # Nominal histograms
    # yapf: enable
    if "et" in [args.gof_channel] + args.channels:
        for process, category in product(et_processes.values(), et_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))

    if "mt" in [args.gof_channel] + args.channels:
        for process, category in product(mt_processes.values(), mt_categories):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))
    if "tt" in [args.gof_channel] + args.channels:
        for process, category in product(tt_processes.values(), tt_categories):
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
        for process_nick in [
                "HTT", "VH", "ggH", "qqH", "ZTT", "TTT", "VV", "EWK"
        ]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # Jet energy scale
    jet_es_variations = create_systematic_variations("CMS_scale_j", "jecUnc",
                                                     DifferentPipeline)
    for variation in jet_es_variations:
        for process_nick in [
                "HTT", "VH", "ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT",
                "TTJ", "VV", "EWK"
        ]:
            if args.emb and process_nick == 'ZTT':
                continue
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # MET energy scale
    met_unclustered_variations = create_systematic_variations(
        "CMS_scale_met_unclustered", "metUnclusteredEn", DifferentPipeline)
    met_clustered_variations = create_systematic_variations(
        "CMS_scale_met_clustered", "metJetEn", DifferentPipeline)
    for variation in met_unclustered_variations + met_clustered_variations:
        for process_nick in [
                "HTT", "VH", "ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT",
                "TTJ", "VV", "EWK"
        ]:
            if args.emb and process_nick == 'ZTT':
                continue
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # Z pt reweighting
    zpt_variations = create_systematic_variations(
        "CMS_htt_dyShape", "zPtReweightWeight", SquareAndRemoveWeight)
    for variation in zpt_variations:
        for process_nick in ["ZTT", "ZL", "ZJ"]:
            if args.emb and process_nick == 'ZTT':
                continue
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # top pt reweighting
    top_pt_variations = create_systematic_variations(
        "CMS_htt_ttbarShape", "topPtReweightWeight", SquareAndRemoveWeight)
    for variation in top_pt_variations:
        for process_nick in ["TTT", "TTJ"]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # jet to tau fake efficiency

    jet_to_tau_fake_variations = []
    jet_to_tau_fake_variations.append(
        AddWeight("CMS_htt_jetToTauFake", "jetToTauFake_weight",
                  Weight("(1.0+pt_2*0.002)", "jetToTauFake_weight"), "Up"))
    jet_to_tau_fake_variations.append(
        AddWeight("CMS_htt_jetToTauFake", "jetToTauFake_weight",
                  Weight("(1.0-pt_2*0.002)", "jetToTauFake_weight"), "Down"))
    for variation in jet_to_tau_fake_variations:
        for process_nick in ["ZJ", "TTJ", "W"]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)

    # Zll reweighting
    zll_et_weight_variations = []
    zll_et_weight_variations.append(
        ReplaceWeight(
            "CMS_htt_eToTauFake_OneProng", "decay_mode_reweight",
            Weight(
                "(((decayMode_2 == 0)*0.98*1.12) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.2) + ((decayMode_2 == 10)*1.0))",
                "decay_mode_reweight"), "Up"))
    zll_et_weight_variations.append(
        ReplaceWeight(
            "CMS_htt_eToTauFake_OneProng", "decay_mode_reweight",
            Weight(
                "(((decayMode_2 == 0)*0.98*0.88) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.2) + ((decayMode_2 == 10)*1.0))",
                "decay_mode_reweight"), "Down"))
    zll_et_weight_variations.append(
        ReplaceWeight(
            "CMS_htt_eToTauFake_OneProngPiZeros", "decay_mode_reweight",
            Weight(
                "(((decayMode_2 == 0)*0.98) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.2*1.12) + ((decayMode_2 == 10)*1.0))",
                "decay_mode_reweight"), "Up"))
    zll_et_weight_variations.append(
        ReplaceWeight(
            "CMS_htt_eToTauFake_OneProngPiZeros", "decay_mode_reweight",
            Weight(
                "(((decayMode_2 == 0)*0.98) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.2*0.88) + ((decayMode_2 == 10)*1.0))",
                "decay_mode_reweight"), "Down"))
    for variation in zll_et_weight_variations:
        for process_nick in ["ZL"]:
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
    zll_mt_weight_variations = []
    zll_mt_weight_variations.append(
        ReplaceWeight(
            "CMS_htt_mToTauFake_OneProng", "decay_mode_reweight",
            Weight(
                "(((decayMode_2 == 0)*0.75*1.25) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.0) + ((decayMode_2 == 10)*1.0))",
                "decay_mode_reweight"), "Up"))
    zll_mt_weight_variations.append(
        ReplaceWeight(
            "CMS_htt_mToTauFake_OneProng", "decay_mode_reweight",
            Weight(
                "(((decayMode_2 == 0)*0.75*0.75) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.0) + ((decayMode_2 == 10)*1.0))",
                "decay_mode_reweight"), "Down"))
    zll_mt_weight_variations.append(
        ReplaceWeight(
            "CMS_htt_mToTauFake_OneProngPiZeros", "decay_mode_reweight",
            Weight(
                "(((decayMode_2 == 0)*0.75) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.25) + ((decayMode_2 == 10)*1.0))",
                "decay_mode_reweight"), "Up"))
    zll_mt_weight_variations.append(
        ReplaceWeight(
            "CMS_htt_mToTauFake_OneProngPiZeros", "decay_mode_reweight",
            Weight(
                "(((decayMode_2 == 0)*0.75) + ((decayMode_2 == 1 || decayMode_2 == 2)*0.75) + ((decayMode_2 == 10)*1.0))",
                "decay_mode_reweight"), "Down"))
    for variation in zll_mt_weight_variations:
        for process_nick in ["ZL"]:
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # b tagging
    btag_eff_variations = create_systematic_variations(
        "CMS_htt_eff_b", "btagEff", DifferentPipeline)
    mistag_eff_variations = create_systematic_variations(
        "CMS_htt_mistag_b", "btagMistag", DifferentPipeline)
    for variation in btag_eff_variations + mistag_eff_variations:
        for process_nick in [
                "HTT", "VH", "ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT",
                "TTJ", "VV", "EWK"
        ]:
            if args.emb and process_nick == 'ZTT':
                continue
            if "et" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "mt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
            if "tt" in [args.gof_channel] + args.channels:
                systematics.add_systematic_variation(
                    variation=variation,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)
    if args.emb:
        # Embedded event specifics

        # 10% removed events in ttbar simulation (ttbar -> real tau tau events) will be added/subtracted to ZTT shape to use as systematic
        tttautau_process_mt = Process(
            "TTTT",
            TTTTEstimationMT(
                era, directory, mt, friend_directory=mt_friend_directory))
        tttautau_process_et = Process(
            "TTTT",
            TTTTEstimationET(
                era, directory, et, friend_directory=et_friend_directory))
        tttautau_process_tt = Process(
            "TTTT",
            TTTEstimationTT(
                era, directory, tt, friend_directory=tt_friend_directory))
        if 'mt' in [args.gof_channel] + args.channels:
            for category in mt_categories:
                mt_processes['ZTTpTTTauTauDown'] = Process(
                    "ZTTpTTTauTauDown",
                    AddHistogramEstimationMethod(
                        "AddHistogram", "nominal", era, directory, mt,
                        [mt_processes["ZTT"], tttautau_process_mt],
                        [1.0, -0.1]))
                systematics.add(
                    Systematic(
                        category=category,
                        process=mt_processes['ZTTpTTTauTauDown'],
                        analysis="smhtt",
                        era=era,
                        variation=Relabel("CMS_htt_emb_ttbar", "Down"),
                        mass="125"))

                mt_processes['ZTTpTTTauTauUp'] = Process(
                    "ZTTpTTTauTauUp",
                    AddHistogramEstimationMethod(
                        "AddHistogram", "nominal", era, directory, mt,
                        [mt_processes["ZTT"], tttautau_process_mt],
                        [1.0, 0.1]))
                systematics.add(
                    Systematic(
                        category=category,
                        process=mt_processes['ZTTpTTTauTauUp'],
                        analysis="smhtt",
                        era=era,
                        variation=Relabel("CMS_htt_emb_ttbar", "Up"),
                        mass="125"))

                #Muon ES uncertainty (needed for smearing due to initial reconstruction)
                muon_es_variations = create_systematic_variations(
                    "CMS_scale_muonES", "muonES", DifferentPipeline)
                for variation in muon_es_variations:
                    for process_nick in ["ZTT"]:
                        if "mt" in [args.gof_channel] + args.channels:
                            systematics.add_systematic_variation(
                                variation=variation,
                                process=mt_processes[process_nick],
                                channel=mt,
                                era=era)

        if 'et' in [args.gof_channel] + args.channels:
            for category in et_categories:
                et_processes['ZTTpTTTauTauDown'] = Process(
                    "ZTTpTTTauTauDown",
                    AddHistogramEstimationMethod(
                        "AddHistogram", "nominal", era, directory, et,
                        [et_processes["ZTT"], tttautau_process_et],
                        [1.0, -0.1]))
                systematics.add(
                    Systematic(
                        category=category,
                        process=et_processes['ZTTpTTTauTauDown'],
                        analysis="smhtt",
                        era=era,
                        variation=Relabel("CMS_htt_emb_ttbar", "Down"),
                        mass="125"))

                et_processes['ZTTpTTTauTauUp'] = Process(
                    "ZTTpTTTauTauUp",
                    AddHistogramEstimationMethod(
                        "AddHistogram", "nominal", era, directory, et,
                        [et_processes["ZTT"], tttautau_process_et],
                        [1.0, 0.1]))
                systematics.add(
                    Systematic(
                        category=category,
                        process=et_processes['ZTTpTTTauTauUp'],
                        analysis="smhtt",
                        era=era,
                        variation=Relabel("CMS_htt_emb_ttbar", "Up"),
                        mass="125"))
        if 'tt' in [args.gof_channel] + args.channels:
            for category in tt_categories:
                tt_processes['ZTTpTTTauTauDown'] = Process(
                    "ZTTpTTTauTauDown",
                    AddHistogramEstimationMethod(
                        "AddHistogram", "nominal", era, directory, tt,
                        [tt_processes["ZTT"], tttautau_process_tt],
                        [1.0, -0.1]))
                systematics.add(
                    Systematic(
                        category=category,
                        process=tt_processes['ZTTpTTTauTauDown'],
                        analysis="smhtt",
                        era=era,
                        variation=Relabel("CMS_htt_emb_ttbar", "Down"),
                        mass="125"))

                tt_processes['ZTTpTTTauTauUp'] = Process(
                    "ZTTpTTTauTauUp",
                    AddHistogramEstimationMethod(
                        "AddHistogram", "nominal", era, directory, tt,
                        [tt_processes["ZTT"], tttautau_process_tt],
                        [1.0, 0.1]))
                systematics.add(
                    Systematic(
                        category=category,
                        process=tt_processes['ZTTpTTTauTauUp'],
                        analysis="smhtt",
                        era=era,
                        variation=Relabel("CMS_htt_emb_ttbar", "Up"),
                        mass="125"))

    # Produce histograms
    systematics.produce()


if __name__ == "__main__":
    args = parse_arguments()
    if ('tt' in args.channels or 'em' in args.channels) and args.emb:
        print "Channels tt and em not yet considered for embedded background estimation."
        exit()
    setup_logging("produce_shapes.log", logging.INFO)
    main(args)
