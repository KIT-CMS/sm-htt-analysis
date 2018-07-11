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
        "--binning", required=False, type=str, help="Binning configuration.")
    parser.add_argument(
        "--channels",
        default=[],
        nargs='+',
        type=str,
        help="Channels to be considered.")
    parser.add_argument(
        "--categories",
        default=[],
        nargs='+',
        type=str,
        help="Categories to be considered.")
    parser.add_argument(
        "--variables",
        default=[],
        nargs='+',
        type=str,
        help="Variables to be considered.")
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
        "EWKZ"  : Process("EWKZ",     EWKZEstimation   (era, directory, mt, friend_directory=mt_friend_directory))
        }
    mt_processes["QCD"] = Process("QCD", QCDEstimationMT(era, directory, mt, [mt_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWKZ"]], mt_processes["data"], extrapolation_factor=1.17))
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
        "EWKZ"  : Process("EWKZ",     EWKZEstimation   (era, directory, et, friend_directory=et_friend_directory))
        }
    et_processes["QCD"] = Process("QCD", QCDEstimationET(era, directory, et, [et_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV", "EWKZ"]], et_processes["data"], extrapolation_factor=1.16))
    tt = TTSM()
    if args.QCD_extrap_fit:
        tt.cuts.get("os").invert()
#    if args.HIG16043:
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
        "VV"    : Process("VV",       VVEstimation   (era, directory, tt, friend_directory=tt_friend_directory))
#        "EWK"   : Process("EWK",      EWKEstimation  (era, directory, tt, friend_directory=tt_friend_directory))
        }
    tt_processes["QCD"] = Process("QCD", QCDEstimationTT(era, directory, tt, [tt_processes[process] for process in ["ZTT", "ZJ", "ZL", "W", "TTT", "TTJ", "VV"]], tt_processes["data"]))

    # Variables and categories
    #binning = yaml.load(open(args.binning))
    cuts ={ "0jet" : Cuts(Cut("njets==0", "0jet")),
            "1jet" : Cuts(Cut("njets==1", "1jet")),
            "2jet" : Cuts(Cut("njets>=1&&(((mjj<500)||jdeta<3.5))", "2jet")),
            "vbf" : Cuts(Cut("njets>=1", "2jet"), Cut("mjj>500", "mjj"), Cut("jdeta>3.5", "jdeta")),
            "inclusive" : Cuts()
          }
    binnings = { "m" : ConstantBinning(52,40,300),
                 "pt" : ConstantBinning(25,0,500),
                 "px" : ConstantBinning(30,-500,500),
                 "py" : ConstantBinning(30,-500,500),
                 "pz" : ConstantBinning(30,-500,500),
                 "e" : ConstantBinning(25,0,500),
                 "eta" : ConstantBinning(30,-7,7),
                 "phi" : ConstantBinning(30,-3.141,3.141),
          } 


    et_categories = []
    # Analysis shapes
    if "et" in args.channels:
        for j, var in enumerate(args.variables):
            for i, label in enumerate(args.categories):
                key = var.split("_")[0]
                score = Variable(
                     var,
                     binnings[key])
                et_categories.append(
                    Category(
                        label,
                        et,
                        cuts[label],
                        variable=score))
    mt_categories = []
    # Analysis shapes
    if "mt" in args.channels:
        for j, var in enumerate(args.variables):
            for i, label in enumerate(args.categories):
                key = var.split("_")[0]
                score = Variable(
                     var,
                     binnings[key])
                mt_categories.append(
                    Category(
                        label,
                        mt,
                        cuts[label],
                        variable=score))
    tt_categories = []
    # Analysis shapes
    if "tt" in args.channels:
        for j, var in enumerate(args.variables):
            for i, label in enumerate(args.categories):
                key = var.split("_")[0]
                score = Variable(
                     var,
                     binnings[key])
                tt_categories.append(
                    Category(
                        label,
                        tt,
                        cuts[label],
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
#    tau_es_3prong_variations = create_systematic_variations(
#        "CMS_scale_t_3prong0pi0", "tauEsThreeProng", DifferentPipeline)
#    tau_es_1prong_variations = create_systematic_variations(
#        "CMS_scale_t_1prong0pi0", "tauEsOneProng", DifferentPipeline)
#    tau_es_1prong1pizero_variations = create_systematic_variations(
#        "CMS_scale_t_1prong1pi0", "tauEsOneProngPiZeros", DifferentPipeline)
#    for variation in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
#        for process_nick in [
#                "HTT", "VH", "ggH", "qqH", "ZTT", "TTT", "VV", "EWK"
#        ]:
#            if "et" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=et_processes[process_nick],
#                    channel=et,
#                    era=era)
#            if "mt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=mt_processes[process_nick],
#                    channel=mt,
#                    era=era)
#            if "tt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=tt_processes[process_nick],
#                    channel=tt,
#                    era=era)
#
#    # Jet energy scale
#    jet_es_variations = create_systematic_variations("CMS_scale_j", "jecUnc",
#                                                     DifferentPipeline)
#    for variation in jet_es_variations:
#        for process_nick in [
#                "HTT", "VH", "ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT",
#                "TTJ", "VV", "EWK"
#        ]:
#            if "et" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=et_processes[process_nick],
#                    channel=et,
#                    era=era)
#            if "mt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=mt_processes[process_nick],
#                    channel=mt,
#                    era=era)
#            if "tt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=tt_processes[process_nick],
#                    channel=tt,
#                    era=era)
#
#    # MET energy scale
#    met_unclustered_variations = create_systematic_variations(
#        "CMS_scale_met_unclustered", "metUnclusteredEn", DifferentPipeline)
#    met_clustered_variations = create_systematic_variations(
#        "CMS_scale_met_clustered", "metJetEn", DifferentPipeline)
#    for variation in met_unclustered_variations + met_clustered_variations:
#        for process_nick in [
#                "HTT", "VH", "ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT",
#                "TTJ", "VV", "EWK"
#        ]:
#            if "et" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=et_processes[process_nick],
#                    channel=et,
#                    era=era)
#            if "mt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=mt_processes[process_nick],
#                    channel=mt,
#                    era=era)
#            if "tt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=tt_processes[process_nick],
#                    channel=tt,
#                    era=era)
#
#    # Z pt reweighting
#    zpt_variations = create_systematic_variations(
#        "CMS_htt_dyShape", "zPtReweightWeight", SquareAndRemoveWeight)
#    for variation in zpt_variations:
#        for process_nick in ["ZTT", "ZL", "ZJ"]:
#            if "et" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=et_processes[process_nick],
#                    channel=et,
#                    era=era)
#            if "mt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=mt_processes[process_nick],
#                    channel=mt,
#                    era=era)
#            if "tt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=tt_processes[process_nick],
#                    channel=tt,
#                    era=era)
#
#    # top pt reweighting
#    top_pt_variations = create_systematic_variations(
#        "CMS_htt_ttbarShape", "topPtReweightWeight", SquareAndRemoveWeight)
#    for variation in top_pt_variations:
#        for process_nick in ["TTT", "TTJ"]:
#            if "et" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=et_processes[process_nick],
#                    channel=et,
#                    era=era)
#            if "mt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=mt_processes[process_nick],
#                    channel=mt,
#                    era=era)
#            if "tt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=tt_processes[process_nick],
#                    channel=tt,
#                    era=era)
#
#    # jet to tau fake efficiency
#    jet_to_tau_fake_variations = []
#    jet_to_tau_fake_variations.append(
#        AddWeight("CMS_htt_jetToTauFake", "jetToTauFake_weight",
#                  Weight("(pt_2*1.02)", "jetToTauFake_weight"), "Up"))
#    jet_to_tau_fake_variations.append(
#        AddWeight("CMS_htt_jetToTauFake", "jetToTauFake_weight",
#                  Weight("((pt_2*0.98))", "jetToTauFake_weight"), "Down"))
#    for variation in jet_to_tau_fake_variations:
#        for process_nick in ["ZJ", "TTJ", "W"]:
#            if "et" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=et_processes[process_nick],
#                    channel=et,
#                    era=era)
#            if "mt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=mt_processes[process_nick],
#                    channel=mt,
#                    era=era)
#            if "tt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=tt_processes[process_nick],
#                    channel=tt,
#                    era=era)
#
#    # Zll reweighting
#    zll_et_weight_variations = []
#    zll_et_weight_variations.append(
#        ReplaceWeight(
#            "CMS_htt_eToTauFake_OneProng", "decay_mode_reweight",
#            Weight(
#                "(((decayMode_2 == 0)*0.98*1.12) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.2) + ((decayMode_2 == 10)*1.0))",
#                "decay_mode_reweight"), "Up"))
#    zll_et_weight_variations.append(
#        ReplaceWeight(
#            "CMS_htt_eToTauFake_OneProng", "decay_mode_reweight",
#            Weight(
#                "(((decayMode_2 == 0)*0.98*0.88) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.2) + ((decayMode_2 == 10)*1.0))",
#                "decay_mode_reweight"), "Down"))
#    zll_et_weight_variations.append(
#        ReplaceWeight(
#            "CMS_htt_eToTauFake_OneProngPiZeros", "decay_mode_reweight",
#            Weight(
#                "(((decayMode_2 == 0)*0.98) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.2*1.12) + ((decayMode_2 == 10)*1.0))",
#                "decay_mode_reweight"), "Up"))
#    zll_et_weight_variations.append(
#        ReplaceWeight(
#            "CMS_htt_eToTauFake_OneProngPiZeros", "decay_mode_reweight",
#            Weight(
#                "(((decayMode_2 == 0)*0.98) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.2*0.88) + ((decayMode_2 == 10)*1.0))",
#                "decay_mode_reweight"), "Down"))
#    for variation in zll_et_weight_variations:
#        for process_nick in ["ZL"]:
#            if "et" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=et_processes[process_nick],
#                    channel=et,
#                    era=era)
#    zll_mt_weight_variations = []
#    zll_mt_weight_variations.append(
#        ReplaceWeight(
#            "CMS_htt_mToTauFake_OneProng", "decay_mode_reweight",
#            Weight(
#                "(((decayMode_2 == 0)*0.75*1.25) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.0) + ((decayMode_2 == 10)*1.0))",
#                "decay_mode_reweight"), "Up"))
#    zll_mt_weight_variations.append(
#        ReplaceWeight(
#            "CMS_htt_mToTauFake_OneProng", "decay_mode_reweight",
#            Weight(
#                "(((decayMode_2 == 0)*0.75*0.75) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.0) + ((decayMode_2 == 10)*1.0))",
#                "decay_mode_reweight"), "Down"))
#    zll_mt_weight_variations.append(
#        ReplaceWeight(
#            "CMS_htt_mToTauFake_OneProngPiZeros", "decay_mode_reweight",
#            Weight(
#                "(((decayMode_2 == 0)*0.75) + ((decayMode_2 == 1 || decayMode_2 == 2)*1.25) + ((decayMode_2 == 10)*1.0))",
#                "decay_mode_reweight"), "Up"))
#    zll_mt_weight_variations.append(
#        ReplaceWeight(
#            "CMS_htt_mToTauFake_OneProngPiZeros", "decay_mode_reweight",
#            Weight(
#                "(((decayMode_2 == 0)*0.75) + ((decayMode_2 == 1 || decayMode_2 == 2)*0.75) + ((decayMode_2 == 10)*1.0))",
#                "decay_mode_reweight"), "Down"))
#    for variation in zll_mt_weight_variations:
#        for process_nick in ["ZL"]:
#            if "mt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=mt_processes[process_nick],
#                    channel=mt,
#                    era=era)
#
#    # b tagging
#    btag_eff_variations = create_systematic_variations(
#        "CMS_htt_eff_b", "btagEff", DifferentPipeline)
#    mistag_eff_variations = create_systematic_variations(
#        "CMS_htt_mistag_b", "btagMistag", DifferentPipeline)
#    for variation in btag_eff_variations + mistag_eff_variations:
#        for process_nick in [
#                "HTT", "VH", "ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT",
#                "TTJ", "VV", "EWK"
#        ]:
#            if "et" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=et_processes[process_nick],
#                    channel=et,
#                    era=era)
#            if "mt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=mt_processes[process_nick],
#                    channel=mt,
#                    era=era)
#            if "tt" in [args.gof_channel] + args.channels:
#                systematics.add_systematic_variation(
#                    variation=variation,
#                    process=tt_processes[process_nick],
#                    channel=tt,
#                    era=era)
#
    # Produce histograms
    print systematics    
    systematics.produce()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_shapes.log", logging.INFO)
    main(args)
