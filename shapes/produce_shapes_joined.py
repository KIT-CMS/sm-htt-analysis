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
    if "2016" == args.era:
        from shape_producer.channel import ETSM2016, MTSM2016, TTSM2016, EMSM2016
        smChannelsDict = {
            "et": ETSM2016(),
            "mt": MTSM2016(),
            "tt": TTSM2016(),
            "em": EMSM2016()
        }
        from shape_producer.estimation_methods_2016 import DataEstimation, HTTEstimation, ggHEstimation, qqHEstimation, VHEstimation, WHEstimation, ZHEstimation, ttHEstimation, ZTTEstimation, ZLEstimation, ZJEstimation, WEstimation, VVLEstimation, VVTEstimation, VVJEstimation, TTLEstimation, TTTEstimation, TTJEstimation, QCDEstimation_SStoOS_MTETEM, QCDEstimationTT, ZTTEmbeddedEstimation, FakeEstimationLT, NewFakeEstimationLT, FakeEstimationTT, NewFakeEstimationTT, ggHWWEstimation, qqHWWEstimation
        from shape_producer.era import Run2016
        era = Run2016(args.datasets)
    elif "2017" == args.era:
        from shape_producer.channel import ETSM2017, MTSM2017, TTSM2017, EMSM2017
        smChannelsDict = {
            "et": ETSM2017(),
            "mt": MTSM2017(),
            "tt": TTSM2017(),
            "em": EMSM2017()
        }
        from shape_producer.estimation_methods_2017 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, qqHEstimation, VHEstimation, WHEstimation, ZHEstimation, ttHEstimation, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, NewFakeEstimationLT, NewFakeEstimationTT, HWWEstimation, ggHWWEstimation, qqHWWEstimation

        from shape_producer.era import Run2017
        era = Run2017(args.datasets)
    elif "2018" == args.era:
        from shape_producer.channel import ETSM2018, MTSM2018, TTSM2018, EMSM2018
        smChannelsDict = {
            "et": ETSM2018(),
            "mt": MTSM2018(),
            "tt": TTSM2018(),
            "em": EMSM2018()
        }
        from shape_producer.estimation_methods_2018 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVLEstimation, VVTEstimation, VVJEstimation, WEstimation, ggHEstimation, qqHEstimation, VHEstimation, WHEstimation, ZHEstimation, ttHEstimation, QCDEstimation_ABCD_TT_ISO2, QCDEstimation_SStoOS_MTETEM, NewFakeEstimationLT, NewFakeEstimationTT, HWWEstimation, ggHWWEstimation, qqHWWEstimation

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

    if args.QCD_extrap_fit:
        smChannelsDict["mt"].cuts.remove("muon_iso")
        smChannelsDict["mt"].cuts.add(
            Cut("(iso_1<0.5)*(iso_1>=0.15)", "muon_iso_loose"))
        smChannelsDict["et"].cuts.remove("ele_iso")
        smChannelsDict["et"].cuts.add(
            Cut("(iso_1<0.5)*(iso_1>=0.1)", "ele_iso_loose"))
        smChannelsDict["tt"].cuts.get("os").invert()
        smChannelsDict["em"].cuts.get("os").invert()

    selectedChannels = set(args.channels) | {args.gof_channel} - {None}

    selectedChannelsTuples = {
        c_: smChannelsDict[c_] for c_ in selectedChannels}.items()
    selectedChannelsTuplesNoEM = {
        c_: smChannelsDict[c_] for c_ in selectedChannels if c_ != "em"}.items()

    pnameToEstD = {
        "data": DataEstimation,
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
    pnameToEstD.update(
        {ggH_htxs: lambda era, directory, channel,
         friend_directory: ggHEstimation(ggH_htxs, era, directory, channel,friend_directory=friend_directory)
         for ggH_htxs in ggHEstimation.htxs_dict})
    pnameToEstD.update(
        {qqH_htxs: lambda era, directory, channel,
         friend_directory: qqHEstimation(qqH_htxs, era, directory, channel,friend_directory=friend_directory)
         for qqH_htxs in qqHEstimation.htxs_dict})
    # define sets to select the correct processes
    trueTauBkgS = {"ZTT", "TTT", "VVT"}
    leptonTauBkgS = {"ZL", "TTL", "VVL"}
    jetFakeBkgS = {"ZJ", "W", "TTJ", "VVJ"}
    jetFakeBkgD = {
        "et": jetFakeBkgS,
        "mt": jetFakeBkgS,
        "tt": jetFakeBkgS,
        "em": {"W"},
    }

    ### collect all MC backgrounds
    MCBkgDS = { cn_: trueTauBkgS | leptonTauBkgS | jetFakeBkgD[cn_] for cn_ in selectedChannels }

    ## defines the signal sets
    ww_nicks = set()  # {"ggHWW125", "qqHWW125"}
    if args.gof_variable is None:
        signal_nicks = {
            "WH125", "ZH125", "VH125", "ttH125"} | {
            ggH_htxs for ggH_htxs in ggHEstimation.htxs_dict} | {
            qqH_htxs for qqH_htxs in qqHEstimation.htxs_dict} | ww_nicks
    else:
        signal_nicks = {"ggHWW125", "qqHWW125"} | ww_nicks

    processes = {}
    for channelname_, ch_ in selectedChannelsTuples:
        pL_ = {"data"} | signal_nicks | MCBkgDS[channelname_] | {"EMB"}
        if channelname_ != "em":
            pL_ = pL_ | {"EMB"}
        processes[channelname_] = {
            processname: Process(
                processname,
                pnameToEstD[processname](
                    era,
                    directory,
                    ch_,
        friend_directory=friend_directory[channelname_])) for processname in
        pL_ }

    for channelname_, ch_ in selectedChannelsTuplesNoEM:
        processes[channelname_]["FAKES"] = Process(
            "jetFakes",
            NewFakeEstimationLT(
                era, directory, ch_,
                [processes[channelname_][process]
                    for process in {"EMB"} | leptonTauBkgS],
                processes[channelname_]["data"],
                friend_directory=friend_directory[channelname_] +
                [args.fake_factor_friend_directory]))

    for channelname_, ch_ in selectedChannelsTuples:
        if channelname_ != "tt":
            est_ = QCDEstimation_SStoOS_MTETEM
        else:
            est_ = QCDEstimation_ABCD_TT_ISO2
        if channelname_ != "em": qcdpL = {"EMB"} | leptonTauBkgS | jetFakeBkgS
        else: qcdpL = {"EMB"} | leptonTauBkgS | {"W"}



        if channelname_ in ["mt", "et"]:
            if args.era == "2016": extrapolation_factor = 1.17
            else:   extrapolation_factor = 1.
            # QCD extrapolation_factor 1.17 for mt et 2016
            processes[channelname_]["QCD"] = Process(
                "QCD",
                est_(
                    era, directory, ch_,
                    [processes[channelname_][process] for process in qcdpL],
                    processes[channelname_]["data"],
                    friend_directory=friend_directory[channelname_],
                    extrapolation_factor=extrapolation_factor))
        elif channelname_ =="tt":
            processes[channelname_]["QCD"] = Process(
                "QCD",
                est_(
                    era, directory, ch_,
                    [processes[channelname_][process] for process in qcdpL],
                    processes[channelname_]["data"],
                    friend_directory=friend_directory[channelname_]))
        else:
            qcd_weight = Weight("em_qcd_osss_binned_Weight", "qcd_weight")
            processes[channelname_]["QCD"] = Process(
                "QCD",
                est_(
                    era, directory, ch_,
                    [processes[channelname_][process] for process in qcdpL],
                    processes[channelname_]["data"],
                    friend_directory=friend_directory[channelname_],
                    qcd_weight=qcd_weight))

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


    catsListD = {channelname_: [] for channelname_ in selectedChannels}
    # if not a gof test:Analysis shapes
    if args.gof_variable is None:
        for channelname_, ch_ in selectedChannelsTuples:
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
        for channelname_, ch_ in selectedChannelsTuples:
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
    for channelname_, ch_ in selectedChannelsTuples:
        catsL_ = catsListD[channelname_]
        processL_ = processes[channelname_]
        for processname_, category in product(processL_.values(), catsL_):
            systematics.add(
                Systematic(category=category,
                           process=processname_,
                           analysis="smhtt",
                           era=era,
                           variation=Nominal(),
                           mass="125"))

    # Shapes variations
    variationsTooAdd = {
        channelname_:
        {process_nick: []
         for process_nick in processes[channelname_]}
        for channelname_, _ in selectedChannelsTuples
    }

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
        for process_nick in signal_nicks | trueTauBkgS | {"TTL", "VVL", "FAKES"
        }:
            for channelname_, _ in selectedChannelsTuplesNoEM:
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
        for process_nick in signal_nicks | trueTauBkgS | {
                "TTL", "VVL", "EMB", "FAKES"
        }:
            for channelname_, _ in selectedChannelsTuplesNoEM:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # MC ele energy scale & smear uncertainties
    ele_es_variations = create_systematic_variations("CMS_scale_mc_e",
                                                     "eleScale",
                                                     DifferentPipeline)
    ele_es_variations += create_systematic_variations("CMS_reso_mc_e",
                                                      "eleSmear",
                                                      DifferentPipeline)
    for variation_ in ele_es_variations:
        for channelname_ in selectedChannels & {"et", "em"}:
            for process_nick in signal_nicks | trueTauBkgS | leptonTauBkgS | jetFakeBkgD[channelname_]:
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
        for channelname_ in selectedChannels:
            for process_nick in signal_nicks | MCBkgDS[channelname_]:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # MET energy scale. Note: only those variations for non-resonant processes
    # are used in the stat. inference
    met_unclustered_variations = create_systematic_variations(
        "CMS_scale_met_unclustered", "metUnclusteredEn", DifferentPipeline)
    for variation_ in met_unclustered_variations:  # + met_clustered_variations:
        for channelname_ in selectedChannels:
            for process_nick in signal_nicks | MCBkgDS[channelname_]:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # Recoil correction unc
    recoil_resolution_variations = create_systematic_variations(
        "CMS_htt_boson_reso_met_Run{era}".format(era=args.era),
        "metRecoilResolution", DifferentPipeline)
    recoil_response_variations = create_systematic_variations(
        "CMS_htt_boson_scale_met_Run{era}".format(era=args.era),
        "metRecoilResponse", DifferentPipeline)

    for variation_ in recoil_resolution_variations + recoil_response_variations:
        for channelname_ in selectedChannels:
            if channelname_ != "em":
                pS_ = signal_nicks | {"ZTT", "ZL", "ZJ", "W"}
            else:
                pS_ = signal_nicks | {"ZTT", "ZL", "W"}
            for process_nick in pS_:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # Z pt reweighting
    if args.era == "2018":
        zpt_variations = create_systematic_variations(
        "CMS_htt_dyShape", "zPtReweightWeight",
        SquareAndRemoveWeight)
    else:
        zpt_variations = create_systematic_variations(
        "CMS_htt_dyShape_Run{era}".format(era=args.era), "zPtReweightWeight",
        SquareAndRemoveWeight)
    for variation_ in zpt_variations:
        for channelname_ in selectedChannels:
            if channelname_ != "em":
                pS_ = {"ZTT", "ZL", "ZJ"}
            else:
                pS_ = {"ZTT", "ZL"}
            for process_nick in pS_:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # top pt reweighting
    top_pt_variations = create_systematic_variations("CMS_htt_ttbarShape",
                                                     "topPtReweightWeight",
                                                     SquareAndRemoveWeight)
    for variation_ in top_pt_variations:
        for channelname_ in selectedChannels:
            if channelname_ != "em":
                pS_ = {"TTT", "TTL", "TTJ"}
            else:
                pS_ = {"TTT", "TTL"}
            for process_nick in pS_:
                variationsTooAdd[channelname_][process_nick].append(variation_)

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
        for process_nick in jetFakeBkgS:
            for channelname_ in selectedChannels - {"em"}:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # ZL fakes energy scale
    ele_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_et_1prong_Run{era}".format(era=args.era),
        "tauEleFakeEsOneProng", DifferentPipeline)
    ele_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_et_1prong1pizero_Run{era}".format(era=args.era),
        "tauEleFakeEsOneProngPiZeros", DifferentPipeline)

    if "et" in selectedChannels:
        for process_nick in ["ZL"]:
            for variation_ in ele_fake_es_1prong_variations + ele_fake_es_1prong1pizero_variations:
                variationsTooAdd["et"][process_nick].append(variation_)

    mu_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong_Run{era}".format(era=args.era),
        "tauMuFakeEsOneProng", DifferentPipeline)
    mu_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong1pizero_Run{era}".format(era=args.era),
        "tauMuFakeEsOneProngPiZeros", DifferentPipeline)

    if "mt" in selectedChannels:
        for process_nick in ["ZL"]:
            for variation_ in mu_fake_es_1prong_variations + mu_fake_es_1prong1pizero_variations:
                variationsTooAdd["mt"][process_nick].append(variation_)

    # lepton trigger efficiency
    lep_trigger_eff_variations_mt_MC = []
    lep_trigger_eff_variations_mt_MC.append(
        AddWeight(
            "CMS_eff_trigger_mt_Run{era}".format(era=args.era),
            "trg_mt_eff_weight",
            Weight("(1.0*(pt_1<=25)+1.02*(pt_1>25))",
                   "trg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations_mt_MC.append(
        AddWeight(
            "CMS_eff_trigger_mt_Run{era}".format(era=args.era),
            "trg_mt_eff_weight",
            Weight("(1.0*(pt_1<=25)+0.98*(pt_1>25))",
                   "trg_mt_eff_weight"), "Down"))
    lep_trigger_eff_variations_mt_MC.append(
        AddWeight(
            "CMS_eff_xtrigger_mt_Run{era}".format(era=args.era),
            "xtrg_mt_eff_weight",
            Weight("(1.054*(pt_1<=25)+1.0*(pt_1>25))",
                   "xtrg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations_mt_MC.append(
        AddWeight(
            "CMS_eff_xtrigger_mt_Run{era}".format(era=args.era),
            "xtrg_mt_eff_weight",
            Weight("(0.946*(pt_1<=25)+1.0*(pt_1>25))",
                   "xtrg_mt_eff_weight"), "Down"))

    for variation_ in lep_trigger_eff_variations_mt_MC:
        for channelname_ in selectedChannels & {"mt"}:
            for process_nick in signal_nicks | MCBkgDS[channelname_]:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    lep_trigger_eff_variations_mt_EMB = []
    lep_trigger_eff_variations_mt_EMB.append(
        AddWeight(
            "CMS_eff_trigger_emb_mt_Run{era}".format(era=args.era),
            "trg_mt_eff_weight",
            Weight("(1.0*(pt_1<=25)+1.02*(pt_1>25))",
                   "trg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations_mt_EMB.append(
        AddWeight(
            "CMS_eff_trigger_emb_mt_Run{era}".format(era=args.era),
            "trg_mt_eff_weight",
            Weight("(1.0*(pt_1<=25)+0.98*(pt_1>25))",
                   "trg_mt_eff_weight"), "Down"))
    lep_trigger_eff_variations_mt_EMB.append(
        AddWeight(
            "CMS_eff_xtrigger_emb_mt_Run{era}".format(era=args.era),
            "xtrg_mt_eff_weight",
            Weight("(1.054*(pt_1<=25)+1.0*(pt_1>25))",
                   "xtrg_mt_eff_weight"), "Up"))
    lep_trigger_eff_variations_mt_EMB.append(
        AddWeight(
            "CMS_eff_xtrigger_emb_mt_Run{era}".format(era=args.era),
            "xtrg_mt_eff_weight",
            Weight("(0.946*(pt_1<=25)+1.0*(pt_1>25))",
                   "xtrg_mt_eff_weight"), "Down"))

    for variation_ in lep_trigger_eff_variations_mt_EMB:
        for process_nick in ["EMB"]:
            for channelname_ in selectedChannels & {"mt"}:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    lep_trigger_eff_variations_et_MC = []
    lep_trigger_eff_variations_et_MC.append(
        AddWeight(
            "CMS_eff_trigger_et_Run{era}".format(era=args.era),
            "trg_et_eff_weight",
            Weight("(1.0*(pt_1<=28)+1.02*(pt_1>28))",
                   "trg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations_et_MC.append(
        AddWeight(
            "CMS_eff_trigger_et_Run{era}".format(era=args.era),
            "trg_et_eff_weight",
            Weight("(1.0*(pt_1<=28)+0.98*(pt_1>28))",
                   "trg_et_eff_weight"), "Down"))
    lep_trigger_eff_variations_et_MC.append(
        AddWeight(
            "CMS_eff_xtrigger_et_Run{era}".format(era=args.era),
            "xtrg_et_eff_weight",
            Weight("(1.054*(pt_1<=28)+1.0*(pt_1>28))",
                   "xtrg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations_et_MC.append(
        AddWeight(
            "CMS_eff_xtrigger_et_Run{era}".format(era=args.era),
            "xtrg_et_eff_weight",
            Weight("(0.946*(pt_1<=28)+1.0*(pt_1>28))",
                   "xtrg_et_eff_weight"), "Down"))
    for variation_ in lep_trigger_eff_variations_et_MC:
        for channelname_ in selectedChannels & {"et"}:
            for process_nick in signal_nicks | MCBkgDS[channelname_]:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    lep_trigger_eff_variations_et_EMB = []
    lep_trigger_eff_variations_et_EMB.append(
        AddWeight(
            "CMS_eff_trigger_emb_et_Run{era}".format(era=args.era),
            "trg_et_eff_weight",
            Weight("(1.0*(pt_1<=28)+1.02*(pt_1>28))",
                   "trg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations_et_EMB.append(
        AddWeight(
            "CMS_eff_trigger_emb_et_Run{era}".format(era=args.era),
            "trg_et_eff_weight",
            Weight("(1.0*(pt_1<=28)+0.98*(pt_1>28))",
                   "trg_et_eff_weight"), "Down"))
    lep_trigger_eff_variations_et_EMB.append(
        AddWeight(
            "CMS_eff_xtrigger_emb_et_Run{era}".format(era=args.era),
            "xtrg_et_eff_weight",
            Weight("(1.054*(pt_1<=28)+1.0*(pt_1>28))",
                   "xtrg_et_eff_weight"), "Up"))
    lep_trigger_eff_variations_et_EMB.append(
        AddWeight(
            "CMS_eff_xtrigger_emb_et_Run{era}".format(era=args.era),
            "xtrg_et_eff_weight",
            Weight("(0.946*(pt_1<=28)+1.0*(pt_1>28))",
                   "xtrg_et_eff_weight"), "Down"))
    for variation_ in lep_trigger_eff_variations_et_EMB:
        for channelname_ in selectedChannels & {"et"}:
            for process_nick in ["EMB"]:
                variationsTooAdd[channelname_][process_nick].append(variation_)
    # Zll reweighting !!! replaced by log normal uncertainties:
    # CMS_eFakeTau_Run2018 16%; CMS_mFakeTau_Run2018 26%

    # b tagging
    btag_eff_variations = create_systematic_variations(
        "CMS_htt_eff_b_Run{era}".format(era=args.era), "btagEff",
        DifferentPipeline)
    mistag_eff_variations = create_systematic_variations(
        "CMS_htt_mistag_b_Run{era}".format(era=args.era), "btagMistag",
        DifferentPipeline)
    for variation_ in btag_eff_variations + mistag_eff_variations:
        for channelname_ in selectedChannels:
            for process_nick in signal_nicks | MCBkgDS[channelname_]:
                variationsTooAdd[channelname_][process_nick].append(variation_)

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
            for channelname_ in selectedChannels - {"em"}:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    # Ele energy scale
    ele_es_variations = create_systematic_variations("CMS_scale_emb_e",
                                                     "eleEs",
                                                     DifferentPipeline)
    for variation_ in ele_es_variations:
        for channelname_ in selectedChannels & {"et", "em"}:
            for process_nick in ["EMB"]:
                variationsTooAdd[channelname_][process_nick].append(variation_)

    mt_decayMode_variations = []
    for shift_direction in ["Up", "Down"]:
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
                "CMS_1ProngPi0Eff_Run{era}".format(
                    era=args.era), "decayMode_SF", Weight(
                    "embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF"), "Up"))
        mt_decayMode_variations.append(
            ReplaceWeight(
                "CMS_1ProngPi0Eff_Run{era}".format(era=args.era), "decayMode_SF",
                Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF"),
                "Down"))
    for variation_ in mt_decayMode_variations:
        for process_nick in ["EMB"]:
            for channelname_ in selectedChannels & {"mt"}:
                variationsTooAdd[channelname_][process_nick].append(variation_)
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
            if "et" in selectedChannels:
                variationsTooAdd["et"][process_nick].append(variation_)
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
            if "tt" in selectedChannels:
                variationsTooAdd["tt"][process_nick].append(variation_)
    # 10% removed events in ttbar simulation (ttbar -> real tau tau events)
    # will be added/subtracted to ZTT shape to use as systematic
    tttautau_processD = {
        channelname_: Process(
            "TTT",
            TTTEstimation(
                era,
                directory,
                ch_,
                friend_directory=friend_directory[channelname_])) for channelname_,
        ch_ in selectedChannelsTuples}
    for channelname_, ch_ in selectedChannelsTuples:
        for shift_direction, shift_ in {"Down": -0.1, "Up": 0.1}.items():
            p_ = Process(
                "ZTTpTTTauTau" + shift_direction,
                AddHistogramEstimationMethod(
                    "AddHistogram", "nominal", era, directory, ch_,
                    [processes[channelname_]["EMB"],
                     tttautau_processD[channelname_]],
                    [1.0, shift_]))
            for cat_ in catsListD[channelname_]:
                systematics.add(
                    Systematic(
                        category=cat_,
                        process=p_,
                        analysis="smhtt",
                        era=era,
                        variation=Relabel(
                            "CMS_htt_emb_ttbar_Run{era}".format(era=args.era),
                            shift_direction),
                        mass="125"))

    # jetfakes
    fake_factor_variations = {}
    fake_factor_weight = {}
    for channelname_ in selectedChannels & {"et", "mt"}:
        fake_factor_variations[channelname_] = [
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
        ]
        fake_factor_weight[channelname_] = "ff2_{syst}"
    for channelname_ in selectedChannels & {"tt"}:
        fake_factor_variations[channelname_] = [
            "ff_qcd{ch}_syst_Run2018{shift}",
            "ff_qcd_dm0_njet0{ch}_stat_Run2018{shift}",
            "ff_qcd_dm0_njet1{ch}_stat_Run2018{shift}",
            # "ff_qcd_dm1_njet0{ch}_stat_Run2018{shift}",
            # "ff_qcd_dm1_njet1{ch}_stat_Run2018{shift}",
            "ff_w{ch}_syst_Run2018{shift}",
            "ff_tt{ch}_syst_Run2018{shift}",
            "ff_w_frac{ch}_syst_Run2018{shift}",
            "ff_tt_frac{ch}_syst_Run2018{shift}"
        ]
        fake_factor_weight[channelname_] = "(0.5*ff1_{syst}*(byTightDeepTau2017v2p1VSjet_1<0.5)+0.5*ff2_{syst}*(byTightDeepTau2017v2p1VSjet_2<0.5))"
    for channelname_, ch_ in selectedChannelsTuplesNoEM:
        for shift_direction in ["Up", "Down"]:
            for systematic_shift in fake_factor_variations[channelname_]:
                variation_ = ReplaceWeight(
                    "CMS_%s" %
                    (systematic_shift.format(
                        ch='_' +
                        channelname_,
                        shift="").replace(
                        "_dm0",
                        "")),
                    "fake_factor",
                    Weight(
                        fake_factor_weight[channelname_].format(
                            syst=systematic_shift.format(
                                ch="",
                                shift="_%s" %
                                shift_direction.lower()).replace(
                                "_Run{era}".format(
                                    era=args.era),
                                "")),
                        "fake_factor"),
                    shift_direction)
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=processes[channelname_]["FAKES"],
                    channel=ch_, era=era)

    # QCD for em
    qcd_variations = []
    for shift_direction in ["up", "down"]:
        qcd_variations.append(
            ReplaceWeight(
                "CMS_htt_qcd_0jet_rate_Run{era}".format(
                    era=args.era),
                "qcd_weight",
                Weight(
                    "em_qcd_osss_0jet_rate" +
                    shift_direction +
                    "_Weight",
                    "qcd_weight"),
                shift_direction.capitalize()))
        qcd_variations.append(
            ReplaceWeight(
                "CMS_htt_qcd_0jet_shape_Run{era}".format(
                    era=args.era),
                "qcd_weight",
                Weight(
                    "em_qcd_osss_0jet_shape" +
                    shift_direction +
                    "_Weight",
                    "qcd_weight"),
                shift_direction.capitalize()))
        qcd_variations.append(
            ReplaceWeight(
                "CMS_htt_qcd_1jet_rate_Run{era}".format(
                    era=args.era),
                "qcd_weight",
                Weight(
                    "em_qcd_osss_1jet_rate" +
                    shift_direction +
                    "_Weight",
                    "qcd_weight"),
                shift_direction.capitalize()))
        qcd_variations.append(
            ReplaceWeight(
                "CMS_htt_qcd_1jet_shape_Run{era}".format(
                    era=args.era),
                "qcd_weight",
                Weight(
                    "em_qcd_osss_1jet_shape" +
                    shift_direction +
                    "_Weight",
                    "qcd_weight"),
                shift_direction.capitalize()))
        qcd_variations.append(
            ReplaceWeight(
                "CMS_htt_qcd_iso_Run{era}".format(
                    era=args.era),
                "qcd_weight",
                Weight(
                    "em_qcd_extrap_" +
                    shift_direction +
                    "_Weight",
                    "qcd_weight"),
                shift_direction.capitalize()))
        qcd_variations.append(  # why do we need both CMS_htt_qcd_iso_Run$ERA and CMS_htt_qcd_iso ?
            ReplaceWeight("CMS_htt_qcd_iso", "qcd_weight",
                          Weight("em_qcd_extrap_" + shift_direction + "_Weight", "qcd_weight"), shift_direction.capitalize()))

    for variation_ in qcd_variations:
        for process_nick in ["QCD"]:
            if "em" in selectedChannels:
                variationsTooAdd["em"][process_nick].append(variation_)

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

    # add all variation from the systematics
    for channelname_, ch_ in selectedChannelsTuples:
        for process_nick in processes[channelname_]:
            for variation_ in variationsTooAdd[channelname_][process_nick]:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=processes[channelname_][process_nick],
                    channel=ch_,
                    era=era)
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
