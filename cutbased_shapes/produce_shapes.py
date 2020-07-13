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
from shape_producer.channel import MSSMvsSMET2016, MSSMvsSMMT2016, MSSMvsSMTT2016, MSSMvsSMEM2016, MSSMvsSMET2017, MSSMvsSMMT2017, MSSMvsSMTT2017, MSSMvsSMEM2017, MSSMvsSMET2018, MSSMvsSMMT2018, MSSMvsSMTT2018, MSSMvsSMEM2018

from itertools import product

import argparse
import yaml
import copy
import numpy as np
import sys
import json

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
    parser = argparse.ArgumentParser(description="Produce shapes for MSSM analysis.")

    parser.add_argument("--directory", required=True, type=str, help="Directory with Artus outputs.")
    parser.add_argument("--et-friend-directory", type=str, default=[], nargs="+", help= "Directories arranged as Artus output and containing a friend tree for et.")
    parser.add_argument("--mt-friend-directory", type=str, default=[], nargs="+", help="Directories arranged as Artus output and containing a friend tree for mt.")
    parser.add_argument("--tt-friend-directory", type=str, default=[], nargs="+", help= "Directories arranged as Artus output and containing a friend tree for tt." )
    parser.add_argument("--em-friend-directory", type=str, default=[], nargs="+", help= "Directories arranged as Artus output and containing a friend tree for em." )
    parser.add_argument("--fake-factor-friend-directory", default=None, type=str, help= "Directory arranged as Artus output and containing friend trees to data files with fake factors." )
    parser.add_argument("--datasets", required=True, type=str, help="Kappa datsets database.")
    parser.add_argument("--binning", required=True, type=str, help="Binning configuration.")
    parser.add_argument("--channels",default=[],nargs='+',type=str,help="Channels to be considered.")
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument("--discriminator-variable",type=str,help="Variable chosen as final discriminator for cut-based analysis.")
    parser.add_argument("--num-threads",default=32,type=int,help="Number of threads to be used.")
    parser.add_argument("--backend",default="classic",choices=["classic", "tdf"],type=str,help="Backend. Use classic or tdf.")
    parser.add_argument("--tag", default="ERA_CHANNEL", type=str, help="Tag of output files.")
    parser.add_argument("--skip-systematic-variations",action="store_true",help="Do not produce the systematic variations.")
    parser.add_argument("--process",default=None,type=str,help="Explicit process to be considered within the shape production")
    parser.add_argument("--category",default="nobtag",type=str,help="Category to be considered within the shape production")
    return parser.parse_args()


