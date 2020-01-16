#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import yaml
import argparse
from itertools import product
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.process import Process
from shape_producer.systematic_variations import Nominal, DifferentPipeline, SquareAndRemoveWeight, create_systematic_variations, AddWeight, ReplaceWeight, Relabel
from shape_producer.variable import Variable
from shape_producer.binning import ConstantBinning, VariableBinning
from shape_producer.categories import Category
from shape_producer.systematics import Systematics, Systematic
from shape_producer.cutstring import Cut, Cuts, Weight
import ROOT
# disable ROOT internal argument parser
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gErrorIgnoreLevel = ROOT.kError


logger = logging.getLogger()


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
        description="Produce shapes for Standard Model analysis.")

    parser.add_argument("--directory",
                        required=True,
                        type=str,
                        help="Directory with Artus outputs.")
    parser.add_argument(
        "--et-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help="Directories arranged as Artus output and containing a friend tree for et."
    )
    parser.add_argument(
        "--mt-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help="Directories arranged as Artus output and containing a friend tree for mt."
    )
    parser.add_argument(
        "--fake-factor-friend-directory",
        default=None,
        type=str,
        help="Directory arranged as Artus output and containing friend trees to data files with fake factors."
    )
    parser.add_argument(
        "--tt-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help="Directories arranged as Artus output and containing a friend tree for tt."
    )
    parser.add_argument(
        "--em-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help="Directories arranged as Artus output and containing a friend tree for em."
    )
    parser.add_argument(
        "--QCD-extrap-fit",
        default=False,
        action='store_true',
        help="Create shapes for QCD extrapolation factor determination.")
    parser.add_argument("--datasets",
                        required=True,
                        type=str,
                        help="Kappa datsets database.")
    parser.add_argument("--binning",
                        required=True,
                        type=str,
                        help="Binning configuration.")
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist:
        [channel for channel in channellist.split(',')],
        help="Channels to be considered, seperated by a comma without space")
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument("--gof-channel",
                        default=None,
                        type=str,
                        help="Channel for goodness of fit shapes.")
    parser.add_argument("--gof-variable",
                        type=str,
                        help="Variable for goodness of fit shapes.")
    parser.add_argument("--num-threads",
                        default=10,
                        type=int,
                        help="Number of threads to be used.")
    parser.add_argument("--backend",
                        default="classic",
                        choices=["classic", "tdf"],
                        type=str,
                        help="Backend. Use classic or tdf.")
    parser.add_argument("--tag",
                        default="ERA_CHANNEL",
                        type=str,
                        help="Tag of output files.")
    parser.add_argument("--skip-systematic-variations",
                        default=False,
                        type=str,
                        help="Do not produce the systematic variations.")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    logger.info(str(args))
    logger.info("Set up shape variations.")
    systematics = Systematics(
        "output/shapes/{ERA}-{TAG}-{CHANNELS}-shapes.root".format(
            ERA=args.era, TAG=args.tag, CHANNELS=",".join(args.channels)),
        num_threads=args.num_threads,
        skip_systematic_variations=args.skip_systematic_variations)

    # Era selection
    if "2016" in args.era:
        from shape_producer.channel import ETSM2016, MTSM2016, TTSM2016, EMSM2016
        smChannelsDict = {
            "et": ETSM2016,
            "mt": MTSM2016,
            "tt": TTSM2016,
            "em": EMSM2016
        }
        from shape_producer.estimation_methods_2016 import DataEstimation, HTTEstimation, ggHEstimation, qqHEstimation, VHEstimation, WHEstimation, ZHEstimation, ttHEstimation, ZTTEstimation, ZLEstimation, ZJEstimation, WEstimation, VVLEstimation, VVTEstimation, VVJEstimation, TTLEstimation, TTTEstimation, TTJEstimation, QCDEstimation_SStoOS_MTETEM, QCDEstimationTT, ZTTEmbeddedEstimation, FakeEstimationLT, NewFakeEstimationLT, FakeEstimationTT, NewFakeEstimationTT, ggHWWEstimation, qqHWWEstimation
        from shape_producer.era import Run2016
        era = Run2016(args.datasets)
    elif "2017" in args.era:
        from shape_producer.channel import ETSM2017, MTSM2017, TTSM2017, EMSM2017
        smChannelsDict = {
            "et": ETSM2017,
            "mt": MTSM2017,
            "tt": TTSM2017,
            "em": EMSM2017
        }
        from shape_producer.estimation_methods_2017 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, qqHEstimation, VHEstimation, WHEstimation, ZHEstimation, ttHEstimation, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, NewFakeEstimationLT, NewFakeEstimationTT, HWWEstimation, ggHWWEstimation, qqHWWEstimation

        from shape_producer.era import Run2017
        era = Run2017(args.datasets)
    elif "2018" in args.era:
        from shape_producer.channel import ETSM2018, MTSM2018, TTSM2018, EMSM2018
        smChannelsDict = {
            "et": ETSM2018,
            "mt": MTSM2018,
            "tt": TTSM2018,
            "em": EMSM2018
        }
        from shape_producer.estimation_methods_2018 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, qqHEstimation, VHEstimation, WHEstimation, ZHEstimation, ttHEstimation, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, NewFakeEstimationLT, NewFakeEstimationTT

        from shape_producer.era import Run2018
        era = Run2018(args.datasets)

    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # Channels and processes
    # yapf: disable
    directory = args.directory
    friend_directory = {
        "mt": args.mt_friend_directory,
        "et": args.et_friend_directory,
        "tt": args.tt_friend_directory,
        "em": args.em_friend_directory}

    # QCD extrapolation_factor 1.17 for mt et 2016
    if args.era == "2016":
        extrapolation_factor = 1.17
    else:
        extrapolation_factor = 1.
    mt = smChannelsDict["mt"]
    et = smChannelsDict["et"]
    tt = smChannelsDict["tt"]
    em = smChannelsDict["em"]
    if args.QCD_extrap_fit:
        mt.cuts.remove("muon_iso")
        mt.cuts.add(Cut("(iso_1<0.5)*(iso_1>=0.15)", "muon_iso_loose"))
        et.cuts.remove("ele_iso")
        et.cuts.add(Cut("(iso_1<0.5)*(iso_1>=0.1)", "ele_iso_loose"))
        tt.cuts.get("os").invert()
        em.cuts.get("os").invert()

    pnameToEstD = {
        "data_obs": DataEstimation,
        "EMB": ZTTEmbeddedEstimation,
        "TTT": TTTEstimation,
        "VVT": VVTEstimation,
        "ZTT": ZTTEstimation,
        "TTL": TTLEstimation,
        "VVL": VVLEstimation,
        "ZL": ZLEstimation,
        "W": WEstimation,
        "VVJ": VVJEstimation,
        "TTJ": TTJEstimation,
        "ZJ": ZJEstimation,
        "VH125": VHEstimation,
        "WH125": WHEstimation,
        "ZH125": ZHEstimation,
        "ttH125": ttHEstimation,
        "ggHWW125": ggHWWEstimation,
        "qqHWW125": qqHWWEstimation,
    }
    bac
    commonProcessesL = [
        "data",
        "EMB",
        "ZL",
        "TTL",
        "VVL",
        "VH125",
        "WH125",
        "ZH125",
        "ttH125",
        "ggHWW125",
        "qqHWW125"]
    allChannelNameList = ["mt", "et", "tt", "em"]
    processesToAdd = {}
    for channelname_ in allChannelNameList:
        processesToAdd[channelname_] = channelname_

    processes = {}
    for channelname_, ch_ in smChannelsDict.items():
        # Add all processes, than dont
        processes[channelname_] = {
            processname: Process(
                processname,
                pnameToEstD[processname](
                    era,
                    directory,
                    ch_,
                    friend_directory=friend_directory[channelname_])) for processname in commonProcessesL}
        # Stage 0 and 1.1 signals for ggH & qqH
        for ggH_htxs in ggHEstimation.htxs_dict:
            processes[ggH_htxs] = Process(
                ggH_htxs,
                ggHEstimation(
                    ggH_htxs, era, directory, ch_,
                    friend_directory=friend_directory[channelname_]))
        for qqH_htxs in qqHEstimation.htxs_dict:
            processes[qqH_htxs] = Process(
                qqH_htxs,
                qqHEstimation(
                    qqH_htxs, era, directory, ch_,
                    friend_directory=friend_directory[channelname_]))

    for channelname_, ch_ in smChannelsDict.items():
        catsL_ = catsListD[channelname_]

        fpL = ["EMB", "ZL", "TTL", "VVL"]
        if channelname_ == "em":
            fpL.append("W")

        processes[channelname_]["FAKES"] = Process(
            "jetFakes",
            NewFakeEstimationLT(
                era, directory, ch_,
                [processes[channelname_][process] for process in fpl],
                processes[channelname_]["data"],
                friend_directory=friend_directory[channelname_] +
                [args.fake_factor_friend_directory]))

        if channelname_ != "em":
            qcdpL = ["EMB", "ZL", "ZJ", "W", "TTJ", "TTL", "VVJ", "VVL"]
            qcd_weight = Weight("1", "qcd_weight")
        else:
            qcdpL = ["EMB", "ZL", "W", "TTL", "VVL"]
            qcd_weight = Weight("em_qcd_osss_binned_Weight", "qcd_weight")

        if channelname_ != "tt":
            est_ = QCDEstimation_SStoOS_MTETEM
        else:
            est_ = QCDEstimation_ABCD_TT_ISO2

        processes[channelname_]["QCD"] = Process(
            "QCD",
            QCDEstimation_SStoOS_MTETEM(
                era, directory, ch_,
                [processes[channelname_][process] for process in qcdpL],
                processes[channelname_]["data"],
                friend_directory=friend_directory[channelname_],
                extrapolation_factor=extrapolation_factor))

    # Variables and categories
    binning = yaml.load(open(args.binning), Loader=yaml.Loader)

    def readclasses(channelname):
        import os
        if args.tag == "" or args.tag is None or not os.path.isfile(
                "output/ml/{}_{}_{}/dataset_config.yaml".format(args.era, channelname, args.tag)):
            logger.warn("No tag given, using template.")
            confFileName = "ml/templates/shape-producer_{}.yaml".format(
                channelname)
        else:
            confFileName = "output/ml/{}_{}_{}/dataset_config.yaml".format(
                args.era, channelname, args.tag)
        logger.debug("Parse classes from " + confFileName)
        confdict = yaml.load(open(confFileName, "r"))
        logger.debug(
            "Classes for {} loaded: {}".format(
                channelname, str(
                    confdict["classes"])))
        return confdict["classes"]

    # Initialise categorie lists
    selelctedChannelsTuples = {
        c_: smChannelsDict[c_] for c_ in args.channels}.items()
    selelctedChannelsTuplesNoEM = {
        c_: smChannelsDict[c_] for c_ in args.channels if c_ != em}.items()
    catsListD = {channelname_: [] for channelname_ in allChannelNameList}
    # if not a gof test:Analysis shapes
    if args.gof_variable is None:
        for channelname_, ch_ in selelctedChannelsTuples:
            catsL_ = catsListD[channelname_]
            for i, label in enumerate(readclasses(channelname_)):
                score = Variable(
                    "{}_max_score".format(channelname_),
                    VariableBinning(binning["analysis"][channelname_][label]))
                maxIdxCut = Cut(
                    "{channel}_max_index=={index}".format(
                        channel=channelname_,
                        index=i),
                    "exclusive_score")
                catsL_.append(
                    Category(
                        label,
                        ch_,
                        Cuts(maxIdxCut),
                        variable=score))
                if label in ["ggh", "qqh"]:
                    stxs = 100 if label == "ggh" else 200
                    for i_e, e in enumerate(binning["stxs_stage1p1"][label]):
                        score = Variable(
                            "{}_max_score".format(channelname_), VariableBinning(
                                binning["analysis"][channelname_][label]))
                        catsL_.append(
                            Category(
                                "{}_{}".format(label, str(stxs + i_e)),
                                ch_,
                                Cuts(maxIdxCut,
                                     Cut(e, "stxs_stage1p1_cut")),
                                variable=score))

    # if gof test
    else:
        # Goodness of fit shapes
        for channelname_, ch_ in selelctedChannelsTuples:
            catsL_ = catsListD[channelname_]
            score = Variable(args.gof_variable,
                             VariableBinning(
                                 binning["gof"][channelname_]
                                 [args.gof_variable]["bins"]),
                             expression=binning["gof"][channelname_]
                             [args.gof_variable]["expression"])
            if "cut" in binning["gof"][channelname_][args.gof_variable].keys():
                cuts = Cuts(
                    Cut(binning["gof"][channelname_][args.gof_variable]["cut"], "binning"))
            else:
                cuts = Cuts()
            catsL_.append(
                Category(
                    args.gof_variable,
                    ch_,
                    cuts,
                    variable=score))

    # Nominal histograms
    signal_nicks = ["WH125", "ZH125", "VH125", "ttH125"]
    ww_nicks = []  # ["ggHWW125", "qqHWW125"]
    if args.gof_variable is None:
        signal_nicks += [ggH_htxs for ggH_htxs in ggHEstimation.htxs_dict] + [
            qqH_htxs for qqH_htxs in qqHEstimation.htxs_dict] + ww_nicks
    else:
        signal_nicks += ["ggH125", "qqH125"] + ww_nicks

    # yapf: enable
    for channelname_, ch_ in selelctedChannelsTuples:
        catsL_ = catsListD[channelname_]
        processL_ = processes[channelname_]
        for process, category in product(processL_.values(), catsL_):
            systematics.add(
                Systematic(category=category,
                           process=process,
                           analysis="smhtt",
                           era=era,
                           variation=Nominal(),
                           mass="125"))

    # Shapes variations
    variationsTooAdd = {
        channelname_:
        {process_nick: []
         for process_nick in processes[channelname_]}
        for channelname_, _ in selelctedChannelsTuples
    }
    # end
    for channelname_, ch_ in selelctedChannelsTuples:
        for process_nick in processes[channelname_]:
            for variation_ in variationsTooAdd[channelname_][process_nick]:
                systematics.add_systematic_variation(
                    variation=variation__,
                    process=processes[channelname_][process_nick],
                    channel=ch_,
                    era=era)
    # MC tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_mc_t_3prong_Run{era}".format(era=args.era),
        "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_mc_t_1prong_Run{era}".format(era=args.era), "tauEsOneProng",
        DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_mc_t_1prong1pizero_Run{era}".format(era=args.era),
        "tauEsOneProngOnePiZero", DifferentPipeline)
    for variation_ in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["ZTT", "TTT", "TTL", "VVL", "VVT", "FAKES"
                             ] + signal_nicks:
            for channelname_, _ in selelctedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # Tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_t_3prong_Run{era}".format(era=args.era), "tauEsThreeProng",
        DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_t_1prong_Run{era}".format(era=args.era), "tauEsOneProng",
        DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_t_1prong1pizero_Run{era}".format(era=args.era),
        "tauEsOneProngOnePiZero", DifferentPipeline)
    for variation_ in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in [
                "ZTT", "TTT", "TTL", "VVT", "VVL", "EMB", "FAKES"
        ] + signal_nicks:
            for channelname_, _ in selelctedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # MC ele energy scale & smear uncertainties
    ele_es_variations = create_systematic_variations("CMS_scale_mc_e",
                                                     "eleScale",
                                                     DifferentPipeline)
    ele_es_variations += create_systematic_variations("CMS_reso_mc_e",
                                                      "eleSmear",
                                                      DifferentPipeline)
    for variation_ in ele_es_variations:
        for channelname_, process_nick in {
                "et":
            ["ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVL", "VVT", "VVJ"
             ] + signal_nicks,
                "em":
            ["ZTT", "ZL", "W", "TTT", "TTL", "VVL", "VVT"] + signal_nicks
        }.items():
            variationsTooAdd[channelname_][process_nick].append(variation_)

    # Jet energy scale

    # Inclusive JES shapes
    jet_es_variations = []
    '''jet_es_variations += create_systematic_variations(
        "CMS_scale_j_Run{era}".format(era=args.era), "jecUnc", DifferentPipeline)'''

    # Splitted JES shapes
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta0to3_Run{era}".format(era=args.era), "jecUncEta0to3",
        DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta0to5_Run{era}".format(era=args.era), "jecUncEta0to5",
        DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_eta3to5_Run{era}".format(era=args.era), "jecUncEta3to5",
        DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeBal_Run{era}".format(era=args.era),
        "jecUncRelativeBal", DifferentPipeline)
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeSample_Run{era}".format(era=args.era),
        "jecUncRelativeSample", DifferentPipeline)

    for variation_ in jet_es_variations:
        for process_nick in [
                "ZTT",
                "ZL",
                "ZJ",
                "W",
                "TTT",
                "TTL",
                "TTJ",
                "VVT",
                "VVJ",
                "VVL",
        ] + signal_nicks:
            for channelname_, _ in selelctedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)
        for process_nick in ["ZTT", "ZL", "W", "TTT", "TTL", "VVL", "VVT"
                             ] + signal_nicks:
            if "em" in args.channels:
                variationsTooAdd["em"][process_nick].append(variation_)

    # MET energy scale. Note: only those variations for non-resonant processes
    # are used in the stat. inference
    met_unclustered_variations = create_systematic_variations(
        "CMS_scale_met_unclustered", "metUnclusteredEn", DifferentPipeline)
    for variation_ in met_unclustered_variations:  # + met_clustered_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVJ",
                "VVL"
        ] + signal_nicks:
            for channelname_, _ in selelctedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)
        for process_nick in ["ZTT", "ZL", "W", "TTT", "TTL", "VVL", "VVT"
                             ] + signal_nicks:
            variationsTooAdd["em"][process_nick].append(variation_)

    # Recoil correction unc
    recoil_resolution_variations = create_systematic_variations(
        "CMS_htt_boson_reso_met_Run{era}".format(era=args.era),
        "metRecoilResolution", DifferentPipeline)
    recoil_response_variations = create_systematic_variations(
        "CMS_htt_boson_scale_met_Run{era}".format(era=args.era),
        "metRecoilResponse", DifferentPipeline)
    for variation_ in recoil_resolution_variations + recoil_response_variations:
        for process_nick in ["ZTT", "ZL", "ZJ", "W"] + signal_nicks:
            for channelname_, _ in selelctedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)
        for process_nick in ["ZTT", "ZL", "W"] + signal_nicks:
            if "em" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # Z pt reweighting
    zpt_variations = create_systematic_variations(
        "CMS_htt_dyShape_Run{era}".format(era=args.era), "zPtReweightWeight",
        SquareAndRemoveWeight)
    for variation_ in zpt_variations:
        for process_nick in ["ZTT", "ZL", "ZJ"]:
            for channelname_, _ in selelctedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)
        for process_nick in ["ZTT", "ZL"]:
            if "em" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # top pt reweighting
    top_pt_variations = create_systematic_variations("CMS_htt_ttbarShape",
                                                     "topPtReweightWeight",
                                                     SquareAndRemoveWeight)
    for variation_ in top_pt_variations:
        for process_nick in ["TTT", "TTL", "TTJ"]:
            for channelname_, _ in selelctedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)
        for process_nick in ["TTT", "TTL"]:
            if "em" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # jet to tau fake efficiency
    jet_to_tau_fake_variations = []
    jet_to_tau_fake_variations.append(
        AddWeight("CMS_htt_jetToTauFake_Run{era}".format(era=args.era),
                  "jetToTauFake_weight",
                  Weight("max(1.0-pt_2*0.002, 0.6)",
                         "jetToTauFake_weight"), "Up"))
    jet_to_tau_fake_variations.append(
        AddWeight("CMS_htt_jetToTauFake_Run{era}".format(era=args.era),
                  "jetToTauFake_weight",
                  Weight("min(1.0+pt_2*0.002, 1.4)",
                         "jetToTauFake_weight"), "Down"))
    for variation_ in jet_to_tau_fake_variations:
        for process_nick in ["ZJ", "TTJ", "W", "VVJ"]:
            for channelname_, _ in selelctedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # ZL fakes energy scale
    ele_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_et_1prong_Run{era}".format(era=args.era),
        "tauEleFakeEsOneProng", DifferentPipeline)
    ele_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_et_1prong1pizero_Run{era}".format(era=args.era),
        "tauEleFakeEsOneProngPiZeros", DifferentPipeline)

    if "et" in args.channels:
        for process_nick in ["ZL"]:
            for variation_ in ele_fake_es_1prong_variations + ele_fake_es_1prong1pizero_variations:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)

    mu_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong_Run{era}".format(era=args.era),
        "tauMuFakeEsOneProng", DifferentPipeline)
    mu_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong1pizero_Run{era}".format(era=args.era),
        "tauMuFakeEsOneProngPiZeros", DifferentPipeline)

    if "mt" in args.channels:
        for process_nick in ["ZL"]:
            for variation_ in mu_fake_es_1prong_variations + mu_fake_es_1prong1pizero_variations:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)

    # lepton trigger efficiency
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_trigger_mt_Run{era}".format(era=args.era),
            "trg_mt_eff_weight",
            Weight("(1.0*(pt_1<=25)+1.02*(pt_1>25))",
                   "trg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_trigger_mt_Run{era}".format(era=args.era),
            "trg_mt_eff_weight",
            Weight("(1.0*(pt_1<=25)+0.98*(pt_1>25))",
                   "trg_mt_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_xtrigger_mt_Run{era}".format(era=args.era),
            "xtrg_mt_eff_weight",
            Weight("(1.054*(pt_1<=25)+1.0*(pt_1>25))",
                   "xtrg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_xtrigger_mt_Run{era}".format(era=args.era),
            "xtrg_mt_eff_weight",
            Weight("(0.946*(pt_1<=25)+1.0*(pt_1>25))",
                   "xtrg_mt_eff_weight"), "Down"))
    for variation_ in lep_trigger_eff_variations:
        for process_nick in [
                "ZTT",
                "ZL",
                "ZJ",
                "W",
                "TTT",
                "TTL",
                "TTJ",
                "VVL",
                "VVT",
                "VVJ",
        ] + signal_nicks:
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_trigger_emb_mt_Run{era}".format(era=args.era),
            "trg_mt_eff_weight",
            Weight("(1.0*(pt_1<=25)+1.02*(pt_1>25))",
                   "trg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_trigger_emb_mt_Run{era}".format(era=args.era),
            "trg_mt_eff_weight",
            Weight("(1.0*(pt_1<=25)+0.98*(pt_1>25))",
                   "trg_mt_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_xtrigger_emb_mt_Run{era}".format(era=args.era),
            "xtrg_mt_eff_weight",
            Weight("(1.054*(pt_1<=25)+1.0*(pt_1>25))",
                   "xtrg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_xtrigger_emb_mt_Run{era}".format(era=args.era),
            "xtrg_mt_eff_weight",
            Weight("(0.946*(pt_1<=25)+1.0*(pt_1>25))",
                   "xtrg_mt_eff_weight"), "Down"))
    for variation_ in lep_trigger_eff_variations:
        for process_nick in ["EMB"]:
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_trigger_et_Run{era}".format(era=args.era),
            "trg_et_eff_weight",
            Weight("(1.0*(pt_1<=28)+1.02*(pt_1>28))",
                   "trg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_trigger_et_Run{era}".format(era=args.era),
            "trg_et_eff_weight",
            Weight("(1.0*(pt_1<=28)+0.98*(pt_1>28))",
                   "trg_et_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_xtrigger_et_Run{era}".format(era=args.era),
            "xtrg_et_eff_weight",
            Weight("(1.054*(pt_1<=28)+1.0*(pt_1>28))",
                   "xtrg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_xtrigger_et_Run{era}".format(era=args.era),
            "xtrg_et_eff_weight",
            Weight("(0.946*(pt_1<=28)+1.0*(pt_1>28))",
                   "xtrg_et_eff_weight"), "Down"))
    for variation_ in lep_trigger_eff_variations:
        for process_nick in [
                "ZTT",
                "ZL",
                "ZJ",
                "W",
                "TTT",
                "TTL",
                "TTJ",
                "VVL",
                "VVT",
                "VVJ",
        ] + signal_nicks:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
    lep_trigger_eff_variations = []
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_trigger_emb_et_Run{era}".format(era=args.era),
            "trg_et_eff_weight",
            Weight("(1.0*(pt_1<=28)+1.02*(pt_1>28))",
                   "trg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_trigger_emb_et_Run{era}".format(era=args.era),
            "trg_et_eff_weight",
            Weight("(1.0*(pt_1<=28)+0.98*(pt_1>28))",
                   "trg_et_eff_weight"), "Down"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_xtrigger_emb_et_Run{era}".format(era=args.era),
            "xtrg_et_eff_weight",
            Weight("(1.054*(pt_1<=28)+1.0*(pt_1>28))",
                   "xtrg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations.append(
        AddWeight(
            "CMS_eff_xtrigger_emb_et_Run{era}".format(era=args.era),
            "xtrg_et_eff_weight",
            Weight("(0.946*(pt_1<=28)+1.0*(pt_1>28))",
                   "xtrg_et_eff_weight"), "Down"))
    for variation_ in lep_trigger_eff_variations:
        for process_nick in ["EMB"]:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)

    # Zll reweighting !!! replaced by log normal uncertainties:
    # CMS_eFakeTau_Run2018 16%; CMS_mFakeTau_Run2018 26%
    '''zll_et_weight_variations = []
    zll_et_weight_variations.append(
        AddWeight(
            "CMS_eFakeTau_Run{era}".format(era=args.era), "eFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 1.46)*2.0/1.8) + ((abs(eta_1) >= 1.46 && abs(eta_1) < 1.558)*2.06) + ((abs(eta_1) >= 1.558)*2.13/1.53))",
                "eFakeTau_reweight"), "Up"))
    zll_et_weight_variations.append(
        AddWeight(
            "CMS_eFakeTau_Run{era}".format(era=args.era), "eFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 1.46)*1.6/1.8) + ((abs(eta_1) >= 1.46 && abs(eta_1) < 1.558)*1.27) + ((abs(eta_1) >= 1.558)*0.93/1.53))",
                "eFakeTau_reweight"), "Down"))
    for variation_ in zll_et_weight_variations:
        for process_nick in ["ZL"]:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
    zll_mt_weight_variations = []
    zll_mt_weight_variations.append(
        AddWeight(
            "CMS_mFakeTau_Run{era}".format(era=args.era), "mFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 0.4)*1.29/1.17) + ((abs(eta_1) >= 0.4 && abs(eta_1) < 0.8)*1.59/1.29) + ((abs(eta_1) >= 0.8 && abs(eta_1) < 1.2)*1.19/1.14) + ((abs(eta_1) >= 1.2 && abs(eta_1) < 1.7)*1.53/0.93) + ((abs(eta_1) >= 1.7 && abs(eta_1) < 2.3)*2.21/1.61) + (abs(eta_1) >= 2.3))",
                "mFakeTau_reweight"), "Up"))
    zll_mt_weight_variations.append(
        AddWeight(
            "CMS_mFakeTau_Run{era}".format(era=args.era), "mFakeTau_reweight",
            Weight(
                "(((abs(eta_1) < 0.4)*1.05/1.17) + ((abs(eta_1) >= 0.4 && abs(eta_1) < 0.8)*0.99/1.29) + ((abs(eta_1) >= 0.8 && abs(eta_1) < 1.2)*1.09/1.14) + ((abs(eta_1) >= 1.2 && abs(eta_1) < 1.7)*0.33/0.93) + ((abs(eta_1) >= 1.7 && abs(eta_1) < 2.3)*1.01/1.61) + (abs(eta_1) >= 2.3))",
                "mFakeTau_reweight"), "Down"))
    for variation_ in zll_mt_weight_variations:
        for process_nick in ["ZL"]:
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)'''

    # b tagging
    btag_eff_variations = create_systematic_variations(
        "CMS_htt_eff_b_Run{era}".format(era=args.era), "btagEff",
        DifferentPipeline)
    mistag_eff_variations = create_systematic_variations(
        "CMS_htt_mistag_b_Run{era}".format(era=args.era), "btagMistag",
        DifferentPipeline)
    for variation_ in btag_eff_variations + mistag_eff_variations:
        for process_nick in [
                "ZTT", "ZL", "ZJ", "W", "TTT", "TTL", "TTJ", "VVT", "VVL",
                "VVJ"
        ] + signal_nicks:
            for channelname_, _ in selelctedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)
        for process_nick in ["ZTT", "ZL", "W", "TTT", "TTL", "VVL", "VVT"
                             ] + signal_nicks:
            if "em" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # Embedded event specifics
    # Tau energy scale
    tau_es_3prong_variations = create_systematic_variations(
        "CMS_scale_emb_t_3prong_Run{era}".format(era=args.era),
        "tauEsThreeProng", DifferentPipeline)
    tau_es_1prong_variations = create_systematic_variations(
        "CMS_scale_emb_t_1prong_Run{era}".format(era=args.era),
        "tauEsOneProng", DifferentPipeline)
    tau_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_scale_emb_t_1prong1pizero_Run{era}".format(era=args.era),
        "tauEsOneProngOnePiZero", DifferentPipeline)
    for variation_ in tau_es_3prong_variations + tau_es_1prong_variations + tau_es_1prong1pizero_variations:
        for process_nick in ["EMB", "FAKES"]:
            for channelname_, _ in selelctedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # Ele energy scale
    ele_es_variations = create_systematic_variations("CMS_scale_emb_e",
                                                     "eleEs",
                                                     DifferentPipeline)
    for variation_ in ele_es_variations:
        for process_nick in ["EMB"]:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
            if "em" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    mt_decayMode_variations = []
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    mt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
            "Down"))
    for variation_ in mt_decayMode_variations:
        for process_nick in ["EMB"]:
            if "mt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=mt_processes[process_nick],
                    channel=mt,
                    era=era)
    et_decayMode_variations = []
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    et_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
            "Down"))
    for variation_ in et_decayMode_variations:
        for process_nick in ["EMB"]:
            if "et" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=et_processes[process_nick],
                    channel=et,
                    era=era)
    tt_decayMode_variations = []
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF"),
            "Up"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_3ProngEff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF"),
            "Down"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"),
            "Up"))
    tt_decayMode_variations.append(
        ReplaceWeight(
            "CMS_1ProngPi0Eff_Run{era}".format(era=args.era), "decayMode_SF",
            Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
            "Down"))
    for variation_ in tt_decayMode_variations:
        for process_nick in ["EMB"]:
            if "tt" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=tt_processes[process_nick],
                    channel=tt,
                    era=era)
    # 10% removed events in ttbar simulation (ttbar -> real tau tau events)
    # will be added/subtracted to ZTT shape to use as systematic
    tttautau_process_mt = Process(
        "TTT",
        TTTEstimation(era,
                      directory,
                      mt,
                      friend_directory=friend_directory["mt"]))
    tttautau_process_et = Process(
        "TTT",
        TTTEstimation(era,
                      directory,
                      et,
                      friend_directory=friend_directory["et"]))
    tttautau_process_tt = Process(
        "TTT",
        TTTEstimation(era,
                      directory,
                      tt,
                      friend_directory=friend_directory["tt"]))
    tttautau_process_em = Process(
        "TTT",
        TTTEstimation(era,
                      directory,
                      em,
                      friend_directory=friend_directory["em"]))
    if 'mt' in args.channels:
        for category in catsListD["mt"]:
            mt_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, mt,
                    [mt_processes["EMB"], tttautau_process_mt], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=mt_processes['ZTTpTTTauTauDown'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel(
                        "CMS_htt_emb_ttbar_Run{era}".format(era=args.era),
                        "Down"),
                    mass="125"))

            mt_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, mt,
                    [mt_processes["EMB"], tttautau_process_mt], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=mt_processes['ZTTpTTTauTauUp'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel(
                        "CMS_htt_emb_ttbar_Run{era}".format(era=args.era),
                        "Up"),
                    mass="125"))

    if 'et' in args.channels:
        for category in catsListD["et"]:
            et_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, et,
                    [et_processes["EMB"], tttautau_process_et], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=et_processes['ZTTpTTTauTauDown'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel(
                        "CMS_htt_emb_ttbar_Run{era}".format(era=args.era),
                        "Down"),
                    mass="125"))

            et_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, et,
                    [et_processes["EMB"], tttautau_process_et], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=et_processes['ZTTpTTTauTauUp'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel(
                        "CMS_htt_emb_ttbar_Run{era}".format(era=args.era),
                        "Up"),
                    mass="125"))
    if 'tt' in args.channels:
        for category in catsListD["tt"]:
            tt_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "EMB", era, directory, tt,
                    [tt_processes["EMB"], tttautau_process_tt], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=tt_processes['ZTTpTTTauTauDown'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel(
                        "CMS_htt_emb_ttbar_Run{era}".format(era=args.era),
                        "Down"),
                    mass="125"))

            tt_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, tt,
                    [tt_processes["EMB"], tttautau_process_tt], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=tt_processes['ZTTpTTTauTauUp'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel(
                        "CMS_htt_emb_ttbar_Run{era}".format(era=args.era),
                        "Up"),
                    mass="125"))
    if 'em' in args.channels:
        for category in catsListD["em"]:
            em_processes['ZTTpTTTauTauDown'] = Process(
                "ZTTpTTTauTauDown",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, em,
                    [em_processes["EMB"], tttautau_process_em], [1.0, -0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=em_processes['ZTTpTTTauTauDown'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel(
                        "CMS_htt_emb_ttbar_Run{era}".format(era=args.era),
                        "Down"),
                    mass="125"))

            em_processes['ZTTpTTTauTauUp'] = Process(
                "ZTTpTTTauTauUp",
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, em,
                    [em_processes["EMB"], tttautau_process_em], [1.0, 0.1]))
            systematics.add(
                Systematic(
                    category=category,
                    process=em_processes['ZTTpTTTauTauUp'],
                    analysis="smhtt",
                    era=era,
                    variation=Relabel(
                        "CMS_htt_emb_ttbar_Run{era}".format(era=args.era),
                        "Up"),
                    mass="125"))
    # jetfakes
    fake_factor_variations_et = []
    fake_factor_variations_mt = []
    for systematic_shift in [
            "ff_qcd{ch}_syst_Run2018{shift}",
            "ff_qcd_dm0_njet0{ch}_stat_Run2018{shift}",
            "ff_qcd_dm0_njet1{ch}_stat_Run2018{shift}",
            # "ff_qcd_dm1_njet0{ch}_stat_Run2018{shift}",
            # "ff_qcd_dm1_njet1{ch}_stat_Run2018{shift}",
            "ff_w_syst_Run2018{shift}",
            "ff_w_dm0_njet0{ch}_stat_Run2018{shift}",
            "ff_w_dm0_njet1{ch}_stat_Run2018{shift}",
            # "ff_w_dm1_njet0{ch}_stat_Run2018{shift}",
            # "ff_w_dm1_njet1{ch}_stat_Run2018{shift}",
            "ff_tt_syst_Run2018{shift}",
            "ff_tt_dm0_njet0_stat_Run2018{shift}",
            "ff_tt_dm0_njet1_stat_Run2018{shift}",
            # "ff_tt_dm1_njet0_stat_Run2018{shift}",
            # "ff_tt_dm1_njet1_stat_Run2018{shift}"
    ]:
        for shift_direction in ["Up", "Down"]:
            fake_factor_variations_et.append(
                ReplaceWeight(
                    "CMS_%s" % (systematic_shift.format(
                        ch='_et', shift="").replace("_dm0", "")),
                    "fake_factor",
                    Weight(
                        "ff2_{syst}".format(syst=systematic_shift.format(
                            ch="", shift="_%s" %
                            shift_direction.lower()).replace(
                                "_Run{era}".format(era=args.era), "")),
                        "fake_factor"), shift_direction))
            fake_factor_variations_mt.append(
                ReplaceWeight(
                    "CMS_%s" % (systematic_shift.format(
                        ch='_mt', shift="").replace("_dm0", "")),
                    "fake_factor",
                    Weight(
                        "ff2_{syst}".format(syst=systematic_shift.format(
                            ch="", shift="_%s" %
                            shift_direction.lower()).replace(
                                "_Run{era}".format(era=args.era), "")),
                        "fake_factor"), shift_direction))
    if "et" in args.channels:
        for variation_ in fake_factor_variations_et:
            systematics.add_systematic_variation(variation=variation_,
                                                 process=et_processes["FAKES"],
                                                 channel=et,
                                                 era=era)
    if "mt" in args.channels:
        for variation_ in fake_factor_variations_mt:
            systematics.add_systematic_variation(variation=variation_,
                                                 process=mt_processes["FAKES"],
                                                 channel=mt,
                                                 era=era)
    fake_factor_variations_tt = []
    for systematic_shift in [
            "ff_qcd{ch}_syst_Run2018{shift}",
            "ff_qcd_dm0_njet0{ch}_stat_Run2018{shift}",
            "ff_qcd_dm0_njet1{ch}_stat_Run2018{shift}",
            # "ff_qcd_dm1_njet0{ch}_stat_Run2018{shift}",
            # "ff_qcd_dm1_njet1{ch}_stat_Run2018{shift}",
            "ff_w{ch}_syst_Run2018{shift}",
            "ff_tt{ch}_syst_Run2018{shift}",
            "ff_w_frac{ch}_syst_Run2018{shift}",
            "ff_tt_frac{ch}_syst_Run2018{shift}"
    ]:
        for shift_direction in ["Up", "Down"]:
            fake_factor_variations_tt.append(
                ReplaceWeight(
                    "CMS_%s" % (systematic_shift.format(
                        ch='_tt', shift="").replace("_dm0", "")),
                    "fake_factor",
                    Weight(
                        "(0.5*ff1_{syst}*(byTightDeepTau2017v2p1VSjet_1<0.5)+0.5*ff2_{syst}*(byTightDeepTau2017v2p1VSjet_2<0.5))"
                        .format(syst=systematic_shift.format(
                            ch="", shift="_%s" %
                            shift_direction.lower()).replace(
                                "_Run{era}".format(era=args.era), "")),
                        "fake_factor"), shift_direction))
    if "tt" in args.channels:
        for variation_ in fake_factor_variations_tt:
            systematics.add_systematic_variation(variation=variation_,
                                                 process=tt_processes["FAKES"],
                                                 channel=tt,
                                                 era=era)

    # QCD for em
    qcd_variations = []
    qcd_variations.append(
        ReplaceWeight(
            "CMS_htt_qcd_0jet_rate_Run{era}".format(era=args.era),
            "qcd_weight",
            Weight(
                "em_qcd_osss_0jet_rateup_Weight*em_qcd_extrap_uncert_Weight",
                "qcd_weight"), "Up"))
    qcd_variations.append(
        ReplaceWeight(
            "CMS_htt_qcd_0jet_rate_Run{era}".format(era=args.era),
            "qcd_weight",
            Weight(
                "em_qcd_osss_0jet_ratedown_Weight*em_qcd_extrap_uncert_Weight",
                "qcd_weight"), "Down"))

    qcd_variations.append(
        ReplaceWeight(
            "CMS_htt_qcd_0jet_shape_Run{era}".format(era=args.era),
            "qcd_weight",
            Weight(
                "em_qcd_osss_0jet_shapeup_Weight*em_qcd_extrap_uncert_Weight",
                "qcd_weight"), "Up"))
    qcd_variations.append(
        ReplaceWeight(
            "CMS_htt_qcd_0jet_shape_Run{era}".format(
                era=args.era),
            "qcd_weight",
            Weight(
                "em_qcd_osss_0jet_shapedown_Weight*em_qcd_extrap_uncert_Weight",
                "qcd_weight"),
            "Down"))

    qcd_variations.append(
        ReplaceWeight(
            "CMS_htt_qcd_1jet_rate_Run{era}".format(era=args.era),
            "qcd_weight",
            Weight(
                "em_qcd_osss_1jet_rateup_Weight*em_qcd_extrap_uncert_Weight",
                "qcd_weight"), "Up"))
    qcd_variations.append(
        ReplaceWeight(
            "CMS_htt_qcd_1jet_rate_Run{era}".format(era=args.era),
            "qcd_weight",
            Weight(
                "em_qcd_osss_1jet_ratedown_Weight*em_qcd_extrap_uncert_Weight",
                "qcd_weight"), "Down"))

    qcd_variations.append(
        ReplaceWeight(
            "CMS_htt_qcd_1jet_shape_Run{era}".format(era=args.era),
            "qcd_weight",
            Weight(
                "em_qcd_osss_1jet_shapeup_Weight*em_qcd_extrap_uncert_Weight",
                "qcd_weight"), "Up"))
    qcd_variations.append(
        ReplaceWeight(
            "CMS_htt_qcd_1jet_shape_Run{era}".format(
                era=args.era),
            "qcd_weight",
            Weight(
                "em_qcd_osss_1jet_shapedown_Weight*em_qcd_extrap_uncert_Weight",
                "qcd_weight"),
            "Down"))

    qcd_variations.append(
        ReplaceWeight(
            "CMS_htt_qcd_iso_Run{era}".format(era=args.era), "qcd_weight",
            Weight("em_qcd_extrap_up_Weight*em_qcd_extrap_uncert_Weight",
                   "qcd_weight"), "Up"))
    qcd_variations.append(
        ReplaceWeight("CMS_htt_qcd_iso_Run{era}".format(era=args.era),
                      "qcd_weight",
                      Weight("em_qcd_osss_binned_Weight",
                             "qcd_weight"), "Down"))
    qcd_variations.append(
        ReplaceWeight(
            "CMS_htt_qcd_iso", "qcd_weight",
            Weight("em_qcd_extrap_up_Weight*em_qcd_extrap_uncert_Weight",
                   "qcd_weight"), "Up"))
    qcd_variations.append(
        ReplaceWeight("CMS_htt_qcd_iso", "qcd_weight",
                      Weight("em_qcd_osss_binned_Weight", "qcd_weight"),
                      "Down"))

    for variation_ in qcd_variations:
        for process_nick in ["QCD"]:
            if "em" in args.channels:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=em_processes[process_nick],
                    channel=em,
                    era=era)

    # Gluon-fusion WG1 uncertainty scheme
    ggh_variations = []
    for unc in [
            "THU_ggH_Mig01", "THU_ggH_Mig12", "THU_ggH_Mu", "THU_ggH_PT120",
            "THU_ggH_PT60", "THU_ggH_Res", "THU_ggH_VBF2j", "THU_ggH_VBF3j",
            "THU_ggH_qmtop"
    ]:
        ggh_variations.append(
            AddWeight(unc, "{}_weight".format(unc),
                      Weight("({})".format(unc), "{}_weight".format(unc)),
                      "Up"))
        ggh_variations.append(
            AddWeight(unc, "{}_weight".format(unc),
                      Weight("(2.0-{})".format(unc), "{}_weight".format(unc)),
                      "Down"))
    for variation_ in ggh_variations:
        for process_nick in [
                nick for nick in signal_nicks
                if "ggH" in nick and "HWW" not in nick
        ]:
            for channelname_ in args.channels:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging(
        "output/log/{}_{}_{}_shapes.log".format(args.era, args.tag,
                                                ",".join(args.channels)),
        logging.INFO)
    main(args)
