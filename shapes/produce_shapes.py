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
import os

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
    parser.add_argument(
        "--processes",
        default=[],
        type=lambda processlist:
        [process for process in processlist.split(',')],
        help="processes to be considered, seperated by a comma without space")
    parser.add_argument(
        "--categories",
        default=[],
        type=lambda categorylist:
        [category for category in categorylist.split(',')],
        help="processes to be considered, seperated by a comma without space")
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument("--gof-variable",
                        type=str,
                        help="Variable for goodness of fit shapes.")
    parser.add_argument("--num-threads",
                        default=1,
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
    logger.info("Set up shape variations.")
    # remote job in this case
    if len(args.categories) > 0 and len(args.processes) > 0:
        path = "output/shapes/{TAG}".format(
            TAG=args.tag)
        if not os.path.exists(path):
            os.makedirs(path)
        systematics = Systematics(
            "{PATH}/{ERA}-{TAG}-{CHANNEL}-{PROCESS}-{CATEGORIES}-shapes.root".format(
                PATH=path,
                ERA=args.era,
                TAG=args.tag,
                CHANNEL=",".join(args.channels),
                PROCESS=",".join(args.processes),
                CATEGORIES=",".join(args.categories)),
            num_threads=args.num_threads,
            skip_systematic_variations=args.skip_systematic_variations)
    else:
        path = "output/shapes/{TAG}".format(
            TAG=args.tag)
        if not os.path.exists(path):
            os.makedirs(path)
        systematics = Systematics(
            "output/shapes/{TAG}/{ERA}-{TAG}-{CHANNELS}-shapes.root".format(
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

    selectedChannels = set(args.channels) - {None}
    selectedCategories = set(args.categories)
    
    selectedChannelsTuples = {
        c_: smChannelsDict[c_] for c_ in selectedChannels}.items()
    selectedChannelsTuplesNoEM = {
        c_: smChannelsDict[c_] for c_ in selectedChannels if c_ != "em"}.items()

    # Define Process Nicks
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

    # collect all MC backgrounds
    MCBkgDS = {
        cn_: trueTauBkgS | leptonTauBkgS | jetFakeBkgD[cn_]
        for cn_ in selectedChannels}

    # defines the signal sets
    ww_nicks = {"ggHWW125", "qqHWW125"}
    # tmp fix, remove for eoy ntuples
    if args.era not in ["2016","2017"]:  ww_nicks = set()

    if args.gof_variable is None:
        signal_nicks = {
            "WH125", "ZH125", "VH125", "ttH125"} | {
            ggH_htxs for ggH_htxs in ggHEstimation.htxs_dict} | {
            qqH_htxs for qqH_htxs in qqHEstimation.htxs_dict} | ww_nicks
    else:
        signal_nicks = {"ggHWW125", "qqHWW125"} | ww_nicks

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

    # provide lambda functions, as the signal estimation methods need an
    # additional argument to determine the stxs class
    pnameToEstD.update(
        {ggH_htxs: lambda era, directory, channel,
         friend_directory, ggH_htxs=ggH_htxs:
         ggHEstimation(
             ggH_htxs, era, directory, channel,
             friend_directory=friend_directory)
         for ggH_htxs in ggHEstimation.htxs_dict})
    pnameToEstD.update(
        {qqH_htxs: lambda era, directory, channel,
         friend_directory, qqH_htxs=qqH_htxs:
         qqHEstimation(
             qqH_htxs, era, directory, channel,
             friend_directory=friend_directory)
         for qqH_htxs in qqHEstimation.htxs_dict})

    # Generate dict mapping processnames to proceses
    processes = {}
    for chname_, ch_ in selectedChannelsTuples:
        pS_ = {"data_obs"} | signal_nicks | MCBkgDS[chname_] | {"EMB"}
        processes[chname_] = {
            processname: Process(
                processname,
                pnameToEstD[processname](
                    era,
                    directory,
                    ch_,
                    friend_directory=friend_directory[chname_])) for processname in
            pS_}

    # Create the jetFakes process for all channels but em
    for chname_, ch_ in selectedChannelsTuplesNoEM:
        if chname_ != "tt":
            est_ = NewFakeEstimationLT
        else:
            est_ = NewFakeEstimationTT
        processes[chname_]["FAKES"] = Process(
            "jetFakes",
            est_(
                era, directory, ch_,
                [processes[chname_][process]
                    for process in {"EMB"} | leptonTauBkgS],
                processes[chname_]["data_obs"],
                friend_directory=friend_directory[chname_] +
                [args.fake_factor_friend_directory]))

    # QCD process setup
    for chname_, ch_ in selectedChannelsTuples:
        if chname_ != "tt":
            est_ = QCDEstimation_SStoOS_MTETEM
        else:
            if args.era != "2016":
                est_ = QCDEstimation_ABCD_TT_ISO2
            else:
                est_ = QCDEstimationTT

        qcdpS = {"EMB"} | leptonTauBkgS | jetFakeBkgD[chname_]

        if chname_ in ["mt", "et"]:
            if args.era == "2016":
                extrapolation_factor = 1.17
            else:
                extrapolation_factor = 1.
            # QCD extrapolation_factor 1.17 for mt et 2016
            processes[chname_]["QCD"] = Process(
                "QCD",
                est_(
                    era, directory, ch_,
                    [processes[chname_][process] for process in qcdpS],
                    processes[chname_]["data_obs"],
                    friend_directory=friend_directory[chname_],
                    extrapolation_factor=extrapolation_factor))
        elif chname_ == "tt":
            processes[chname_]["QCD"] = Process(
                "QCD",
                est_(
                    era, directory, ch_,
                    [processes[chname_][process] for process in qcdpS],
                    processes[chname_]["data_obs"],
                    friend_directory=friend_directory[chname_]))
        else:
            qcd_weight = Weight("em_qcd_osss_binned_Weight", "qcd_weight")
            processes[chname_]["QCD"] = Process(
                "QCD",
                est_(
                    era, directory, ch_,
                    [processes[chname_][process] for process in qcdpS],
                    processes[chname_]["data_obs"],
                    friend_directory=friend_directory[chname_],
                    qcd_weight=qcd_weight))

    # If no processes are passed as an argument, generate all
    if args.processes in [None, []]:
        selectedProcesses = {pname_
                             for pname_ in processes[chname_]
                             for chname_ in processes}
    else:
        selectedProcesses = set(args.processes)
        for chname_ in processes.keys():
            for process in processes[chname_].keys():
                if process not in selectedProcesses:
                    del processes[chname_][process]

    # Read the NN output classes either from the training, or from the template
    binning = yaml.load(open(args.binning), Loader=yaml.Loader)
    def readclasses(channelname, selectedCategories):
        if args.tag == "" or args.tag is None or not os.path.isfile(
                "output/ml/{}_{}_{}/dataset_config.yaml".format(args.era, channelname, args.tag)):
            logger.warn("No tag given, using template.")
            confFileName = "ml/templates/shape-producer_{}.yaml".format(
                channelname)
        else:
            confFileName = "output/ml/{}_{}_{}/dataset_config.yaml".format(
                args.era, channelname, args.tag)
        logger.debug("Parse classes from " + confFileName)
        confdict = yaml.load(open(confFileName, "r"), Loader=yaml.Loader)
        logger.debug(
            "Classes for {} loaded: {}".format(
                channelname, str(
                    confdict["classes"])))
        classdict = {}
        if len(selectedCategories) > 0:
            for nnclass in set(confdict["classes"]).intersection(selectedCategories):
                classdict[nnclass] = confdict["classes"].index(nnclass)
            return classdict
        else:
            for nnclass in set(confdict["classes"]):
                classdict[nnclass] = confdict["classes"].index(nnclass)
            return classdict

    catsListD = {chname_: [] for chname_ in selectedChannels}

    # if not a gof test:Analysis shapes
    # add the max nnscore as variables
    if args.gof_variable is None:
        for chname_, ch_ in selectedChannelsTuples:
            catsL_ = catsListD[chname_]
            classdict = readclasses(chname_, selectedCategories)
            for label in classdict.keys():
                score = Variable(
                    "{}_max_score".format(chname_),
                    VariableBinning(binning["analysis"][chname_][label]))
                maxIdxCut = Cut(
                    "{channel}_max_index=={index}".format(
                        channel=chname_,
                        index=classdict[label]),
                    "exclusive_score")
                catsL_.append(
                    Category(
                        label,
                        ch_,
                        Cuts(maxIdxCut),
                        variable=score))
                # if the net was trained on stage0 signals, add the stage1p1
                # categories cutbased, otherwise use classes give
                if label in ["ggh", "qqh"]:
                    stxs = 100 if label == "ggh" else 200
                    for i_e, e in enumerate(binning["stxs_stage1p1"][label]):
                        score = Variable(
                            "{}_max_score".format(chname_), VariableBinning(
                                binning["analysis"][chname_][label]))
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
        for chname_, ch_ in selectedChannelsTuples:
            catsL_ = catsListD[chname_]
            score = Variable(args.gof_variable,
                             VariableBinning(
                                 binning["gof"][chname_]
                                 [args.gof_variable]["bins"]),
                             expression=binning["gof"][chname_]
                             [args.gof_variable]["expression"])
            if "cut" in binning["gof"][chname_][args.gof_variable].keys():
                cuts = Cuts(
                    Cut(binning["gof"][chname_][args.gof_variable]["cut"], "binning"))
            else:
                cuts = Cuts()
            catsL_.append(
                Category(
                    args.gof_variable,
                    ch_,
                    cuts,
                    variable=score))

    # Nominal histograms
    for chname_, ch_ in selectedChannelsTuples:
        catsL_ = catsListD[chname_]
        processL_ = processes[chname_]
        for pname_, category in product(processL_.values(), catsL_):
            systematics.add(
                Systematic(category=category,
                           process=pname_,
                           analysis="smhtt",
                           era=era,
                           variation=Nominal(),
                           mass="125"))

    # Shapes variations
    variationsToAdd = {
        chname_:
        {process_nick: []
         for process_nick in processes[chname_]}
        for chname_, _ in selectedChannelsTuples
    }

    if args.era in ["2016", "2017"]:
        # Prefiring weights
        prefiring_variaitons = [
            ReplaceWeight(
                "CMS_prefiring", "prefireWeight", Weight(
                    "prefiringweightup", "prefireWeight"), "Up"), ReplaceWeight(
                "CMS_prefiring", "prefireWeight", Weight(
                    "prefiringweightdown", "prefireWeight"), "Down"), ]
        for variation_ in prefiring_variaitons:
            for process_nick in selectedProcesses & (
                    MCBkgDS[chname_] | signal_nicks):
                for chname_, _ in selectedChannelsTuples:
                    variationsToAdd[chname_][process_nick].append(variation_)


    # Tau ID
    # in et and mt one nuisance per pT bin
    # [30., 35., 40., 500., 1000. ,$\le$ 1000.]
    if len(selectedChannels & {"et", "mt"}) > 0:
        pt = [30, 35, 40, 500, 1000, "inf"]
        for histname_, pS_ in {
            "CMS_eff_t_{}-{}_Run{}": signal_nicks | {"EMB", "VVL", "TTL"} |
                trueTauBkgS, "CMS_eff_emb_t_{}-{}_Run{}": {"EMB"}}.items():
            tau_id_variations = []
            for shift_direction in ["Up", "Down"]:
                for i, ptbin in enumerate(pt[:-1]):
                    bindown = ptbin
                    binup = pt[i + 1]
                    if binup == "inf":
                        weightstr = "(((pt_2 >= {bindown})*tauIDScaleFactorWeight{shift_direction}_medium_DeepTau2017v2p1VSjet_2)+((pt_2 < {bindown})*tauIDScaleFactorWeight_medium_DeepTau2017v2p1VSjet_2))"
                    else:
                        weightstr = "(((pt_2 >= {bindown} && pt_2 <= {binup})*tauIDScaleFactorWeight{shift_direction}_medium_DeepTau2017v2p1VSjet_2)+((pt_2 < {bindown} || pt_2 > {binup})*tauIDScaleFactorWeight_medium_DeepTau2017v2p1VSjet_2))"
                    tau_id_variations.append(
                        ReplaceWeight(
                            histname_.format(bindown, binup, args.era),
                            "taubyIsoIdWeight",
                            Weight(
                                weightstr.format(
                                    bindown=bindown, binup=binup,
                                    shift_direction=shift_direction),
                                "taubyIsoIdWeight"),
                            shift_direction))

            for variation_ in tau_id_variations:
                for chname_ in selectedChannels & {"et", "mt"}:
                    for process_nick in selectedProcesses & pS_:
                        variationsToAdd[chname_][process_nick].append(
                            variation_)

    # for tautau, the id is split by decay mode, and each decay mode is assosicated one nuicance
    for chname_ in selectedChannels & {"tt"}:
        for histname_, pS_ in {
            "CMS_eff_t_dm{dm}_Run{era}": signal_nicks | {"EMB", "VVL", "TTL"} |
                trueTauBkgS, "CMS_eff_emb_t_dm{dm}_Run{era}": {"EMB"}}.items():
            tau_id_variations = []
            for shift_direction in ["Up", "Down"]:
                for decaymode in [0, 1, 10, 11]:
                    weightstr = "(((decayMode_1=={dm})*tauIDScaleFactorWeight{shift_direction}_medium_DeepTau2017v2p1VSjet_1)+((decayMode_1!={dm})*tauIDScaleFactorWeight_medium_DeepTau2017v2p1VSjet_1)*((decayMode_2=={dm})*tauIDScaleFactorWeight{shift_direction}_medium_DeepTau2017v2p1VSjet_2)+((decayMode_2!={dm})*tauIDScaleFactorWeight_medium_DeepTau2017v2p1VSjet_2))"
                    tau_id_variations.append(
                        ReplaceWeight(
                            histname_.format(
                                dm=decaymode, era=args.era),
                            "taubyIsoIdWeight",
                            Weight(
                                weightstr.format(
                                    dm=decaymode,shift_direction=shift_direction),
                                "taubyIsoIdWeight"),
                            shift_direction))
            # run two times, one for regular, one for embedding
            for variation_ in tau_id_variations:
                for process_nick in selectedProcesses & pS_:
                    variationsToAdd[chname_][process_nick].append(
                        variation_)

    # Tau energy scale
        # Tau energy scale
    for name_, pS_ in {
        "_emb_": {
            "EMB", "FAKES"}, "_": signal_nicks | trueTauBkgS | {
            "TTL", "VVL", "EMB", "FAKES"}}.items():
        tau_es_3prong_variations = create_systematic_variations(
            "CMS_scale{name}t_3prong_Run{era}".format(
                name=name_, era=args.era),
            "tauEsThreeProng", DifferentPipeline)
        tau_es_3prong1pizero_variations = create_systematic_variations(
            "CMS_scale{name}t_3prong1pizero_Run{era}".format(
                name=name_, era=args.era),
            "tauEsThreeProngOnePiZero", DifferentPipeline)
        tau_es_1prong_variations = create_systematic_variations(
            "CMS_scale{name}t_1prong_Run{era}".format(
                name=name_, era=args.era),
            "tauEsOneProng", DifferentPipeline)
        tau_es_1prong1pizero_variations = create_systematic_variations(
            "CMS_scale{name}t_1prong1pizero_Run{era}".format(
                name=name_, era=args.era), "tauEsOneProngOnePiZero", DifferentPipeline)
        for variation_ in tau_es_3prong_variations + tau_es_1prong_variations + \
                tau_es_1prong1pizero_variations + tau_es_3prong1pizero_variations:
            for process_nick in selectedProcesses & pS_:
                for chname_ in selectedChannels - {"em"}:
                    variationsToAdd[chname_][process_nick].append(
                        variation_)

    # MC ele energy scale & smear uncertainties
    ele_es_variations = create_systematic_variations("CMS_scale_mc_e",
                                                     "eleScale",
                                                     DifferentPipeline)
    ele_es_variations += create_systematic_variations("CMS_reso_mc_e",
                                                      "eleSmear",
                                                      DifferentPipeline)
    for variation_ in ele_es_variations:
        for chname_ in selectedChannels & {"et", "em"}:
            for process_nick in selectedProcesses & (
                    signal_nicks | trueTauBkgS | leptonTauBkgS |
                    jetFakeBkgD[chname_]):
                variationsToAdd[chname_][process_nick].append(variation_)

    # Jet energy scale

    # Inclusive JES shapes
    jet_es_variations = []
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_Absolute", "jecUncAbsolute", DifferentPipeline
    )
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_Absolute_Run{era}".format(era=args.era), "jecUncAbsoluteYear", DifferentPipeline
    )
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_BBEC1", "jecUncBBEC1", DifferentPipeline
    )
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_BBEC1_Run{era}".format(era=args.era), "jecUncBBEC1Year", DifferentPipeline
    )
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_EC2", "jecUncEC2", DifferentPipeline
    )
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_EC2_Run{era}".format(era=args.era), "jecUncEC2Year", DifferentPipeline
    )
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_HF", "jecUncHF", DifferentPipeline
    )
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_HF_Run{era}".format(era=args.era), "jecUncHFYear", DifferentPipeline
    )
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_FlavorQCD", "jecUncFlavorQCD", DifferentPipeline
    )
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeBal", "jecUncRelativeBal", DifferentPipeline
    )
    jet_es_variations += create_systematic_variations(
        "CMS_scale_j_RelativeSample_Run{era}".format(era=args.era),
        "jecUncRelativeSampleYear",
        DifferentPipeline,
    )
    jet_es_variations += create_systematic_variations(
        "CMS_reso_j_Run{era}".format(era=args.era), "jerUnc", DifferentPipeline
    )


    for variation_ in jet_es_variations:
        for chname_ in selectedChannels:
            for process_nick in selectedProcesses & (
                    signal_nicks | MCBkgDS[chname_]):
                variationsToAdd[chname_][process_nick].append(variation_)

    # MET energy scale. Note: only those variations for non-resonant processes
    # are used in the stat. inference
    met_unclustered_variations = create_systematic_variations(
        "CMS_scale_met_unclustered", "metUnclusteredEn", DifferentPipeline)
    for variation_ in met_unclustered_variations:  # + met_clustered_variations:
        for chname_ in selectedChannels:
            for process_nick in selectedProcesses & (
                    signal_nicks | MCBkgDS[chname_]):
                variationsToAdd[chname_][process_nick].append(variation_)

    # Recoil correction unc
    recoil_resolution_variations = create_systematic_variations(
        "CMS_htt_boson_reso_met_Run{era}".format(era=args.era),
        "metRecoilResolution", DifferentPipeline)
    recoil_response_variations = create_systematic_variations(
        "CMS_htt_boson_scale_met_Run{era}".format(era=args.era),
        "metRecoilResponse", DifferentPipeline)

    for variation_ in recoil_resolution_variations + recoil_response_variations:
        for chname_ in selectedChannels:
            if chname_ != "em":
                pS_ = signal_nicks | {"ZTT", "ZL", "ZJ", "W"}
            else:
                pS_ = signal_nicks | {"ZTT", "ZL", "W"}
            # tmp fix, remove for eoy ntuples
            if args.era == "2016": pS_={p_ for p_ in pS_ if "ttH125" not in p_ }
            for process_nick in selectedProcesses & pS_:
                variationsToAdd[chname_][process_nick].append(variation_)

    # Z pt reweighting
    if args.era == "2018":
        zpt_variations = create_systematic_variations(
            "CMS_htt_dyShape", "zPtReweightWeight",
            SquareAndRemoveWeight)
    else:
        zpt_variations = create_systematic_variations(
            "CMS_htt_dyShape_Run{era}".format(era=args.era),
            "zPtReweightWeight", SquareAndRemoveWeight)
    for variation_ in zpt_variations:
        for chname_ in selectedChannels:
            if chname_ != "em":
                pS_ = {"ZTT", "ZL", "ZJ"}
            else:
                pS_ = {"ZTT", "ZL"}
            for process_nick in selectedProcesses & pS_:
                variationsToAdd[chname_][process_nick].append(variation_)

    # top pt reweighting
    top_pt_variations = create_systematic_variations("CMS_htt_ttbarShape",
                                                     "topPtReweightWeight",
                                                     SquareAndRemoveWeight)
    for variation_ in top_pt_variations:
        for chname_ in selectedChannels:
            if chname_ != "em":
                pS_ = {"TTT", "TTL", "TTJ"}
            else:
                pS_ = {"TTT", "TTL"}
            for process_nick in selectedProcesses & pS_:
                variationsToAdd[chname_][process_nick].append(variation_)

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
        for process_nick in selectedProcesses & jetFakeBkgS:
            for chname_ in selectedChannels - {"em"}:
                variationsToAdd[chname_][process_nick].append(variation_)

    # ZL fakes energy scale
    ele_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_et_1prong_barrel_Run{era}".format(era=args.era),
        "tauEleFakeEsOneProngBarrel",
        DifferentPipeline,
    )
    ele_fake_es_1prong_variations += create_systematic_variations(
        "CMS_ZLShape_et_1prong_endcap_Run{era}".format(era=args.era),
        "tauEleFakeEsOneProngEndcap",
        DifferentPipeline,
    )
    ele_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_et_1prong1pizero_barrel_Run{era}".format(era=args.era),
        "tauEleFakeEsOneProngPiZerosBarrel",
        DifferentPipeline,
    )
    ele_fake_es_1prong1pizero_variations += create_systematic_variations(
        "CMS_ZLShape_et_1prong1pizero_endcap_Run{era}".format(era=args.era),
        "tauEleFakeEsOneProngPiZerosEndcap",
        DifferentPipeline,
    )
    if "et" in selectedChannels:
        for process_nick in selectedProcesses & {"ZL"}:
            for variation_ in ele_fake_es_1prong_variations + ele_fake_es_1prong1pizero_variations:
                variationsToAdd["et"][process_nick].append(variation_)

    mu_fake_es_1prong_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong_Run{era}".format(era=args.era),
        "tauMuFakeEsOneProng", DifferentPipeline)
    mu_fake_es_1prong1pizero_variations = create_systematic_variations(
        "CMS_ZLShape_mt_1prong1pizero_Run{era}".format(era=args.era),
        "tauMuFakeEsOneProngPiZeros", DifferentPipeline)

    if "mt" in selectedChannels:
        for process_nick in selectedProcesses & {"ZL"}:
            for variation_ in mu_fake_es_1prong_variations + mu_fake_es_1prong1pizero_variations:
                variationsToAdd["mt"][process_nick].append(variation_)

    # lepton trigger efficiency
    if args.era == "2017":
        lteffCutD = {
            "mt": "25",
            "et": "28",
        }
    elif args.era == "2016":
        lteffCutD = {
            "mt": "23",
            "et": "28",
        }
    for chname_ in selectedChannels & {"mt", "et"}:
        if chname_ == "et" and args.era not in ["2017", "2018"]:
            continue
        for flag, pS_ in {
            "_emb_": {"EMB"},
                "_": signal_nicks | MCBkgDS[chname_]}.items():
            lep_trigger_eff_variations = []
            lep_trigger_eff_variations.append(
                AddWeight(
                    "CMS_eff_trigger{embflag}{ch}_Run{era}".format(
                        embflag=flag, ch=chname_, era=args.era), "trg_{ch}_eff_weight".format(
                        ch=chname_), Weight(
                        "(1.0*(pt_1<={ptcut})+1.02*(pt_1>{ptcut}))".format(
                            ptcut=lteffCutD[chname_]), "trg_{ch}_eff_weight".format(
                            ch=chname_)), "Up"))
            lep_trigger_eff_variations.append(
                AddWeight(
                    "CMS_eff_trigger{embflag}{ch}_Run{era}".format(
                        embflag=flag, ch=chname_, era=args.era), "trg_{ch}_eff_weight".format(
                        ch=chname_), Weight(
                        "(1.0*(pt_1<={ptcut})+0.98*(pt_1>{ptcut}))".format(
                            ptcut=lteffCutD[chname_]), "trg_{ch}_eff_weight".format(
                            ch=chname_)), "Down"))
            lep_trigger_eff_variations.append(
                AddWeight(
                    "CMS_eff_xtrigger{embflag}{ch}_Run{era}".format(
                        embflag=flag, ch=chname_, era=args.era), "xtrg_{ch}_eff_weight".format(
                        ch=chname_), Weight(
                        "(1.054*(pt_1<={ptcut})+1.0*(pt_1>{ptcut}))".format(
                            ptcut=lteffCutD[chname_]), "xtrg_{ch}_eff_weight".format(
                            ch=chname_)), "Up"))
            lep_trigger_eff_variations.append(
                AddWeight(
                    "CMS_eff_xtrigger{embflag}{ch}_Run{era}".format(
                        embflag=flag, ch=chname_, era=args.era), "xtrg_{ch}_eff_weight".format(
                        ch=chname_), Weight(
                        "(0.946*(pt_1<={ptcut})+1.0*(pt_1>{ptcut}))".format(
                            ptcut=lteffCutD[chname_]), "xtrg_{ch}_eff_weight".format(
                            ch=chname_)), "Down"))
            for variation_ in lep_trigger_eff_variations:
                for process_nick in selectedProcesses & pS_:
                    variationsToAdd[chname_][process_nick].append(variation_)

    # Zll reweighting !!! replaced by log normal uncertainties:
    # CMS_eFakeTau_Run2018 16%; CMS_mFakeTau_Run2018 26%

    # Embedded event specifics
    # b tagging
    btag_eff_variations = create_systematic_variations(
        "CMS_htt_eff_b_Run{era}".format(era=args.era), "btagEff",
        DifferentPipeline)
    mistag_eff_variations = create_systematic_variations(
        "CMS_htt_mistag_b_Run{era}".format(era=args.era), "btagMistag",
        DifferentPipeline)
    for variation_ in btag_eff_variations + mistag_eff_variations:
        for chname_ in selectedChannels:
            for process_nick in selectedProcesses & (
                    signal_nicks | MCBkgDS[chname_]):
                variationsToAdd[chname_][process_nick].append(variation_)

    # Ele energy scale
    ele_es_variations = create_systematic_variations("CMS_scale_emb_e",
                                                     "eleEs",
                                                     DifferentPipeline)
    for variation_ in ele_es_variations:
        for chname_ in selectedChannels & {"et", "em"}:
            for process_nick in selectedProcesses & {"EMB"}:
                variationsToAdd[chname_][process_nick].append(variation_)

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
        for process_nick in selectedProcesses & {"EMB"}:
            for chname_ in selectedChannels & {"mt"}:
                variationsToAdd[chname_][process_nick].append(variation_)
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
        for process_nick in selectedProcesses & {"EMB"}:
            if "et" in selectedChannels:
                variationsToAdd["et"][process_nick].append(variation_)
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
        for process_nick in selectedProcesses & {"EMB"}:
            if "tt" in selectedChannels:
                variationsToAdd["tt"][process_nick].append(variation_)
    # 10% removed events in ttbar simulation (ttbar -> real tau tau events)
    # will be added/subtracted to ZTT shape to use as systematic

    if "EMB" in selectedProcesses:
        for chname_, ch_ in selectedChannelsTuples:
            for shift_direction, shift_ in {"Down": -0.1, "Up": 0.1}.items():
                p_ = Process(
                    "ZTTpTTTauTau" + shift_direction,
                    AddHistogramEstimationMethod(
                        "AddHistogram", "nominal", era, directory, ch_,
                        [processes[chname_]["EMB"],
                        processes[chname_]["TTT"]],
                        [1.0, shift_]))
                for cat_ in catsListD[chname_]:
                    systematics.add(
                        Systematic(
                            category=cat_,
                            process=p_,
                            analysis="smhtt",
                            era=era,
                            variation=Relabel(
                                "CMS_htt_emb_ttbar_Run{era}".format(
                                    era=args.era),
                                shift_direction),
                            mass="125"))
    if "FAKES" in selectedProcesses:
        # jetfakes
        fake_factor_variations = {}
        fake_factor_weight = {}
        for chname_ in selectedChannels & {"et", "mt"}:
            fake_factor_variations[chname_] = [
                "ff_qcd{ch}_syst{era}{shift}",
                "ff_qcd_dm0_njet0{ch}_stat{era}{shift}",
                "ff_qcd_dm0_njet1{ch}_stat{era}{shift}",
                # "ff_qcd_dm1_njet0{ch}_stat{era}{shift}",
                # "ff_qcd_dm1_njet1{ch}_stat{era}{shift}",
                "ff_w_syst{era}{shift}",
                "ff_w_dm0_njet0{ch}_stat{era}{shift}",
                "ff_w_dm0_njet1{ch}_stat{era}{shift}",
                # "ff_w_dm1_njet0{ch}_stat{era}{shift}",
                # "ff_w_dm1_njet1{ch}_stat{era}{shift}",
                "ff_tt_syst{era}{shift}",
                "ff_tt_dm0_njet0_stat{era}{shift}",
                "ff_tt_dm0_njet1_stat{era}{shift}",
                # "ff_tt_dm1_njet0_stat{era}{shift}",
                # "ff_tt_dm1_njet1_stat{era}{shift}"
            ]
            fake_factor_weight[chname_] = "ff2_{syst}"
        for chname_ in selectedChannels & {"tt"}:
            fake_factor_variations[chname_] = [
                "ff_qcd{ch}_syst{era}{shift}",
                "ff_qcd_dm0_njet0{ch}_stat{era}{shift}",
                "ff_qcd_dm0_njet1{ch}_stat{era}{shift}",
                # "ff_qcd_dm1_njet0{ch}_stat{era}{shift}",
                # "ff_qcd_dm1_njet1{ch}_stat{era}{shift}",
                "ff_w{ch}_syst{era}{shift}",
                "ff_tt{ch}_syst{era}{shift}",
                "ff_w_frac{ch}_syst{era}{shift}",
                "ff_tt_frac{ch}_syst{era}{shift}"
            ]
            fake_factor_weight[chname_] = "(0.5*ff1_{syst}*(byTightDeepTau2017v2p1VSjet_1<0.5)+0.5*ff2_{syst}*(byTightDeepTau2017v2p1VSjet_2<0.5))"
        for chname_, ch_ in selectedChannelsTuplesNoEM:
            for shift_direction in ["Up", "Down"]:
                for systematic_shift in fake_factor_variations[chname_]:
                    hname_ = "CMS_" + systematic_shift.format(
                        ch="_" + chname_, shift="", era="_Run" + args.era).replace("_dm0", "")
                    systname_ = systematic_shift.format(
                        ch="",
                        shift="_" + shift_direction.lower(),
                        era=""
                    )
                    variation_ = ReplaceWeight(
                        hname_, "fake_factor", Weight(
                            fake_factor_weight[chname_].format(
                                syst=systname_), "fake_factor"), shift_direction)
                    variationsToAdd[chname_]["FAKES"].append(variation_)

    # QCD for em
    qcd_variations = []
    for shift_direction in ["up", "down"]:
        qcd_variations.append(
            ReplaceWeight(
                "CMS_htt_qcd_0jet_rate_Run{era}".format(era=args.era),
                "qcd_weight",
                Weight("em_qcd_osss_0jet_rate{}_Weight".format(shift_direction), "qcd_weight"),
                shift_direction.capitalize(),
            )
        )
        qcd_variations.append(
            ReplaceWeight(
                "CMS_htt_qcd_0jet_shape_Run{era}".format(era=args.era),
                "qcd_weight",
                Weight("em_qcd_osss_0jet_shape{}_Weight".format(shift_direction), "qcd_weight"),
                shift_direction.capitalize(),
            )
        )
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
                "CMS_htt_qcd_2jet_rate_Run{era}".format(
                    era=args.era),
                "qcd_weight",
                Weight(
                    "em_qcd_osss_2jet_rate" +
                    shift_direction +
                    "_Weight",
                    "qcd_weight"),
                shift_direction.capitalize()))
        qcd_variations.append(
            ReplaceWeight(
                "CMS_htt_qcd_2jet_shape_Run{era}".format(
                    era=args.era),
                "qcd_weight",
                Weight(
                    "em_qcd_osss_2jet_shape" +
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
        for process_nick in selectedProcesses & {"QCD"}:
            if "em" in selectedChannels:
                variationsToAdd["em"][process_nick].append(variation_)

    # Gluon-fusion WG1 uncertainty scheme
    ggh_variations = []
    for unc in [
            "THU_ggH_Mig01",
            "THU_ggH_Mig12",
            "THU_ggH_Mu",
            "THU_ggH_PT120",
            "THU_ggH_PT60",
            "THU_ggH_Res",
            "THU_ggH_VBF2j",
            "THU_ggH_VBF3j",
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
        for process_nick in selectedProcesses & {
                nick for nick in signal_nicks
                if "ggH" in nick and "HWW" not in nick
        }:
            for chname_ in selectedChannels:
                variationsToAdd[chname_][process_nick].append(variation_)

# VBF uncertainties
    qqh_variations = []
    for unc in [
        "THU_qqH_25",
        "THU_qqH_JET01",
        "THU_qqH_Mjj1000",
        "THU_qqH_Mjj120",
        "THU_qqH_Mjj1500",
        "THU_qqH_Mjj350",
        "THU_qqH_Mjj60",
        "THU_qqH_Mjj700",
        "THU_qqH_PTH200",
        "THU_qqH_TOT",
    ]:
        qqh_variations.append(
            AddWeight(
                unc,
                "{}_weight".format(unc),
                Weight("({})".format(unc), "{}_weight".format(unc)),
                "Up",
            )
        )
        qqh_variations.append(
            AddWeight(
                unc,
                "{}_weight".format(unc),
                Weight("(2.0-{})".format(unc), "{}_weight".format(unc)),
                "Down",
            )
        )

    for variation_ in qqh_variations:
        for process_nick in selectedProcesses & {
                nick for nick in signal_nicks
                if "qqH" in nick and "qqHWW" not in nick
        }:
            for chname_ in selectedChannels:
                variationsToAdd[chname_][process_nick].append(variation_)




    # add all variation from the systematics
    for chname_, ch_ in selectedChannelsTuples:
        for process_nick in processes[chname_]:
            for variation_ in variationsToAdd[chname_][process_nick]:
                systematics.add_systematic_variation(
                    variation=variation_,
                    process=processes[chname_][process_nick],
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
