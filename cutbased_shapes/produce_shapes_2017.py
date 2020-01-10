#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
ROOT.gErrorIgnoreLevel = ROOT.kError

from shape_producer.cutstring import Cut, Cuts, Weight
from shape_producer.systematics import Systematics, Systematic
from shape_producer.categories import Category
from shape_producer.binning import ConstantBinning, VariableBinning
from shape_producer.variable import Variable
from shape_producer.systematic_variations import Nominal, DifferentPipeline, SquareAndRemoveWeight, create_systematic_variations, AddWeight, ReplaceWeight, Relabel
from shape_producer.process import Process
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.channel import ETMSSM2017, MTMSSM2017, TTMSSM2017, EMMSSM2017

from itertools import product

import argparse
import yaml
import copy
import numpy as np
import sys

import logging
logger = logging.getLogger()


def construct_variable(binning_configuration, variablename):
    expression = binning_configuration["variables"][variablename]["expression"]
    binning_structure = binning_configuration["variables"][variablename]["bins"]
    end = 0.0
    bins = np.concatenate([np.arange(start, end, step) for start, end, step in binning_structure] + [np.array([end])])
    return Variable(variablename, VariableBinning(sorted(bins)), expression)


def create_cut_map(binning, channel):
    cut_map = {}
    for cat, cut in binning["cutbased"][channel].iteritems():
        cut_map[cat] = [Cut(cut, cat)]
        if cat in ["nobtag", "nobtag_lowmsv"]:
            for subcat, add_cut in binning["stxs_stage1p1_v2"][channel].iteritems():
                cut_list = copy.deepcopy(cut_map[cat])
                cut_list.append(Cut(add_cut, "_".join([cat, subcat])))
                cut_map["_".join([cat, subcat])] = cut_list
    return cut_map


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
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument(
        "--discriminator-variable",
        type=str,
        help="Variable chosen as final discriminator for cut-based analysis.")
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
        "--tag", default="ERA_CHANNEL", type=str, help="Tag of output files.")
    parser.add_argument(
        "--skip-systematic-variations",
        action='store_true',
        help="Do not produce the systematic variations.")
    parser.add_argument(
        "--shape-group",
        default="backgrounds",
        choices=["backgrounds", "sm_signals", "bbH", "ggH_t", "ggH_b", "ggH_i", "ggA_i", "ggA_t", "ggA_b", "ggh_i", "ggh_t", "ggh_b"],
        type=str,
        help="Process groups to be considered within the shape production")
    parser.add_argument(
        "--category",
        default="nobtag",
        type=str,
        help="Category to be considered within the shape production")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    logger.info("Set up shape variations.")
    systematics = Systematics(
        "{}_cutbased_shapes_{}.root".format(args.tag,args.discriminator_variable),
        num_threads=args.num_threads,
        skip_systematic_variations=args.skip_systematic_variations)

    # Era selection
    if "2017" in args.era:
        from shape_producer.estimation_methods_2017 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, qqHEstimation, VHEstimation, WHEstimation, ZHEstimation, ttHEstimation, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, NewFakeEstimationLT, NewFakeEstimationTT, HWWEstimation, ggHWWEstimation, qqHWWEstimation, SUSYggHEstimation, SUSYbbHEstimation

        from shape_producer.era import Run2017
        era = Run2017(args.datasets)

    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # Channels and processes
    # yapf: disable
    directory = args.directory
    friend_directories = {
        "et" : args.et_friend_directory,
        "mt" : args.mt_friend_directory,
        "tt" : args.tt_friend_directory,
        "em" : args.em_friend_directory,
    }
    ff_friend_directory = args.fake_factor_friend_directory

    channel_dict = {
        "mt" : MTMSSM2017(),
        "et" : ETMSSM2017(),
        "tt" : TTMSSM2017(),
        "em" : EMMSSM2017(),

    }

    susyggH_masses = [80, 90, 100, 110, 120, 130, 140, 180, 200, 250, 300, 350, 400, 450, 600, 700, 800, 900, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200]
    susybbH_masses = [80, 90, 100, 110, 120, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 600, 700, 800, 900, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200]
    susybbH_nlo_masses = [80, 90, 100, 110, 120, 125, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200, 3500]

    processes = {
        "mt" : {},
        "et" : {},
        "tt" : {},
        "em" : {},
    }

    for ch in args.channels:

        # common processes
        if args.shape_group == "backgrounds":
            processes[ch]["data"] = Process("data_obs", DataEstimation         (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))
            processes[ch]["EMB"]  = Process("EMB",      ZTTEmbeddedEstimation  (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))
            processes[ch]["ZL"]   = Process("ZL",       ZLEstimation           (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))
            processes[ch]["TTL"]  = Process("TTL",      TTLEstimation          (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))
            processes[ch]["VVL"]  = Process("VVL",      VVLEstimation          (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))

            processes[ch]["VH125"]   = Process("VH125",    VHEstimation        (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))
            processes[ch]["WH125"]   = Process("WH125",    WHEstimation        (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))
            processes[ch]["ZH125"]   = Process("ZH125",    ZHEstimation        (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))
            processes[ch]["ttH125"]  = Process("ttH125",   ttHEstimation       (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))

            processes[ch]["ggHWW125"] = Process("ggHWW125", ggHWWEstimation       (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))
            processes[ch]["qqHWW125"] = Process("qqHWW125", qqHWWEstimation       (era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))

        # mssm ggH and bbH signals
        if "gg" in args.shape_group:
            for m in susyggH_masses:
                name = args.shape_group + "_" + str(m)
                processes[ch][name] = Process(name, SUSYggHEstimation(era, directory, channel_dict[ch], str(m), args.shape_group.replace("gg",""), friend_directory=friend_directories[ch]))
        if args.shape_group == "bbH":
            for m in susybbH_masses:
                name = "bbH_" + str(m)
                processes[ch][name] = Process(name, SUSYbbHEstimation(era, directory, channel_dict[ch], str(m), friend_directory=friend_directories[ch]))

        if args.shape_group == "sm_signals":
            # stage 0 and stage 1.1 ggh and qqh
            for ggH_htxs in ggHEstimation.htxs_dict:
                processes[ch][ggH_htxs] = Process(ggH_htxs, ggHEstimation(ggH_htxs, era, directory, channel_dict[ch], friend_directory=[]))  # friend_directories[ch]))
            for qqH_htxs in qqHEstimation.htxs_dict:
                processes[ch][qqH_htxs] = Process(qqH_htxs, qqHEstimation(qqH_htxs, era, directory, channel_dict[ch], friend_directory=[]))  # friend_directories[ch]))

        # channel-specific processes
        if args.shape_group == "backgrounds":
            if ch in ["mt", "et"]:
                processes[ch]["FAKES"] = Process("jetFakes", NewFakeEstimationLT(era, directory, channel_dict[ch], [processes[ch][process] for process in ["EMB", "ZL", "TTL", "VVL"]], processes[ch]["data"], friend_directory=friend_directories[ch]+[ff_friend_directory]))
            elif ch == "tt":
                processes[ch]["FAKES"] = Process("jetFakes", NewFakeEstimationTT(era, directory, channel_dict[ch], [processes[ch][process] for process in ["EMB", "ZL", "TTL", "VVL"]], processes[ch]["data"], friend_directory=friend_directories[ch]+[ff_friend_directory]))
            elif ch == "em":
                processes[ch]["W"]   = Process("W",   WEstimation(era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))
                processes[ch]["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, channel_dict[ch], [processes[ch][process] for process in ["EMB", "ZL", "W", "VVL", "TTL"]], processes[ch]["data"], extrapolation_factor=1.0, qcd_weight = Weight("em_qcd_extrap_up_Weight","qcd_weight")))

    # Variables and categories
    if sys.version_info.major <= 2 and sys.version_info.minor <= 7 and sys.version_info.micro <= 15:
        binning = yaml.load(open(args.binning))
    else:
        binning = yaml.load(open(args.binning), Loader=yaml.FullLoader)

    # Cut-based analysis shapes
    categories = {
        "mt" : [],
        "et" : [],
        "tt" : [],
        "em" : [],
    }

    for ch in args.channels:
        discriminator = construct_variable(binning, args.discriminator_variable)
        # Get dictionary mapping category name to cut objects.
        cut_dict = create_cut_map(binning, ch)
        # Create full set of cuts from dict and create category using these cuts.
        cuts = Cuts(*cut_dict[args.category])
        categories[ch].append(Category(args.category, channel_dict[ch], cuts, variable=discriminator))


    # Choice of activated signal processes
    signal_nicks = []

    sm_htt_backgrounds_nicks = ["WH125", "ZH125", "VH125", "ttH125"]
    sm_hww_nicks = ["ggHWW125", "qqHWW125"]
    sm_htt_signals_nicks = [ggH_htxs for ggH_htxs in ggHEstimation.htxs_dict] + [qqH_htxs for qqH_htxs in qqHEstimation.htxs_dict]
    susy_nicks = []
    if "gg" in args.shape_group:
        for m in susyggH_masses:
            susy_nicks.append(args.shape_group + "_" + str(m))
    if args.shape_group == "bbH":
        for m in susybbH_masses:
            susy_nicks.append("bbH_" + str(m))

    if args.shape_group == "backgrounds":
        signal_nicks = sm_htt_backgrounds_nicks + sm_hww_nicks
    elif args.shape_group == "sm_signals":
        signal_nicks = sm_htt_signals_nicks
    else:
        signal_nicks = susy_nicks

    # Nominal histograms
    for ch in args.channels:
        for process, category in product(processes[ch].values(), categories[ch]):
            systematics.add(Systematic(category=category, process=process, analysis="mssmvssm", era=era, variation=Nominal(), mass="125"))

    # Setup shapes variations

    # EMB: 10% removed events in ttbar simulation (ttbar -> real tau tau events) will be added/subtracted to EMB shape to use as systematic. Technical procedure different to usual systematic variations
    if args.shape_group == "backgrounds":
        tttautau_process = {}
        for ch in args.channels:
            tttautau_process[ch] = Process("TTT", TTTEstimation(era, directory, channel_dict[ch], friend_directory=friend_directories[ch]))
            processes[ch]['ZTTpTTTauTauDown'] = Process("ZTTpTTTauTauDown", AddHistogramEstimationMethod("AddHistogram", "nominal", era, directory, channel_dict[ch], [processes[ch]["EMB"], tttautau_process[ch]], [1.0, -0.1]))
            processes[ch]['ZTTpTTTauTauUp'] = Process("ZTTpTTTauTauUp", AddHistogramEstimationMethod("AddHistogram", "nominal", era, directory, channel_dict[ch], [processes[ch]["EMB"], tttautau_process[ch]], [1.0, 0.1]))
            for category in categories[ch]:
                for updownvar in ["Down", "Up"]:
                    systematics.add(Systematic(category=category, process=processes[ch]['ZTTpTTTauTau%s'%updownvar], analysis="smhtt", era=era, variation=Relabel("CMS_htt_emb_ttbar_Run2017", updownvar), mass="125"))

    # Prefiring weights
    prefiring_variations = [
        ReplaceWeight("CMS_prefiring_Run2017", "prefireWeight", Weight("prefiringweightup", "prefireWeight"),"Up"),
        ReplaceWeight("CMS_prefiring_Run2017", "prefireWeight", Weight("prefiringweightdown", "prefireWeight"),"Down"),
    ]

    # Split JES shapes
    jet_es_variations = create_systematic_variations("CMS_scale_j_Absolute", "jecUncAbsolute", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_Absolute_Run2017", "jecUncAbsoluteYear", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_BBEC1", "jecUncBBEC1", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_BBEC1_Run2017", "jecUncBBEC1Year", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_EC2", "jecUncEC2", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_EC2_Run2017", "jecUncEC2Year", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_FlavorQCD", "jecUncFlavorQCD", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_HF", "jecUncHF", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_HF_Run2017", "jecUncHFYear", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_RelativeBal", "jecUncRelativeBal", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_RelativeSample_Run2017", "jecUncRelativeSampleYear", DifferentPipeline)

    # B-tagging
    btag_eff_variations = create_systematic_variations("CMS_htt_eff_b_Run2017", "btagEff", DifferentPipeline)
    mistag_eff_variations = create_systematic_variations("CMS_htt_mistag_b_Run2017", "btagMistag", DifferentPipeline)

    ## Variations common for all groups (most of the mc-related systematics)
    common_mc_variations = prefiring_variations + btag_eff_variations + mistag_eff_variations + jet_es_variations

    # MET energy scale. Note: only those variations for non-resonant processes are used in the stat. inference
    met_unclustered_variations = create_systematic_variations("CMS_scale_met_unclustered", "metUnclusteredEn", DifferentPipeline)

    # Recoil correction unc, for resonant processes
    recoil_variations = create_systematic_variations( "CMS_htt_boson_reso_met_Run2017", "metRecoilResolution", DifferentPipeline)
    recoil_variations += create_systematic_variations( "CMS_htt_boson_scale_met_Run2017", "metRecoilResponse", DifferentPipeline)

    # Tau energy scale (general, MC-specific & EMB-specific), it is mt, et & tt specific
    tau_es_variations = {}

    for unctype in ["", "_mc", "_emb"]:
        tau_es_variations[unctype] = create_systematic_variations("CMS_scale%s_t_3prong_Run2017"%unctype, "tauEsThreeProng", DifferentPipeline)
        tau_es_variations[unctype] += create_systematic_variations("CMS_scale%s_t_3prong1pizero_Run2017"%unctype, "tauEsThreeProngOnePiZero", DifferentPipeline)
        tau_es_variations[unctype] += create_systematic_variations("CMS_scale%s_t_1prong_Run2017"%unctype, "tauEsOneProng", DifferentPipeline)
        tau_es_variations[unctype] += create_systematic_variations("CMS_scale%s_t_1prong1pizero_Run2017"%unctype, "tauEsOneProngOnePiZero", DifferentPipeline)

    # Tau ID variations (general, MC-specific & EMB specific), it is mt, et & tt specific
    # in et and mt one nuisance per pT bin, in tt per dm
    tau_id_variations = {}
    for ch in ["et" , "mt", "tt"]:
        tau_id_variations[ch] = {}
        for unctype in ["", "_emb"]:
            tau_id_variations[ch][unctype] = []
            if ch in ["et", "mt"]:
                pt = [30, 35, 40, 500, 1000, "inf"]
                for i, ptbin in enumerate(pt[:-1]):
                    bindown = ptbin
                    binup = pt[i+1]
                    if binup == "inf":
                        tau_id_variations[ch][unctype].append(
                                ReplaceWeight("CMS_eff{unctype}_t_{bindown}-{binup}_Run2017".format(unctype=unctype,bindown=bindown, binup=binup), "taubyIsoIdWeight",
                                    Weight("(((pt_2 >= {bindown})*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < {bindown})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))".format(bindown=bindown), "taubyIsoIdWeight"), "Up"))
                        tau_id_variations[ch][unctype].append(
                                ReplaceWeight("CMS_eff{unctype}_t_{bindown}-{binup}_Run2017".format(unctype=unctype, bindown=bindown, binup=binup), "taubyIsoIdWeight",
                                    Weight("(((pt_2 >= {bindown})*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < {bindown})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))".format(bindown=bindown),"taubyIsoIdWeight"), "Down"))
                    else:
                        tau_id_variations[ch][unctype].append(
                                ReplaceWeight("CMS_eff{unctype}_t_{bindown}-{binup}_Run2017".format(unctype=unctype, bindown=bindown, binup=binup), "taubyIsoIdWeight",
                                    Weight("(((pt_2 >= {bindown} && pt_2 <= {binup})*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < {bindown} || pt_2 > {binup})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))".format(bindown=bindown, binup=binup),"taubyIsoIdWeight"), "Up"))
                        tau_id_variations[ch][unctype].append(
                                ReplaceWeight("CMS_eff{unctype}_t_{bindown}-{binup}_Run2017".format(unctype=unctype, bindown=bindown, binup=binup), "taubyIsoIdWeight",
                                    Weight("(((pt_2 >= {bindown} && pt_2 <= {binup})*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < {bindown} || pt_2 > {binup})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))".format(bindown=bindown, binup=binup),"taubyIsoIdWeight"), "Down"))
            if ch in ["tt"]:
                for decaymode in [0, 1, 10, 11]:
                    tau_id_variations[ch][unctype].append(
                                ReplaceWeight("CMS_eff{unctype}_t_dm{dm}_Run2017".format(unctype=unctype, dm=decaymode), "taubyIsoIdWeight",
                                    Weight("(((decayMode_1=={dm})*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!={dm})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1)*((decayMode_2=={dm})*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!={dm})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))".format(dm=decaymode), "taubyIsoIdWeight"), "Up"))
                    tau_id_variations[ch][unctype].append(
                                ReplaceWeight("CMS_eff{unctype}_t_dm{dm}_Run2017".format(unctype=unctype, dm=decaymode), "taubyIsoIdWeight",
                                    Weight("(((decayMode_1=={dm})*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!={dm})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1)*((decayMode_2=={dm})*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!={dm})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))".format(dm=decaymode), "taubyIsoIdWeight"), "Down"))

    # Ele energy scale & smear uncertainties (MC-specific), it is et & em specific
    ele_es_variations = create_systematic_variations("CMS_scale_mc_e", "eleScale", DifferentPipeline)
    ele_es_variations += create_systematic_variations("CMS_reso_mc_e", "eleSmear", DifferentPipeline)
    # Ele energy scale (EMB-specific), it is et & em specific
    ele_es_emb_variations = create_systematic_variations("CMS_scale_emb_e", "eleEs", DifferentPipeline)

    # Z pt reweighting
    zpt_variations = create_systematic_variations("CMS_htt_dyShape_Run2017", "zPtReweightWeight", SquareAndRemoveWeight)

    # top pt reweighting
    top_pt_variations = create_systematic_variations("CMS_htt_ttbarShape", "topPtReweightWeight", SquareAndRemoveWeight)


    # EMB charged track correction uncertainty (DM-dependent)
    decayMode_variations = []
    decayMode_variations.append(ReplaceWeight("CMS_3ProngEff_Run2017", "decayMode_SF", Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"), "Up"))
    decayMode_variations.append(ReplaceWeight("CMS_3ProngEff_Run2017", "decayMode_SF", Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"), "Down"))
    decayMode_variations.append(ReplaceWeight("CMS_1ProngPi0Eff_Run2017", "decayMode_SF", Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"), "Up"))
    decayMode_variations.append(ReplaceWeight("CMS_1ProngPi0Eff_Run2017", "decayMode_SF", Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"), "Down"))

    # QCD for em
    qcd_variations = []
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_0jet_rate_Run2017", "qcd_weight", Weight("em_qcd_osss_0jet_rateup_Weight", "qcd_weight"), "Up"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_0jet_rate_Run2017", "qcd_weight", Weight("em_qcd_osss_0jet_ratedown_Weight", "qcd_weight"), "Down"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_0jet_shape_Run2017", "qcd_weight", Weight("em_qcd_osss_0jet_shapeup_Weight", "qcd_weight"), "Up"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_0jet_shape_Run2017", "qcd_weight", Weight("em_qcd_osss_0jet_shapedown_Weight", "qcd_weight"), "Down"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_1jet_rate_Run2017", "qcd_weight", Weight("em_qcd_osss_1jet_rateup_Weight", "qcd_weight"), "Up"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_1jet_rate_Run2017", "qcd_weight", Weight("em_qcd_osss_1jet_ratedown_Weight", "qcd_weight"), "Down"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_1jet_shape_Run2017", "qcd_weight", Weight("em_qcd_osss_1jet_shapeup_Weight", "qcd_weight"), "Up"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_1jet_shape_Run2017", "qcd_weight", Weight("em_qcd_osss_1jet_shapedown_Weight", "qcd_weight"), "Down"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_iso_Run2017", "qcd_weight", Weight("em_qcd_extrap_up_Weight", "qcd_weight"), "Up"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_iso_Run2017", "qcd_weight", Weight("em_qcd_extrap_down_Weight", "qcd_weight"), "Down"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_iso", "qcd_weight", Weight("em_qcd_extrap_up_Weight", "qcd_weight"), "Up"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_iso", "qcd_weight", Weight("em_qcd_extrap_down_Weight", "qcd_weight"), "Down"))

    # Gluon-fusion WG1 uncertainty scheme
    ggh_variations = []
    for unc in [
            "THU_ggH_Mig01", "THU_ggH_Mig12", "THU_ggH_Mu", "THU_ggH_PT120",
            "THU_ggH_PT60", "THU_ggH_Res", "THU_ggH_VBF2j", "THU_ggH_VBF3j",
            "THU_ggH_qmtop"
    ]:
        ggh_variations.append(AddWeight(unc, "{}_weight".format(unc), Weight("({})".format(unc), "{}_weight".format(unc)), "Up"))
        ggh_variations.append(AddWeight(unc, "{}_weight".format(unc), Weight("(2.0-{})".format(unc), "{}_weight".format(unc)), "Down"))

    # ZL fakes energy scale
    fakelep_dict = {"et" : "Ele", "mt" : "Mu"}
    lep_fake_es_variations = {}
    for ch in ["mt", "et"]:
        lep_fake_es_variations[ch] = create_systematic_variations("CMS_ZLShape_%s_1prong_Run2017"%ch, "tau%sFakeEsOneProng"%fakelep_dict[ch], DifferentPipeline)
        lep_fake_es_variations[ch] += create_systematic_variations("CMS_ZLShape_%s_1prong1pizero_Run2017"%ch, "tau%sFakeEsOneProngPiZeros"%fakelep_dict[ch], DifferentPipeline)

    # Lepton trigger efficiency; the same values for (MC & EMB) and (mt & et)
    lep_trigger_eff_variations = {}
    for ch in ["mt", "et"]:
        lep_trigger_eff_variations[ch] = {}
        thresh_dict = {"mt": 23., "et": 28.}
        for unctype in ["", "_emb"]:
            lep_trigger_eff_variations[ch][unctype] = []
            lep_trigger_eff_variations[ch][unctype].append(AddWeight("CMS_eff_trigger%s_%s_Run2017"%(unctype, ch), "trg_%s_eff_weight"%ch, Weight("(1.0*(pt_1<={0})+1.02*(pt_1>{0}))".format(thresh_dict[ch]), "trg_%s_eff_weight"%ch), "Up"))
            lep_trigger_eff_variations[ch][unctype].append(AddWeight("CMS_eff_trigger%s_%s_Run2017"%(unctype, ch), "trg_%s_eff_weight"%ch, Weight("(1.0*(pt_1<={0})+0.98*(pt_1>{0}))".format(thresh_dict[ch]), "trg_%s_eff_weight"%ch), "Down"))
            lep_trigger_eff_variations[ch][unctype].append(AddWeight("CMS_eff_xtrigger%s_%s_Run2017"%(unctype, ch), "xtrg_%s_eff_weight"%ch, Weight("(1.054*(pt_1<={0})+1.0*(pt_1>{0}))".format(thresh_dict[ch]), "xtrg_%s_eff_weight"%ch), "Up"))
            lep_trigger_eff_variations[ch][unctype].append(AddWeight("CMS_eff_xtrigger%s_%s_Run2017"%(unctype, ch), "xtrg_%s_eff_weight"%ch, Weight("(0.946*(pt_1<={0})+1.0*(pt_1>{0}))".format(thresh_dict[ch]), "xtrg_%s_eff_weight"%ch), "Down"))

    # Fake factor uncertainties
    fake_factor_variations = {}
    for ch in ["mt", "et", "tt"]:
        fake_factor_variations[ch] = []
        if ch in ["mt", "et"]:
            for systematic_shift in [
                    "ff_qcd{ch}_syst_Run2017{shift}",
                    "ff_qcd_dm0_njet0{ch}_stat_Run2017{shift}",
                    "ff_qcd_dm0_njet1{ch}_stat_Run2017{shift}",
                    "ff_w_syst_Run2017{shift}",
                    "ff_w_dm0_njet0{ch}_stat_Run2017{shift}",
                    "ff_w_dm0_njet1{ch}_stat_Run2017{shift}",
                    "ff_tt_syst_Run2017{shift}",
                    "ff_tt_dm0_njet0_stat_Run2017{shift}",
                    "ff_tt_dm0_njet1_stat_Run2017{shift}",
            ]:
                for shift_direction in ["Up", "Down"]:
                    fake_factor_variations[ch].append(ReplaceWeight("CMS_%s"%(systematic_shift.format(ch="_"+ch, shift="").replace("_dm0", "")), "fake_factor", Weight("ff2_{syst}".format(syst=systematic_shift.format(ch="", shift="_%s" %shift_direction.lower()).replace("_Run2017", "")), "fake_factor"), shift_direction))
        elif ch == "tt":
            for systematic_shift in [
                    "ff_qcd{ch}_syst_Run2017{shift}",
                    "ff_qcd_dm0_njet0{ch}_stat_Run2017{shift}",
                    "ff_qcd_dm0_njet1{ch}_stat_Run2017{shift}",
                    "ff_w{ch}_syst_Run2017{shift}", "ff_tt{ch}_syst_Run2017{shift}",
                    "ff_w_frac{ch}_syst_Run2017{shift}",
                    "ff_tt_frac{ch}_syst_Run2017{shift}"
            ]:
                for shift_direction in ["Up", "Down"]:
                    fake_factor_variations[ch].append(ReplaceWeight("CMS_%s" % (systematic_shift.format(ch="_"+ch, shift="").replace("_dm0", "")), "fake_factor", Weight("(0.5*ff1_{syst}*(byTightDeepTau2017v2p1VSjet_1<0.5)+0.5*ff2_{syst}*(byTightDeepTau2017v2p1VSjet_2<0.5))".format(syst=systematic_shift.format(ch="", shift="_%s" % shift_direction.lower()).replace("_Run2017", "")), "fake_factor"), shift_direction))

    ## Group nicks
    mc_nicks = ["ZL", "TTL", "VVL"] + signal_nicks # to be extended with 'W' in em
    boson_mc_nicks = ["ZL"]         + signal_nicks # to be extended with 'W' in em

    ## Add variations to systematics
    for ch in args.channels:

        channel_mc_nicks = mc_nicks + ["W"] if ch == "em" else mc_nicks
        channel_boson_mc_nicks = boson_mc_nicks + ["W"] if ch == "em" else boson_mc_nicks
        if args.shape_group != "backgrounds":
            channel_mc_nicks = signal_nicks
            channel_boson_mc_nicks = signal_nicks

        channel_mc_common_variations = common_mc_variations
        if ch in ["et", "em"]:
            channel_mc_common_variations += ele_es_variations
        if ch in ["et", "mt", "tt"]:
            channel_mc_common_variations += tau_es_variations[""] + tau_es_variations["_mc"] + tau_id_variations[ch][""]
        if ch in ["et", "mt"]:
            channel_mc_common_variations += lep_trigger_eff_variations[ch][""]

        # variations common accross all shape groups
        for variation in channel_mc_common_variations:
            for process_nick in channel_mc_nicks:
                systematics.add_systematic_variation(variation=variation, process=processes[ch][process_nick], channel=channel_dict[ch], era=era)

        for variation in recoil_variations:
            for process_nick in channel_boson_mc_nicks:
                systematics.add_systematic_variation(variation=variation, process=processes[ch][process_nick], channel=channel_dict[ch], era=era)

        # variations relevant for ggH signals in 'sm_signals' shape group
        if args.shape_group == "sm_signals":
            for variation in ggh_variations:
                for process_nick in [nick for nick in signal_nicks if "ggH" in nick and "HWW" not in nick and "ggH_" not in nick]:
                    systematics.add_systematic_variation(variation=variation, process=processes[ch][process_nick], channel=channel_dict[ch], era=era)

        # variations only relevant for the 'background' shape group
        if args.shape_group == "backgrounds":
            for variation in top_pt_variations:
                # TODO: Needs to be adapted if one wants to use DY MC or QCD estimation(lt,tt: TTT, TTL, TTJ, em: TTT, TTL)
                systematics.add_systematic_variation(variation=variation, process=processes[ch]["TTL"], channel=channel_dict[ch], era=era)

            for variation in met_unclustered_variations:
                    for process_nick in ["TTL", "VVL"]:
                        systematics.add_systematic_variation(variation=variation, process=processes[ch][process_nick], channel=channel_dict[ch], era=era)

            zl_variations = zpt_variations
            if ch in ["et", "mt"]:
                zl_variations += lep_fake_es_variations[ch]
            # TODO: maybe prepare variations for shape production with DY MC and QCD estimation, then applied to ZTT, ZL and ZJ for lt channels and ZTT and ZL for em channel
            for variation in zl_variations:
                systematics.add_systematic_variation(variation=variation, process=processes[ch]["ZL"], channel=channel_dict[ch], era=era)

            if ch == "em":
                for variation in qcd_variations:
                    systematics.add_systematic_variation(variation=variation ,process=processes[ch]["QCD"], channel=channel_dict[ch], era=era)

            if ch in ["mt","et", "tt"]:
                ff_variations = fake_factor_variations[ch] + tau_es_variations[""] + tau_es_variations["_mc"] + tau_es_variations["_emb"]
                for variation in ff_variations:
                    systematics.add_systematic_variation(variation=variation, process=processes[ch]["FAKES"], channel=channel_dict[ch], era=era)

            emb_variations = []
            if ch in ["mt","et", "tt"]:
                emb_variations += tau_es_variations[""] + tau_es_variations["_emb"] + tau_id_variations[ch]["_emb"] + decayMode_variations
            if ch in ["mt", "et"]:
                emb_variations += lep_trigger_eff_variations[ch]["_emb"]
            if ch in ["et", "em"]:
                emb_variations += ele_es_emb_variations
            for variation in emb_variations:
                systematics.add_systematic_variation(variation=variation, process=processes[ch]["EMB"], channel=channel_dict[ch], era=era)

    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_produce_cutbased_shapes_{}.log".format(args.tag, args.discriminator_variable), logging.INFO)
    main(args)