def main(args):
    # Container for all distributions to be drawn
    logger.info("Set up shape variations.")
    systematics = Systematics("{}_cutbased_shapes_{}.root".format(args.tag,args.discriminator_variable),num_threads=args.num_threads,skip_systematic_variations=args.skip_systematic_variations)

    # Era selection
    if "2016" in args.era:
        from shape_producer.estimation_methods_2016 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, TTLEstimation, TTTEstimation, VVLEstimation, WEstimation, ggHEstimation, qqHEstimation, WHEstimation, ZHEstimation, ttHEstimation, ggHWWEstimation, qqHWWEstimation, WHWWEstimation, ZHWWEstimation, SUSYggHEstimation, SUSYbbHEstimation, QCDEstimation_SStoOS_MTETEM, NewFakeEstimationLT, NewFakeEstimationTT

        from shape_producer.era import Run2016
        era = Run2016(args.datasets)
    elif "2017" in args.era:
        from shape_producer.estimation_methods_2017 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, TTLEstimation, TTTEstimation, VVLEstimation, WEstimation, ggHEstimation, qqHEstimation, WHEstimation, ZHEstimation, ttHEstimation, ggHWWEstimation, qqHWWEstimation, WHWWEstimation, ZHWWEstimation, SUSYggHEstimation, SUSYbbHEstimation, QCDEstimation_SStoOS_MTETEM, NewFakeEstimationLT, NewFakeEstimationTT

        from shape_producer.era import Run2017
        era = Run2017(args.datasets)
    elif "2018" in args.era:
        from shape_producer.estimation_methods_2018 import DataEstimation, ZTTEstimation, ZTTEmbeddedEstimation, ZLEstimation, TTLEstimation, TTTEstimation, VVLEstimation, WEstimation, ggHEstimation, qqHEstimation, WHEstimation, ZHEstimation, ttHEstimation, ggHWWEstimation, qqHWWEstimation, WHWWEstimation, ZHWWEstimation, SUSYggHEstimation, SUSYbbHEstimation, QCDEstimation_SStoOS_MTETEM, NewFakeEstimationLT, NewFakeEstimationTT

        from shape_producer.era import Run2018
        era = Run2018(args.datasets)
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
        "2016": {
            "mt" : MSSMvsSMMT2016(),
            "et" : MSSMvsSMET2016(),
            "tt" : MSSMvsSMTT2016(),
            "em" : MSSMvsSMEM2016(),
            },
        "2017": {
            "mt" : MSSMvsSMMT2017(),
            "et" : MSSMvsSMET2017(),
            "tt" : MSSMvsSMTT2017(),
            "em" : MSSMvsSMEM2017(),
            },
        "2018": {
            "mt" : MSSMvsSMMT2018(),
            "et" : MSSMvsSMET2018(),
            "tt" : MSSMvsSMTT2018(),
            "em" : MSSMvsSMEM2018(),
            }
    }

    mass_dict = {
        "2016": {
            "ggH": [80, 90, 100, 110, 120, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "bbH_nlo": [80, 90, 110, 120, 130, 140, 160, 180, 200, 250, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
        },
        "2017": {
            "ggH": [80, 90, 100, 110, 120, 130, 140, 180, 200, 250, 300, 350, 400, 450, 600, 700, 800, 900, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "bbH_nlo": [80, 90, 110, 120, 125, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200, 3500],
        },
        "2018": {
            "ggH": [80, 90, 100, 110, 120, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 600, 700, 800, 900, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "bbH_nlo": [80, 90, 100, 110, 120, 125, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200, 3500],
        }
    }
    susyggH_masses = mass_dict[args.era]["ggH"]
    susybbH_masses = mass_dict[args.era]["bbH_nlo"]

    processes = {
        "mt" : {},
        "et" : {},
        "tt" : {},
        "em" : {},
    }

    for ch in args.channels:

        # common processes
        processes[ch]["data_obs"] = Process("data_obs", DataEstimation         (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
        processes[ch]["EMB"]  = Process("EMB",      ZTTEmbeddedEstimation  (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
        processes[ch]["ZL"]   = Process("ZL",       ZLEstimation           (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
        processes[ch]["TTL"]  = Process("TTL",      TTLEstimation          (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
        processes[ch]["VVL"]  = Process("VVL",      VVLEstimation          (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))

        processes[ch]["WH125"]   = Process("WH125",    WHEstimation        (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
        processes[ch]["ZH125"]   = Process("ZH125",    ZHEstimation        (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
        processes[ch]["ttH125"]  = Process("ttH125",   ttHEstimation       (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))

        processes[ch]["WHWW125"] = Process("WHWW125",   WHWWEstimation     (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
        processes[ch]["ZHWW125"] = Process("ZHWW125",   ZHWWEstimation     (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
        processes[ch]["ggHWW125"] = Process("ggHWW125", ggHWWEstimation    (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
        processes[ch]["qqHWW125"] = Process("qqHWW125", qqHWWEstimation    (era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))

        # mssm ggH and bbH signals
        gghfraction_corrections = json.load(open("cutbased_shapes/ggphi_contirbution_weights.json","r"))
        for ggH_contribution in ["ggh_t", "ggh_b", "ggh_i", "ggH_t", "ggH_b", "ggH_i", "ggA_t", "ggA_b", "ggA_i"]:
            for m in susyggH_masses:
                name = ggH_contribution + "_" + str(m)
                weight = gghfraction_corrections[args.era][str(m)][ggH_contribution]
                processes[ch][name] = Process(name, SUSYggHEstimation(era, directory, channel_dict[args.era][ch], str(m), ggH_contribution, weight, friend_directory=friend_directories[ch]))
        for m in susybbH_masses:
            name = "bbH_" + str(m)
            processes[ch][name] = Process(name, SUSYbbHEstimation(era, directory, channel_dict[args.era][ch], str(m), friend_directory=friend_directories[ch]))

        ## stage 0 and stage 1.1 ggh and qqh
        for ggH_htxs in ggHEstimation.htxs_dict:
            processes[ch][ggH_htxs] = Process(ggH_htxs, ggHEstimation(ggH_htxs, era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
        for qqH_htxs in qqHEstimation.htxs_dict:
            processes[ch][qqH_htxs] = Process(qqH_htxs, qqHEstimation(qqH_htxs, era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))

        # channel-specific processes
        qcd_weight_string = "1."
        qcd_aisoiso_string = "*(1.0)"
        if ch in ["mt", "et"]:
            processes[ch]["jetFakes"] = Process("jetFakes", NewFakeEstimationLT(era, directory, channel_dict[args.era][ch], [processes[ch][process] for process in ["EMB", "ZL", "TTL", "VVL"]], processes[ch]["data_obs"], friend_directory=friend_directories[ch]+[ff_friend_directory]))
        elif ch == "tt":
            processes[ch]["jetFakes"] = Process("jetFakes", NewFakeEstimationTT(era, directory, channel_dict[args.era][ch], [processes[ch][process] for process in ["EMB", "ZL", "TTL", "VVL"]], processes[ch]["data_obs"], friend_directory=friend_directories[ch]+[ff_friend_directory]))
        elif ch == "em":
            processes[ch]["W"]   = Process("W",   WEstimation(era, directory, channel_dict[args.era][ch], friend_directory=friend_directories[ch]))
            ROOT.v5.TFormula.SetMaxima(3000)
            if args.era == "2016":
                qcd_aisoiso_string = "*(1.0*(pt_1>=150.0||pt_2>=150.0)+0.889611*(pt_1>=0.0&&pt_1<20.0&&pt_2>=20.0&&pt_2<25.0)+0.906323*(pt_1>=0.0&&pt_1<20.0&&pt_2>=25.0&&pt_2<30.0)+0.838287*(pt_1>=0.0&&pt_1<20.0&&pt_2>=30.0&&pt_2<150.0)+0.900872*(pt_1>=20.0&&pt_1<25.0&&pt_2>=0.0&&pt_2<20.0)+0.918876*(pt_1>=20.0&&pt_1<25.0&&pt_2>=20.0&&pt_2<25.0)+0.857904*(pt_1>=20.0&&pt_1<25.0&&pt_2>=25.0&&pt_2<30.0)+0.833439*(pt_1>=20.0&&pt_1<25.0&&pt_2>=30.0&&pt_2<150.0)+0.956127*(pt_1>=25.0&&pt_1<30.0&&pt_2>=0.0&&pt_2<20.0)+0.863690*(pt_1>=25.0&&pt_1<30.0&&pt_2>=20.0&&pt_2<25.0)+1.060816*(pt_1>=25.0&&pt_1<30.0&&pt_2>=25.0&&pt_2<30.0)+0.938181*(pt_1>=25.0&&pt_1<30.0&&pt_2>=30.0&&pt_2<150.0)+0.993274*(pt_1>=30.0&&pt_1<150.0&&pt_2>=0.0&&pt_2<20.0)+0.936018*(pt_1>=30.0&&pt_1<150.0&&pt_2>=20.0&&pt_2<25.0)+0.864106*(pt_1>=30.0&&pt_1<150.0&&pt_2>=25.0&&pt_2<30.0)+0.954102*(pt_1>=30.0&&pt_1<150.0&&pt_2>=30.0&&pt_2<150.0))"
                qcd_weight_string = "((-0.1138*(njets==0)+(-0.07938)*(njets==1)+(-0.02602)*(njets>=2))*((DiTauDeltaR-3.0)**2.0-3.0)+(-0.2287*(njets==0)+(-0.3251)*(njets==1)+(-0.2802)*(njets>=2))*(DiTauDeltaR-3.0)+(1.956*(njets==0)+(1.890)*(njets==1)+(1.753)*(njets>=2)))*(1.0*(pt_1>=150.0||pt_2>=150.0)+1.132149*(pt_1>=0.0&&pt_1<24.0&&pt_2>=24.0&&pt_2<30.0)+1.118163*(pt_1>=0.0&&pt_1<24.0&&pt_2>=30.0&&pt_2<40.0)+1.142240*(pt_1>=0.0&&pt_1<24.0&&pt_2>=40.0&&pt_2<150.0)+1.004560*(pt_1>=24.0&&pt_1<30.0&&pt_2>=0.0&&pt_2<24.0)+1.055802*(pt_1>=24.0&&pt_1<30.0&&pt_2>=24.0&&pt_2<30.0)+1.171731*(pt_1>=24.0&&pt_1<30.0&&pt_2>=30.0&&pt_2<40.0)+1.351143*(pt_1>=24.0&&pt_1<30.0&&pt_2>=40.0&&pt_2<150.0)+0.921943*(pt_1>=30.0&&pt_1<40.0&&pt_2>=0.0&&pt_2<24.0)+1.078412*(pt_1>=30.0&&pt_1<40.0&&pt_2>=24.0&&pt_2<30.0)+1.096989*(pt_1>=30.0&&pt_1<40.0&&pt_2>=30.0&&pt_2<40.0)+1.222142*(pt_1>=30.0&&pt_1<40.0&&pt_2>=40.0&&pt_2<150.0)+0.848351*(pt_1>=40.0&&pt_1<150.0&&pt_2>=0.0&&pt_2<24.0)+0.852887*(pt_1>=40.0&&pt_1<150.0&&pt_2>=24.0&&pt_2<30.0)+0.891202*(pt_1>=40.0&&pt_1<150.0&&pt_2>=30.0&&pt_2<40.0)+0.913323*(pt_1>=40.0&&pt_1<150.0&&pt_2>=40.0&&pt_2<150.0))%s"%qcd_aisoiso_string
            elif args.era == "2017":
                qcd_aisoiso_string = "*(1.0*(pt_1>=150.0||pt_2>=150.0)+0.878304*(pt_1>=0.0&&pt_1<20.0&&pt_2>=20.0&&pt_2<25.0)+0.916277*(pt_1>=0.0&&pt_1<20.0&&pt_2>=25.0&&pt_2<30.0)+0.853211*(pt_1>=0.0&&pt_1<20.0&&pt_2>=30.0&&pt_2<150.0)+0.920458*(pt_1>=20.0&&pt_1<25.0&&pt_2>=0.0&&pt_2<20.0)+0.872271*(pt_1>=20.0&&pt_1<25.0&&pt_2>=20.0&&pt_2<25.0)+0.957983*(pt_1>=20.0&&pt_1<25.0&&pt_2>=25.0&&pt_2<30.0)+0.910988*(pt_1>=20.0&&pt_1<25.0&&pt_2>=30.0&&pt_2<150.0)+0.935900*(pt_1>=25.0&&pt_1<30.0&&pt_2>=0.0&&pt_2<20.0)+0.903964*(pt_1>=25.0&&pt_1<30.0&&pt_2>=20.0&&pt_2<25.0)+0.888112*(pt_1>=25.0&&pt_1<30.0&&pt_2>=25.0&&pt_2<30.0)+0.872235*(pt_1>=25.0&&pt_1<30.0&&pt_2>=30.0&&pt_2<150.0)+0.927075*(pt_1>=30.0&&pt_1<150.0&&pt_2>=0.0&&pt_2<20.0)+0.983504*(pt_1>=30.0&&pt_1<150.0&&pt_2>=20.0&&pt_2<25.0)+0.921924*(pt_1>=30.0&&pt_1<150.0&&pt_2>=25.0&&pt_2<30.0)+0.881401*(pt_1>=30.0&&pt_1<150.0&&pt_2>=30.0&&pt_2<150.0))"
                qcd_weight_string = "((-0.1430*(njets==0)+(-0.05544)*(njets==1)+(0.03128)*(njets>=2))*((DiTauDeltaR-3.0)**2.0-3.0)+(-0.1949*(njets==0)+(-0.3685)*(njets==1)+(-0.3531)*(njets>=2))*(DiTauDeltaR-3.0)+(1.928*(njets==0)+(2.020)*(njets==1)+(1.855)*(njets>=2)))*(1.0*(pt_1>=150.0||pt_2>=150.0)+1.155767*(pt_1>=0.0&&pt_1<24.0&&pt_2>=24.0&&pt_2<30.0)+1.136188*(pt_1>=0.0&&pt_1<24.0&&pt_2>=30.0&&pt_2<40.0)+1.163907*(pt_1>=0.0&&pt_1<24.0&&pt_2>=40.0&&pt_2<150.0)+0.988366*(pt_1>=24.0&&pt_1<30.0&&pt_2>=0.0&&pt_2<24.0)+1.198820*(pt_1>=24.0&&pt_1<30.0&&pt_2>=24.0&&pt_2<30.0)+1.134818*(pt_1>=24.0&&pt_1<30.0&&pt_2>=30.0&&pt_2<40.0)+1.051062*(pt_1>=24.0&&pt_1<30.0&&pt_2>=40.0&&pt_2<150.0)+0.917948*(pt_1>=30.0&&pt_1<40.0&&pt_2>=0.0&&pt_2<24.0)+1.042672*(pt_1>=30.0&&pt_1<40.0&&pt_2>=24.0&&pt_2<30.0)+0.973973*(pt_1>=30.0&&pt_1<40.0&&pt_2>=30.0&&pt_2<40.0)+1.143160*(pt_1>=30.0&&pt_1<40.0&&pt_2>=40.0&&pt_2<150.0)+0.845711*(pt_1>=40.0&&pt_1<150.0&&pt_2>=0.0&&pt_2<24.0)+0.853038*(pt_1>=40.0&&pt_1<150.0&&pt_2>=24.0&&pt_2<30.0)+0.890487*(pt_1>=40.0&&pt_1<150.0&&pt_2>=30.0&&pt_2<40.0)+1.037247*(pt_1>=40.0&&pt_1<150.0&&pt_2>=40.0&&pt_2<150.0))%s"%qcd_aisoiso_string
            elif args.era == "2018":
                qcd_aisoiso_string = "*(1.0*(pt_1>=150.0||pt_2>=150.0)+0.847702*(pt_1>=0.0&&pt_1<20.0&&pt_2>=20.0&&pt_2<25.0)+0.878120*(pt_1>=0.0&&pt_1<20.0&&pt_2>=25.0&&pt_2<30.0)+0.887496*(pt_1>=0.0&&pt_1<20.0&&pt_2>=30.0&&pt_2<150.0)+0.874935*(pt_1>=20.0&&pt_1<25.0&&pt_2>=0.0&&pt_2<20.0)+0.829801*(pt_1>=20.0&&pt_1<25.0&&pt_2>=20.0&&pt_2<25.0)+0.922954*(pt_1>=20.0&&pt_1<25.0&&pt_2>=25.0&&pt_2<30.0)+0.954270*(pt_1>=20.0&&pt_1<25.0&&pt_2>=30.0&&pt_2<150.0)+0.935953*(pt_1>=25.0&&pt_1<30.0&&pt_2>=0.0&&pt_2<20.0)+0.908383*(pt_1>=25.0&&pt_1<30.0&&pt_2>=20.0&&pt_2<25.0)+0.927804*(pt_1>=25.0&&pt_1<30.0&&pt_2>=25.0&&pt_2<30.0)+0.917511*(pt_1>=25.0&&pt_1<30.0&&pt_2>=30.0&&pt_2<150.0)+0.983508*(pt_1>=30.0&&pt_1<150.0&&pt_2>=0.0&&pt_2<20.0)+0.952974*(pt_1>=30.0&&pt_1<150.0&&pt_2>=20.0&&pt_2<25.0)+0.945860*(pt_1>=30.0&&pt_1<150.0&&pt_2>=25.0&&pt_2<30.0)+0.858417*(pt_1>=30.0&&pt_1<150.0&&pt_2>=30.0&&pt_2<150.0))"
                qcd_weight_string = "((-0.1249*(njets==0)+(-0.04374)*(njets==1)+(-0.00606)*(njets>=2))*((DiTauDeltaR-3.0)**2.0-3.0)+(-0.1644*(njets==0)+(-0.3172)*(njets==1)+(-0.3627)*(njets>=2))*(DiTauDeltaR-3.0)+(1.963*(njets==0)+(2.014)*(njets==1)+(1.757)*(njets>=2)))*(1.0*(pt_1>=150.0||pt_2>=150.0)+1.163939*(pt_1>=0.0&&pt_1<24.0&&pt_2>=24.0&&pt_2<30.0)+1.128795*(pt_1>=0.0&&pt_1<24.0&&pt_2>=30.0&&pt_2<40.0)+1.083493*(pt_1>=0.0&&pt_1<24.0&&pt_2>=40.0&&pt_2<150.0)+1.006878*(pt_1>=24.0&&pt_1<30.0&&pt_2>=0.0&&pt_2<24.0)+1.078046*(pt_1>=24.0&&pt_1<30.0&&pt_2>=24.0&&pt_2<30.0)+1.080539*(pt_1>=24.0&&pt_1<30.0&&pt_2>=30.0&&pt_2<40.0)+1.080385*(pt_1>=24.0&&pt_1<30.0&&pt_2>=40.0&&pt_2<150.0)+0.930821*(pt_1>=30.0&&pt_1<40.0&&pt_2>=0.0&&pt_2<24.0)+1.077226*(pt_1>=30.0&&pt_1<40.0&&pt_2>=24.0&&pt_2<30.0)+1.030334*(pt_1>=30.0&&pt_1<40.0&&pt_2>=30.0&&pt_2<40.0)+0.940508*(pt_1>=30.0&&pt_1<40.0&&pt_2>=40.0&&pt_2<150.0)+0.836243*(pt_1>=40.0&&pt_1<150.0&&pt_2>=0.0&&pt_2<24.0)+0.878972*(pt_1>=40.0&&pt_1<150.0&&pt_2>=24.0&&pt_2<30.0)+0.867798*(pt_1>=40.0&&pt_1<150.0&&pt_2>=30.0&&pt_2<40.0)+0.910642*(pt_1>=40.0&&pt_1<150.0&&pt_2>=40.0&&pt_2<150.0))%s"%qcd_aisoiso_string
            qcd_weight = Weight(qcd_weight_string, "qcd_weight")
            processes[ch]["QCD"] = Process("QCD", QCDEstimation_SStoOS_MTETEM(era, directory, channel_dict[args.era][ch], [processes[ch][process] for process in ["EMB", "ZL", "W", "VVL", "TTL"]], processes[ch]["data_obs"], friend_directory=friend_directories[ch], extrapolation_factor=1.0, qcd_weight = qcd_weight))

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
        categories[ch].append(Category(args.category, channel_dict[args.era][ch], cuts, variable=discriminator))


    # Choice of activated signal processes
    sm_htt_backgrounds_nicks = ["WH125", "ZH125", "ttH125"]
    sm_hww_nicks = ["ggHWW125", "qqHWW125", "WHWW125", "ZHWW125"]
    sm_htt_signals_nicks = [ggH_htxs for ggH_htxs in ggHEstimation.htxs_dict] + [qqH_htxs for qqH_htxs in qqHEstimation.htxs_dict]
    susy_nicks = []
    for ggH_contribution in ["ggh_t", "ggh_b", "ggh_i", "ggH_t", "ggH_b", "ggH_i", "ggA_t", "ggA_b", "ggA_i"]:
        for m in susyggH_masses:
            susy_nicks.append(ggH_contribution + "_" + str(m))
    for m in susybbH_masses:
        susy_nicks.append("bbH_" + str(m))

    signal_nicks = sm_htt_backgrounds_nicks + sm_hww_nicks + sm_htt_signals_nicks + susy_nicks

    # Nominal histograms
    for ch in args.channels:
        for (process_name, process), category in product(processes[ch].items(), categories[ch]):
            if args.process == process_name:
                systematics.add(Systematic(category=category, process=process, analysis="mssmvssm", era=era, variation=Nominal(), mass="125"))

    # Setup shapes variations

    # EMB: 10% removed events in ttbar simulation (ttbar -> real tau tau events) will be added/subtracted to EMB shape to use as systematic. Technical procedure different to usual systematic variations
    if args.process == "EMB" and not args.skip_systematic_variations:
        for ch in args.channels:
            processes[ch]['ZTTpTTTauTauDown'] = Process("ZTTpTTTauTauDown", AddHistogramEstimationMethod("AddHistogram", "nominal", era, directory, channel_dict[args.era][ch], [processes[ch]["EMB"], processes[ch]["TTT"]], [1.0, -0.1]))
            processes[ch]['ZTTpTTTauTauUp'] = Process("ZTTpTTTauTauUp", AddHistogramEstimationMethod("AddHistogram", "nominal", era, directory, channel_dict[args.era][ch], [processes[ch]["EMB"], processes[ch]["TTT"]], [1.0, 0.1]))
            for category in categories[ch]:
                for updownvar in ["Down", "Up"]:
                    systematics.add(Systematic(category=category, process=processes[ch]['ZTTpTTTauTau%s'%updownvar], analysis="mssmvssm", era=era, variation=Relabel("CMS_htt_emb_ttbar_{}".format(args.era), updownvar), mass="125"))

    # Prefiring weights
    if "2018" in args.era:
        prefiring_variations = []
    else:
        prefiring_variations = [
            ReplaceWeight("CMS_prefiring_{}".format(args.era), "prefireWeight", Weight("prefiringweightup", "prefireWeight"),"Up"),
            ReplaceWeight("CMS_prefiring_{}".format(args.era), "prefireWeight", Weight("prefiringweightdown", "prefireWeight"),"Down"),
        ]

    # Split JES shapes
    jet_es_variations = create_systematic_variations("CMS_scale_j_Absolute", "jecUncAbsolute", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_Absolute_{}".format(args.era), "jecUncAbsoluteYear", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_BBEC1", "jecUncBBEC1", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_BBEC1_{}".format(args.era), "jecUncBBEC1Year", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_EC2", "jecUncEC2", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_EC2_{}".format(args.era), "jecUncEC2Year", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_FlavorQCD", "jecUncFlavorQCD", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_HF", "jecUncHF", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_HF_{}".format(args.era), "jecUncHFYear", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_RelativeBal", "jecUncRelativeBal", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_scale_j_RelativeSample_{}".format(args.era), "jecUncRelativeSampleYear", DifferentPipeline)
    jet_es_variations += create_systematic_variations("CMS_res_j_{}".format(args.era), "jerUnc", DifferentPipeline)

    # B-tagging
    btag_eff_variations = create_systematic_variations("CMS_htt_eff_b_{}".format(args.era), "btagEff", DifferentPipeline)
    mistag_eff_variations = create_systematic_variations("CMS_htt_mistag_b_{}".format(args.era), "btagMistag", DifferentPipeline)

    # Variations common for all groups (most of the mc-related systematics)
    common_mc_variations = prefiring_variations + btag_eff_variations + mistag_eff_variations + jet_es_variations

    # MET energy scale. Note: only those variations for non-resonant processes are used in the stat. inference
    met_unclustered_variations = create_systematic_variations("CMS_scale_met_unclustered_{}".format(args.era), "metUnclusteredEn", DifferentPipeline)

    # Recoil correction unc, for resonant processes
    recoil_variations = create_systematic_variations("CMS_htt_boson_reso_met_{}".format(args.era), "metRecoilResolution", DifferentPipeline)
    recoil_variations += create_systematic_variations("CMS_htt_boson_scale_met_{}".format(args.era), "metRecoilResponse", DifferentPipeline)

    # Tau energy scale (general, MC-specific & EMB-specific), it is mt, et & tt specific
    tau_es_variations = {}

    for unctype in ["", "_emb"]:
        tau_es_variations[unctype] = create_systematic_variations("CMS_scale_t%s_3prong_%s"% (unctype, args.era), "tauEsThreeProng", DifferentPipeline)
        tau_es_variations[unctype] += create_systematic_variations("CMS_scale_t%s_3prong1pizero_%s"% (unctype, args.era), "tauEsThreeProngOnePiZero", DifferentPipeline)
        tau_es_variations[unctype] += create_systematic_variations("CMS_scale_t%s_1prong_%s"% (unctype, args.era), "tauEsOneProng", DifferentPipeline)
        tau_es_variations[unctype] += create_systematic_variations("CMS_scale_t%s_1prong1pizero_%s"% (unctype, args.era), "tauEsOneProngOnePiZero", DifferentPipeline)

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
                    for shift_direction in ["Up","Down"]:
                        bindown = ptbin
                        binup = pt[i+1]
                        if binup == "inf":
                            tau_id_variations[ch][unctype].append(
                                    ReplaceWeight("CMS_eff_t{unctype}_{bindown}-{binup}_{era}".format(unctype=unctype,bindown=bindown, binup=binup, era=args.era), "taubyIsoIdWeight",
                                        Weight("(pt_2 >= {bindown})*tauIDScaleFactorWeight{shift_direction}_tight_DeepTau2017v2p1VSjet_2 + (pt_2 < {bindown})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2".format(bindown=bindown,shift_direction=shift_direction), "taubyIsoIdWeight"), shift_direction))
                        else:
                            tau_id_variations[ch][unctype].append(
                                    ReplaceWeight("CMS_eff_t{unctype}_{bindown}-{binup}_{era}".format(unctype=unctype, bindown=bindown, binup=binup, era=args.era), "taubyIsoIdWeight",
                                        Weight("(pt_2 >= {bindown} && pt_2 < {binup})*tauIDScaleFactorWeight{shift_direction}_tight_DeepTau2017v2p1VSjet_2 + (pt_2 < {bindown} || pt_2 >= {binup})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2".format(bindown=bindown, binup=binup, shift_direction=shift_direction),"taubyIsoIdWeight"), shift_direction))
            if ch in ["tt"]:
                for shift_direction in ["Up", "Down"]:
                    for decaymode in [0, 10, 11]:
                        tau_id_variations[ch][unctype].append(
                                    ReplaceWeight("CMS_eff_t{unctype}_dm{dm}_{era}".format(unctype=unctype, dm=decaymode, era=args.era), "taubyIsoIdWeight",
                                        Weight("((decayMode_1=={dm})*tauIDScaleFactorWeight{shift_direction}_tight_DeepTau2017v2p1VSjet_1 + (decayMode_1!={dm})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1)*((decayMode_2=={dm})*tauIDScaleFactorWeight{shift_direction}_tight_DeepTau2017v2p1VSjet_2 + (decayMode_2!={dm})*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2)".format(dm=decaymode,shift_direction=shift_direction), "taubyIsoIdWeight"), shift_direction))
                    # decaymodes in {1,2} handled as DM = 1
                    tau_id_variations[ch][unctype].append(
                                ReplaceWeight("CMS_eff_t{unctype}_dm{dm}_{era}".format(unctype=unctype, dm=1, era=args.era), "taubyIsoIdWeight",
                                    Weight("((decayMode_1==1 || decayMode_1==2)*tauIDScaleFactorWeight{shift_direction}_tight_DeepTau2017v2p1VSjet_1 + (decayMode_1!=1 && decayMode_1!=2)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1)*((decayMode_2==1 || decayMode_2==2)*tauIDScaleFactorWeight{shift_direction}_tight_DeepTau2017v2p1VSjet_2 + (decayMode_2!=1 && decayMode_2!=2)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2)".format(shift_direction=shift_direction), "taubyIsoIdWeight"), shift_direction))

    # Ele energy scale & smear uncertainties (MC-specific), it is et & em specific
    ele_es_variations = create_systematic_variations("CMS_scale_e", "eleScale", DifferentPipeline)
    ele_es_variations += create_systematic_variations("CMS_res_e", "eleSmear", DifferentPipeline)
    # Ele energy scale (EMB-specific), it is et & em specific
    ele_es_emb_variations = create_systematic_variations("CMS_scale_e_emb", "eleEs", DifferentPipeline)

    # Z pt reweighting
    zpt_variations = []
    if args.era in ['2017', '2018']:
        zpt_variations = create_systematic_variations("CMS_htt_dyShape", "zPtReweightWeight", SquareAndRemoveWeight)
    elif args.era == '2016':
        zpt_variations = create_systematic_variations("CMS_htt_dyShape_{}".format(args.era), "zPtReweightWeight", SquareAndRemoveWeight)

    # top pt reweighting
    top_pt_variations = create_systematic_variations("CMS_htt_ttbarShape", "topPtReweightWeight", SquareAndRemoveWeight)

    # jet to tau fake efficiency
    # Needs to be introduced if one wants to create shapes for QCD
    # Applied to lt,tt channels for processes ZJ, TTJ, VVJ, W
    # value of weight: Up max(1-pt_2*0.002, 0.6)
    #                   Down min(1+pt_2*0.002, 1.4)

    # EMB charged track correction uncertainty (DM-dependent)
    decayMode_variations = []
    for shift_direction in ["Up","Down"]:
        decayMode_variations.append(ReplaceWeight("CMS_3ProngEff_{}".format(args.era), "decayMode_SF", Weight("embeddedDecayModeWeight_eff{shift_direction}_pi0Nom".format(shift_direction=shift_direction), "decayMode_SF"), shift_direction))
        decayMode_variations.append(ReplaceWeight("CMS_1ProngPi0Eff_{}".format(args.era), "decayMode_SF", Weight("embeddedDecayModeWeight_effNom_pi0{shift_direction}".format(shift_direction=shift_direction), "decayMode_SF"), shift_direction))

    # QCD for em
    qcd_parameters = {
        "p0" : { # constant parameter
            "2016" : {
                "0j" : {"Nom": "1.956", "Up": "2.018", "Down": "1.894"},
                "1j" : {"Nom": "1.890", "Up": "1.930", "Down": "1.850"},
                "2j" : {"Nom": "1.753", "Up": "1.814", "Down": "1.692"},
            },
            "2017" : {
                "0j" : {"Nom": "1.928", "Up": "1.993", "Down": "1.863"},
                "1j" : {"Nom": "2.020", "Up": "2.060", "Down": "1.980"},
                "2j" : {"Nom": "1.855", "Up": "1.914", "Down": "1.796"},
            },
            "2018" : {
                "0j" : {"Nom": "1.963", "Up": "2.010", "Down": "1.916"},
                "1j" : {"Nom": "2.014", "Up": "2.045", "Down": "1.983"},
                "2j" : {"Nom": "1.757", "Up": "1.794", "Down": "1.720"},
            }
        },
        "p1" : { # linear parameter
            "2016" : {
                "0j" : {"Nom": "-0.2287", "Up": "-0.1954", "Down": "-0.262"},
                "1j" : {"Nom": "-0.3251", "Up": "-0.2972", "Down": "-0.353"},
                "2j" : {"Nom": "-0.2802", "Up": "-0.2402", "Down": "-0.3202"},
            },
            "2017" : {
                "0j" : {"Nom": "-0.1949", "Up": "-0.1617", "Down": "-0.2281"},
                "1j" : {"Nom": "-0.3685", "Up": "-0.3445", "Down": "-0.3925"},
                "2j" : {"Nom": "-0.3531", "Up": "-0.3154", "Down": "-0.3908"},
            },
            "2018" : {
                "0j" : {"Nom": "-0.1644", "Up": "-0.1402", "Down": "-0.1886"},
                "1j" : {"Nom": "-0.3172", "Up": "-0.2977", "Down": "-0.3367"},
                "2j" : {"Nom": "-0.3627", "Up": "-0.3389", "Down": "-0.3865"},
            }
        },
        "p2" : { # quadratic parameter
            "2016" : {
                "0j" : {"Nom": "-0.1138", "Up": "-0.0922", "Down": "-0.1354"},
                "1j" : {"Nom": "-0.07938","Up": "-0.06242","Down": "-0.09634"},
                "2j" : {"Nom": "-0.02602","Up": "-0.00307","Down": "-0.04897"},
            },
            "2017" : {
                "0j" : {"Nom": "-0.1430", "Up": "-0.12",   "Down": "-0.166"},
                "1j" : {"Nom": "-0.05544","Up": "-0.03986","Down": "-0.07102"},
                "2j" : {"Nom": "0.03128", "Up": "0.05409", "Down": "0.00847"},
            },
            "2018" : {
                "0j" : {"Nom": "-0.1249", "Up": "-0.1083", "Down": "-0.1415"},
                "1j" : {"Nom": "-0.04374","Up": "-0.03139","Down": "-0.05609"},
                "2j" : {"Nom": "-0.00606","Up": "0.005143","Down": "-0.024355"},
            }
        }
    }
    qcd_variations = []
    for shift_direction in ["Up", "Down"]:
        for dof,parameter in zip(["rate", "shape", "shape2"],["p0", "p1", "p2"]):
            for jetbin in ["0j", "1j", "2j"]:
                qcd_variations.append(ReplaceWeight("CMS_htt_qcd_{}et_{}_{}".format(jetbin, dof, args.era), "qcd_weight",
                    Weight(qcd_weight_string.replace(qcd_parameters[parameter][args.era][jetbin]["Nom"], qcd_parameters[parameter][args.era][jetbin][shift_direction]), "qcd_weight"), shift_direction))

    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_iso_{}".format(args.era), "qcd_weight", Weight(qcd_weight_string.replace(qcd_aisoiso_string, qcd_aisoiso_string+"**2"), "qcd_weight"), "Up"))
    qcd_variations.append(ReplaceWeight("CMS_htt_qcd_iso_{}".format(args.era), "qcd_weight", Weight(qcd_weight_string.replace(qcd_aisoiso_string, ""), "qcd_weight"), "Down"))

    # Gluon-fusion WG1 uncertainty scheme
    ggh_variations = []
    for unc in [
            "THU_ggH_Mig01", "THU_ggH_Mig12", "THU_ggH_Mu", "THU_ggH_PT120",
            "THU_ggH_PT60", "THU_ggH_Res", "THU_ggH_VBF2j", "THU_ggH_VBF3j",
            "THU_ggH_qmtop"
    ]:
        ggh_variations.append(AddWeight(unc, "{}_weight".format(unc), Weight("({})".format(unc), "{}_weight".format(unc)), "Up"))
        ggh_variations.append(AddWeight(unc, "{}_weight".format(unc), Weight("(2.0-{})".format(unc), "{}_weight".format(unc)), "Down"))

    qqh_variations = []
    for unc in ["THU_qqH_25", "THU_qqH_JET01", "THU_qqH_Mjj1000",
                "THU_qqH_Mjj120", "THU_qqH_Mjj1500", "THU_qqH_Mjj350",
                "THU_qqH_Mjj60", "THU_qqH_Mjj700", "THU_qqH_PTH200",
                "THU_qqH_TOT",
    ]:
        qqh_variations.append(AddWeight(unc, "{}_weight".format(unc), Weight("({})".format(unc), "{}_weight".format(unc)), "Up"))
        qqh_variations.append(AddWeight(unc, "{}_weight".format(unc), Weight("(2.0-{})".format(unc), "{}_weight".format(unc)), "Down"))



    # ZL fakes energy scale
    lep_fake_es_variations = {}

    lep_fake_es_variations["mt"] =  create_systematic_variations("CMS_ZLShape_mt_1prong_%s"%args.era, "tauMuFakeEsOneProng", DifferentPipeline)
    lep_fake_es_variations["mt"] += create_systematic_variations("CMS_ZLShape_mt_1prong1pizero_%s"%args.era, "tauMuFakeEsOneProngPiZeros", DifferentPipeline)

    lep_fake_es_variations["et"] =  create_systematic_variations("CMS_ZLShape_et_1prong_barrel_%s"%args.era, "tauEleFakeEsOneProngBarrel", DifferentPipeline)
    lep_fake_es_variations["et"] += create_systematic_variations("CMS_ZLShape_et_1prong_endcap_%s"%args.era, "tauEleFakeEsOneProngEndcap", DifferentPipeline)
    lep_fake_es_variations["et"] += create_systematic_variations("CMS_ZLShape_et_1prong1pizero_barrel_%s"%args.era, "tauEleFakeEsOneProngPiZerosBarrel", DifferentPipeline)
    lep_fake_es_variations["et"] += create_systematic_variations("CMS_ZLShape_et_1prong1pizero_endcap_%s"%args.era, "tauEleFakeEsOneProngPiZerosEndcap", DifferentPipeline)


    # ZL fakes rate uncertainties
    lep_fake_eff_variations = {}
    efake_dict = {
        "2016" : {
            "BA" : "0.31*(abs(eta_1)<1.448)",
            "EC" : "0.22*(abs(eta_1)>1.558)"
        },
        "2017" : {
            "BA" : "0.26*(abs(eta_1)<1.448)",
            "EC" : "0.41*(abs(eta_1)>1.558)"
        },
        "2018" : {
            "BA" : "0.18*(abs(eta_1)<1.448)",
            "EC" : "0.30*(abs(eta_1)>1.558)"
        }
    }
    mfake_dict = {
        "2016" : {
            "WH1" : "0.09*((abs(eta_1)<0.4))",
            "WH2" : "0.42*((abs(eta_1)>=0.4)*((abs(eta_1)<0.8)))",
            "WH3" : "0.20*((abs(eta_1)>=0.8)*((abs(eta_1)<1.2)))",
            "WH4" : "0.63*((abs(eta_1)>=1.2)*((abs(eta_1)<1.7)))",
            "WH5" : "0.17*((abs(eta_1)>=1.7))"
        },
        "2017" : {
            "WH1" : "0.18*((abs(eta_1)<0.4))",
            "WH2" : "0.32*((abs(eta_1)>=0.4)*((abs(eta_1)<0.8)))",
            "WH3" : "0.39*((abs(eta_1)>=0.8)*((abs(eta_1)<1.2)))",
            "WH4" : "0.42*((abs(eta_1)>=1.2)*((abs(eta_1)<1.7)))",
            "WH5" : "0.21*((abs(eta_1)>=1.7))"
        },
        "2018" : {
            "WH1" : "0.19*((abs(eta_1)<0.4))",
            "WH2" : "0.34*((abs(eta_1)>=0.4)*((abs(eta_1)<0.8)))",
            "WH3" : "0.24*((abs(eta_1)>=0.8)*((abs(eta_1)<1.2)))",
            "WH4" : "0.57*((abs(eta_1)>=1.2)*((abs(eta_1)<1.7)))",
            "WH5" : "0.20*((abs(eta_1)>=1.7))"
        }
    }

    lep_fake_eff_variations["et"] = []
    for section, weight in efake_dict[args.era].items():
        lep_fake_eff_variations["et"].append(AddWeight("CMS_fake_e_%s_%s"%(section, args.era), "eFakeTau_reweight",Weight("(1.0+%s)"%weight, "eFakeTau_reweight"),"Up"))
        lep_fake_eff_variations["et"].append(AddWeight("CMS_fake_e_%s_%s"%(section, args.era), "eFakeTau_reweight",Weight("(1.0-%s)"%weight, "eFakeTau_reweight"),"Down"))

    lep_fake_eff_variations["mt"] = []
    for section, weight in mfake_dict[args.era].items():
        lep_fake_eff_variations["mt"].append(AddWeight("CMS_fake_m_%s_%s"%(section, args.era), "mFakeTau_reweight",Weight("(1.0+%s)"%weight, "mFakeTau_reweight"),"Up"))
        lep_fake_eff_variations["mt"].append(AddWeight("CMS_fake_m_%s_%s"%(section, args.era), "mFakeTau_reweight",Weight("(1.0-%s)"%weight, "mFakeTau_reweight"),"Down"))

    # Lepton trigger efficiency; the same values for (MC & EMB) and (mt & et)
    lep_trigger_eff_variations = {}
    for ch in ["mt", "et"]:
        lep_trigger_eff_variations[ch] = {}
        thresh_dict = {"2016": {"mt": 23., "et": 30.},
                       "2017": {"mt": 28., "et": 40.},
                       "2018": {"mt": 28., "et": 37.}}
        for unctype in ["", "_emb"]:
            lep_trigger_eff_variations[ch][unctype] = []
            lep_trigger_eff_variations[ch][unctype].append(AddWeight("CMS_eff_trigger%s_%s_%s"%(unctype, ch, args.era), "trg_%s_eff_weight"%ch, Weight("(1.0*(pt_1<={0})+1.02*(pt_1>{0}))".format(thresh_dict[args.era][ch]), "trg_%s_eff_weight"%ch), "Up"))
            lep_trigger_eff_variations[ch][unctype].append(AddWeight("CMS_eff_trigger%s_%s_%s"%(unctype, ch, args.era), "trg_%s_eff_weight"%ch, Weight("(1.0*(pt_1<={0})+0.98*(pt_1>{0}))".format(thresh_dict[args.era][ch]), "trg_%s_eff_weight"%ch), "Down"))
            lep_trigger_eff_variations[ch][unctype].append(AddWeight("CMS_eff_xtrigger_l%s_%s_%s"%(unctype, ch, args.era), "xtrg_%s_eff_weight"%ch, Weight("(1.02*(pt_1<={0})+1.0*(pt_1>{0}))".format(thresh_dict[args.era][ch]), "xtrg_%s_eff_weight"%ch), "Up"))
            lep_trigger_eff_variations[ch][unctype].append(AddWeight("CMS_eff_xtrigger_l%s_%s_%s"%(unctype, ch, args.era), "xtrg_%s_eff_weight"%ch, Weight("(0.98*(pt_1<={0})+1.0*(pt_1>{0}))".format(thresh_dict[args.era][ch]), "xtrg_%s_eff_weight"%ch), "Down"))


    # Tau trigger efficiency; needed separately for ( MC | EMB ) x (mt & et | tt)
    tau_trigger_variations = { "Embedded" : {}, "MC" : {}}
    single_lep_common = { "Embedded" : {}, "MC" : {}}
    xtrg_lep_common = { "Embedded" : {},  "MC" : {}}

    single_lep_common["MC"] = {
            "2016": {
                "et": "(trg_singleelectron==1 && pt_1 > 30)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerMCEfficiencyWeightKIT_1)",
                "mt": "(trg_singlemuon==1 && pt_1 > 23)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerMCEfficiencyWeightKIT_1)"},
            "2017": {
                "et": "(trg_singlemuon_27==1 && pt_1 > 28)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerMCEfficiencyWeightKIT_1)",
                "mt": "(trg_singleelectron_35==1 && pt_1 > 40)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerMCEfficiencyWeightKIT_1)"},
            "2018": {
                "et": "((trg_singleelectron_32==1 && pt_1>37)*trigger_32_35_Weight_1)",
                "mt": "((trg_singlemuon_27==1 && pt_1>28)*trigger_27_Weight_1)"},
    }
    xtrg_lep_common["MC"] = {
            "2016": {
                "et": "(trg_eletaucross==1 && pt_1<=30)*(crossTriggerDataEfficiencyWeightKIT_1/crossTriggerMCEfficiencyWeightKIT_1)",
                "mt": "(trg_mutaucross==1 && pt_1 <= 23)*(crossTriggerDataEfficiencyWeightKIT_1/crossTriggerMCEfficiencyWeightKIT_1)"},
            "2017": {
                "et": "(trg_crossele_ele24tau30==1 && pt_1>29 && pt_1<=40)*(crossTriggerDataEfficiencyWeight_1/crossTriggerMCEfficiencyWeight_1)",
                "mt": "(trg_crossmuon_mu20tau27==1 && pt_1 > 21 && pt_1 <= 28)*(crossTriggerDataEfficiencyWeight_1/crossTriggerMCEfficiencyWeight_1)"},
            "2018": {
                "et": "(pt_1>29 && pt_1<= 37 && (trg_crossele_ele24tau30==1 || trg_crossele_ele24tau30_hps==1))*(crossTriggerDataEfficiencyWeight_1/crossTriggerMCEfficiencyWeight_1)",
                "mt": "(pt_1 > 21 && pt_1 <= 28 && (trg_crossmuon_mu20tau27==1 || trg_crossmuon_mu20tau27_hps==1))*(crossTriggerDataEfficiencyWeight_1/crossTriggerMCEfficiencyWeight_1)"}
    }
    single_lep_common["Embedded"] = {
            "2016": {
                "et": "(trg_singleelectron==1 && pt_1 > 30)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerEmbeddedEfficiencyWeightKIT_1)",
                "mt": "(trg_singlemuon==1 && pt_1 > 23)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerEmbeddedEfficiencyWeightKIT_1)"},
            "2017": {
                "et": "(trg_singleelectron_35==1 && pt_1 > 40)*(trigger_27_32_35_Weight_1)",
                "mt": "(trg_singlemuon_27==1 && pt_1 > 28)*(trigger_27_Weight_1)"},
            "2018": {
                "et": "((trg_singleelectron_32==1 && pt_1>37)*(trigger_32_35_Weight_1)",
                "mt": "((trg_singlemuon_27==1 && pt_1>28)*(trigger_27_Weight_1)"},
    }
    xtrg_lep_common["Embedded"] = {
            "2016": {
                "et": "(trg_eletaucross==1 && pt_1<=30)*(crossTriggerDataEfficiencyWeightKIT_1/crossTriggerEmbeddedEfficiencyWeightKIT_1)",
                "mt": "(trg_mutaucross==1 && pt_1 <= 23)*(crossTriggerDataEfficiencyWeightKIT_1/crossTriggerEmbeddedEfficiencyWeightKIT_1)"},
            "2017": {
                "et": "(trg_crossele_ele24tau30==1 && pt_1>29 && pt_1<=40)*crossTriggerEmbeddedWeight_1",
                "mt": "(trg_crossmuon_mu20tau27==1 && pt_1 > 21 && pt_1 <= 28)*crossTriggerEmbeddedWeight_1"},
            "2018": {
                "et": "(pt_1>29 && pt_1<= 37 && (trg_crossele_ele24tau30==1 || trg_crossele_ele24tau30_hps==1))*crossTriggerEmbeddedWeight_1",
                "mt": "(pt_1 > 21 && pt_1 <= 28 && (trg_crossmuon_mu20tau27==1 || trg_crossmuon_mu20tau27_hps==1))*crossTriggerEmbeddedWeight_1"}
    }

    for ch in ["mt", "et", "tt"]:
        weight_string_template = "({TAU})" if ch == "tt" else "({SLEP} + {XLEP}*{TAU})"
        tauindices = ["1", "2"] if ch == "tt" else ["2"]
        for processtype in ["MC", "Embedded"]:
            unctypes = ["", "_emb"] if processtype == "Embedded" else [""]
            weight_string = weight_string_template if ch == "tt" else weight_string_template.format(SLEP=single_lep_common[processtype][args.era][ch],XLEP=xtrg_lep_common[processtype][args.era][ch],TAU="{TAU}")
            variationname = "CMS_eff_xtrigger_t{unctype}_{ch}_dm{dm}_{era}"
            tautrigweightname = "crossTriggerCorrected{PROCESS}EfficiencyWeight{VARIATION}_tight_DeepTau_{INDEX}"
            tauvarelement = "({DATAW}/{PW})*({DM}*(1.0 {OPERATOR} TMath::Sqrt( (({DATAW} - {DATADOWNW})/(DATAW))**2 + (({PW} - {PDOWNW})/(PW))**2 )) + {DMNOT})"
            tau_trigger_variations[processtype][ch] = {}
            for unctype in unctypes:
                tau_trigger_variations[processtype][ch][unctype] = []
                for shift_direction in ["Up", "Down"]:
                    for decaymode in [0, 1, 10, 11]:
                        dmpassed = "(decayMode_{INDEX} == {DM})".format(DM=decaymode, INDEX="{INDEX}") if decaymode != 1 else "(decayMode_{INDEX} == 1 || decayMode_{INDEX} == 2)"
                        dmnotpassed = "(decayMode_{INDEX} != {DM})".format(DM=decaymode, INDEX="{INDEX}") if decaymode != 1 else "(decayMode_{INDEX} != 1 && decayMode_{INDEX} != 2)"
                        tautrg_varelements = []
                        for tauind in  tauindices:
                            tautrg_varelements.append(tauvarelement.format(
                                DATAW=tautrigweightname.format(PROCESS="Data",VARIATION="",INDEX=tauind),
                                DATADOWNW=tautrigweightname.format(PROCESS="Data",VARIATION="Down",INDEX=tauind),
                                PW=tautrigweightname.format(PROCESS=processtype,VARIATION="",INDEX=tauind),
                                PDOWNW=tautrigweightname.format(PROCESS=processtype,VARIATION="Down",INDEX=tauind),
                                DM=dmpassed.format(INDEX=tauind),
                                DMNOT=dmnotpassed.format(INDEX=tauind),
                                OPERATOR="+" if shift_direction == "Up" else "-"
                                )
                            )
                        tautrgweight = tautrg_varelements[0] if len(tautrg_varelements) == 1 else "*".join(tautrg_varelements)
                        tau_trigger_variations[processtype][ch][unctype].append(ReplaceWeight(
                            variationname.format(unctype=unctype,ch=ch,dm=decaymode,era=args.era),
                            "triggerweight",
                            Weight(weight_string.format(TAU=tautrgweight),"triggerweight"),
                            shift_direction)
                        )


    # Fake factor uncertainties
    fake_factor_names = {}
    fake_factor_variations = {
        "mt" : [],
        "et" : [],
        "tt" : [],
    }
    fake_factor_weight = {}
    for ch in ["mt", "et"]:
        fake_factor_names[ch] = [

            # QCD FF's
            ## mvis correction
            "ff_corr_qcd_mvis{ch}{era}{shift}", # applying correction twice/not applying it
            "ff_corr_qcd_mvis_osss{ch}{era}{shift}", # applying correction twice/not applying it
            "ff_qcd_mvis{ch}{era}{shift}", # statistical uncertainty from smoothed band (morphed)
            "ff_qcd_mvis_osss{ch}{era}{shift}", # statistical uncertainty from smoothed band (morphed)
            ## lepton (!!!) isolation correction
            "ff_corr_qcd_muiso{ch}{era}{shift}", # applying correction twice/not applying it
            "ff_qcd_muiso{ch}{era}{shift}", # statistical uncertainty from smoothed band (morphed)
            ## combined quadratically, not morphed statistical uncertainty from smoothed band (needed for normalization uncertainty via lnN)
            "ff_qcd_syst{ch}{era}{shift}",
            ## uncertainty from the sampling method of the raw FF's
            ### morphed
            "ff_qcd_dr0_njet0_morphed_stat{ch}{era}{shift}",
            "ff_qcd_dr0_njet1_morphed_stat{ch}{era}{shift}",
            "ff_qcd_dr0_njet2_morphed_stat{ch}{era}{shift}",
            ### not morphed (needed for normalization uncertainty via lnN)
            "ff_qcd_dr0_njet0_stat{ch}{era}{shift}",
            "ff_qcd_dr0_njet1_stat{ch}{era}{shift}",
            "ff_qcd_dr0_njet2_stat{ch}{era}{shift}",
            ## uncertainty for the mc subtraction
            "ff_qcd_mc{ch}{era}{shift}",
            # WJets FF's
            ## lepton Pt correction
            "ff_corr_w_lepPt{ch}{era}{shift}", # applying correction twice/not applying it
            "ff_w_lepPt{ch}{era}{shift}", # statistical uncertainty from smoothed band (morphed)
            ## mT correction
            "ff_corr_w_mt{ch}{era}{shift}", # applying correction twice/not applying it
            "ff_w_mt{ch}{era}{shift}", # statistical uncertainty from smoothed band (morphed)
            ## combined quadratically, not morphed statistical uncertainty from smoothed band (needed for normalization uncertainty via lnN)
            "ff_w_syst{ch}{era}{shift}",
            ## uncertainty from the sampling method of the raw FF's
            ### morphed
            "ff_w_dr0_njet0_morphed_stat{ch}{era}{shift}",
            "ff_w_dr0_njet1_morphed_stat{ch}{era}{shift}",
            "ff_w_dr0_njet2_morphed_stat{ch}{era}{shift}",
            "ff_w_dr1_njet0_morphed_stat{ch}{era}{shift}",
            "ff_w_dr1_njet1_morphed_stat{ch}{era}{shift}",
            "ff_w_dr1_njet2_morphed_stat{ch}{era}{shift}",
            ### not morphed (needed for normalization uncertainty via lnN)
            "ff_w_dr0_njet0_stat{ch}{era}{shift}",
            "ff_w_dr0_njet1_stat{ch}{era}{shift}",
            "ff_w_dr0_njet2_stat{ch}{era}{shift}",
            "ff_w_dr1_njet0_stat{ch}{era}{shift}",
            "ff_w_dr1_njet1_stat{ch}{era}{shift}",
            "ff_w_dr1_njet2_stat{ch}{era}{shift}",
            ## uncertainty for the mc subtraction
            "ff_w_mc{ch}{era}{shift}",
            # TT FF's
            ## mvis correction
            "ff_corr_tt_syst{ch}{era}{shift}", # applying correction twice/not applying it
            "ff_tt_morphed{ch}{era}{shift}", # statistical uncertainty from smoothed band (morphed)
            "ff_tt_syst{ch}{era}{shift}", # statistical uncertainty from smoothed band (not morphed, needed for normalization uncertainty via lnN)
            ## uncertainty from the sampling method of the raw FF's
            ### morphed
            "ff_tt_dr0_njet0_morphed_stat{ch}{era}{shift}",
            "ff_tt_dr0_njet1_morphed_stat{ch}{era}{shift}",
            ### not morphed (needed for normalization uncertainty via lnN)
            "ff_tt_stat{ch}{era}{shift}",
            ## uncertainty on the correction from MC to data
            "ff_tt_sf{ch}{era}{shift}",
            # uncertainty on the fractions
            "ff_frac_w{ch}{era}{shift}",

        ]
        fake_factor_weight[ch] = "ff2_{syst}"
    fake_factor_names["tt"] = [
            # correciton in mvis
            "ff_corr_qcd_mvis{ch}{era}{shift}", # applying correction twice/not applying it
            "ff_corr_qcd_mvis_osss{ch}{era}{shift}", # applying correction twice/not applying it
            "ff_qcd_mvis{ch}{era}{shift}", # statistical uncertainty from smoothed band (morphed)
            "ff_qcd_mvis_osss{ch}{era}{shift}", # statistical uncertainty from smoothed band (morphed)
            # correction in isolated (trailing) tau pt
            "ff_corr_qcd_tau2_pt{ch}{era}{shift}", # applying correction twice/not applying it
            "ff_qcd_tau2_pt{ch}{era}{shift}", # statistical uncertainty from smoothed band (morphed)
            # combined quadratically, not morphed statistical uncertainty from smoothed band (needed for normalization uncertainty via lnN)
            "ff_qcd_syst{ch}{era}{shift}",
            # uncertainty from the sampling method of the raw FF's
            ## morphed
            "ff_qcd_dr0_njet0_morphed_stat{ch}{era}{shift}",
            "ff_qcd_dr0_njet1_morphed_stat{ch}{era}{shift}",
            "ff_qcd_dr0_njet2_morphed_stat{ch}{era}{shift}",
            ## not morphed (needed for normalization uncertainty via lnN)
            "ff_qcd_dr0_njet0_stat{ch}{era}{shift}",
            "ff_qcd_dr0_njet1_stat{ch}{era}{shift}",
            "ff_qcd_dr0_njet2_stat{ch}{era}{shift}",
            # uncertainty for the mc subtraction
            "ff_qcd_mc{ch}{era}{shift}",
            # 30% uncertainty for contamination of other processes, derived from fractions in tt
            "ff_w_syst{ch}{era}{shift}", # WJets
            "ff_tt_syst{ch}{era}{shift}", # TT
    ]
    fake_factor_weight["tt"] = "(0.5*ff1_{syst}*(byTightDeepTau2017v2p1VSjet_1<0.5)+0.5*ff2_{syst}*(byTightDeepTau2017v2p1VSjet_2<0.5))"
    for ch in ["mt", "et", "tt"]:
        for shift_direction in ["Up", "Down"]:
            for systematic_shift in fake_factor_names[ch]:
                hname = "CMS_" + systematic_shift.format(ch="_" + ch, shift="", era="_" + args.era).replace("_dm0", "")
                systname = systematic_shift.format(ch="",shift="_" + shift_direction.lower(),era="")
                variation = ReplaceWeight(hname, "fake_factor", Weight(fake_factor_weight[ch].format(syst=systname), "fake_factor"), shift_direction)
                fake_factor_variations[ch].append(variation)

    ## Group nicks
    mc_nicks = ["ZL", "TTL", "VVL"] + signal_nicks # to be extended with 'W' in em
    boson_mc_nicks = ["ZL"]         + signal_nicks # to be extended with 'W' in em

    ### Add variations to systematics
    for ch in args.channels:

        channel_mc_nicks = mc_nicks + ["W"] if ch == "em" else mc_nicks
        channel_boson_mc_nicks = boson_mc_nicks + ["W"] if ch == "em" else boson_mc_nicks

        channel_mc_common_variations = common_mc_variations
        if ch in ["et", "em"]:
            channel_mc_common_variations += ele_es_variations
        if ch in ["et", "mt", "tt"]:
            channel_mc_common_variations += tau_es_variations[""] + tau_id_variations[ch][""] + tau_trigger_variations["MC"][ch][""]
        if ch in ["et", "mt"]:
            channel_mc_common_variations += lep_trigger_eff_variations[ch][""]

        # variations common accross all shape groups
        for variation in channel_mc_common_variations:
            for process_nick in channel_mc_nicks:
                if args.process == process_nick:
                    systematics.add_systematic_variation(variation=variation, process=processes[ch][process_nick], channel=channel_dict[args.era][ch], era=era)

        for variation in recoil_variations:
            for process_nick in channel_boson_mc_nicks:
                if args.process == process_nick:
                    systematics.add_systematic_variation(variation=variation, process=processes[ch][process_nick], channel=channel_dict[args.era][ch], era=era)

        # variations relevant for ggH signals in 'sm_signals' shape group
        for variation in ggh_variations:
            for process_nick in [nick for nick in signal_nicks if "ggH" in nick and "HWW" not in nick and "ggH_" not in nick]:
                if args.process == process_nick:
                    systematics.add_systematic_variation(variation=variation, process=processes[ch][process_nick], channel=channel_dict[args.era][ch], era=era)

        # variations relevant for qqH signals in 'sm_signals' shape group
        for variation in qqh_variations:
            for process_nick in [nick for nick in signal_nicks if "qqH" in nick and "HWW" not in nick]:
                if args.process == process_nick:
                    systematics.add_systematic_variation(variation=variation, process=processes[ch][process_nick], channel=channel_dict[args.era][ch], era=era)

        # variations only relevant for the 'background' shape group
        for variation in top_pt_variations:
            if args.process == "TTL":
                systematics.add_systematic_variation(variation=variation, process=processes[ch]["TTL"], channel=channel_dict[args.era][ch], era=era)

        for variation in met_unclustered_variations:
            for process_nick in ["TTL", "VVL"]:
                if args.process == process_nick:
                    systematics.add_systematic_variation(variation=variation, process=processes[ch][process_nick], channel=channel_dict[args.era][ch], era=era)

        zl_variations = zpt_variations
        if ch in ["et", "mt"]:
            zl_variations += lep_fake_es_variations[ch] + lep_fake_eff_variations[ch]
        for variation in zl_variations:
            if args.process == "ZL":
                systematics.add_systematic_variation(variation=variation, process=processes[ch]["ZL"], channel=channel_dict[args.era][ch], era=era)

        if ch == "em":
            for variation in qcd_variations:
                if args.process == "QCD":
                    systematics.add_systematic_variation(variation=variation, process=processes[ch]["QCD"], channel=channel_dict[args.era][ch], era=era)

        if ch in ["mt", "et", "tt"]:
            ff_variations = fake_factor_variations[ch] + tau_es_variations[""] + tau_es_variations["_emb"]
            for variation in ff_variations:
                if args.process == "jetFakes":
                    systematics.add_systematic_variation(variation=variation, process=processes[ch]["jetFakes"], channel=channel_dict[args.era][ch], era=era)

        emb_variations = []
        if ch in ["mt", "et", "tt"]:
            emb_variations += tau_es_variations[""] + tau_es_variations["_emb"]
            emb_variations += tau_id_variations[ch][""] + tau_id_variations[ch]["_emb"] + decayMode_variations
            emb_variations += tau_trigger_variations["Embedded"][ch][""] + tau_trigger_variations["Embedded"][ch]["_emb"]
        if ch in ["mt", "et"]:
            emb_variations += lep_trigger_eff_variations[ch]["_emb"]
        if ch in ["et", "em"]:
            emb_variations += ele_es_emb_variations
        for variation in emb_variations:
            if args.process == "EMB":
                systematics.add_systematic_variation(variation=variation, process=processes[ch]["EMB"], channel=channel_dict[args.era][ch], era=era)

    # Produce histograms
    logger.info("Start producing shapes.")
    systematics.produce()
    logger.info("Done producing shapes.")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_produce_cutbased_shapes_{}.log".format(args.tag, args.discriminator_variable), logging.INFO)
    main(args)
