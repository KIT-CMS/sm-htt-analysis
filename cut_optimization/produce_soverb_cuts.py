#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
ROOT.gErrorIgnoreLevel = ROOT.kError

from shape_producer.cutstring import Cut, Cuts
from shape_producer.systematics import Systematics, Systematic
from shape_producer.categories import Category
from shape_producer.binning import ConstantBinning, VariableBinning
from shape_producer.variable import Variable
from shape_producer.systematic_variations import Nominal, DifferentPipeline, SquareAndRemoveWeight, create_systematic_variations
from shape_producer.process import Process
from shape_producer.estimation_methods_2017 import *
from shape_producer.estimation_methods import AddHistogramEstimationMethod
from shape_producer.era import Run2017
from shape_producer.channel import MTSM2017 as MT
from shape_producer.channel import ETSM2017 as ET
from shape_producer.channel import TTSM2017 as TT
from shape_producer.channel import EMSM2017 as EM
from shape_producer.channel import MMSM2017 as MM

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
    parser.add_argument(
        "--QCD-extrap-fit",
        default=False,
        action='store_true',
        help="Create shapes for QCD extrapolation factor determination.")
    parser.add_argument(
        "--HIG16043",
        action="store_true",
        default=False,
        help="Create shapes of HIG16043 reference analysis.")
    parser.add_argument(
        "--num-threads",
        default=20,
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
    systematics = Systematics("counts_for_soverb.root", num_threads=args.num_threads, find_unique_objects=False)

    # Era
    era = Run2017(args.datasets)

    # Channels and processes
    # yapf: disable
    directory = args.directory
    et_friend_directory = args.et_friend_directory
    mt_friend_directory = args.mt_friend_directory
    tt_friend_directory = args.tt_friend_directory
    em_friend_directory = args.em_friend_directory

    ff_friend_directory = args.fake_factor_friend_directory

    mt = MT()
    mt_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, mt, friend_directory=mt_friend_directory)),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, mt, friend_directory=mt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, mt, friend_directory=mt_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, mt, friend_directory=mt_friend_directory)),
#        "WH"    : Process("WH125",    WHEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
#        "ZH"    : Process("ZH125",    ZHEstimation        (era, directory, mt, friend_directory=mt_friend_directory)),
#        "ttH"   : Process("ttH125",   ttHEstimation       (era, directory, mt, friend_directory=mt_friend_directory)),
        }
    mt_processes["FAKESEMB"] = Process("jetFakesEMB", NewFakeEstimationLT(era, directory, mt, [mt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], mt_processes["data"], friend_directory=mt_friend_directory+[ff_friend_directory]))


    et = ET()
    et_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, et, friend_directory=et_friend_directory)),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, et, friend_directory=et_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, et, friend_directory=et_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, et, friend_directory=et_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, et, friend_directory=et_friend_directory)),
#        "WH"    : Process("WH125",    WHEstimation        (era, directory, et, friend_directory=et_friend_directory)),
#        "ZH"    : Process("ZH125",    ZHEstimation        (era, directory, et, friend_directory=et_friend_directory)),
#        "ttH"   : Process("ttH125",   ttHEstimation       (era, directory, et, friend_directory=et_friend_directory)),
        }
    et_processes["FAKESEMB"] = Process("jetFakesEMB", NewFakeEstimationLT(era, directory, et, [et_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], et_processes["data"], friend_directory=et_friend_directory+[ff_friend_directory]))


    tt = TT()
    tt_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, tt, friend_directory=tt_friend_directory)),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, tt, friend_directory=tt_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, tt, friend_directory=tt_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, tt, friend_directory=tt_friend_directory)),
#        "WH"    : Process("WH125",    WHEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
#        "ZH"    : Process("ZH125",    ZHEstimation        (era, directory, tt, friend_directory=tt_friend_directory)),
#        "ttH"   : Process("ttH125",   ttHEstimation       (era, directory, tt, friend_directory=tt_friend_directory)),
        }
    tt_processes["FAKESEMB"] = Process("jetFakesEMB", NewFakeEstimationTT(era, directory, tt, [tt_processes[process] for process in ["EMB", "ZL", "TTL", "VVL"]], tt_processes["data"], friend_directory=tt_friend_directory+[ff_friend_directory]))


    em = EM()
    em_processes = {
        "data"  : Process("data_obs", DataEstimation      (era, directory, em, friend_directory=em_friend_directory)),
        "EMB"   : Process("EMB",      ZTTEmbeddedEstimation  (era, directory, em, friend_directory=em_friend_directory)),
        "ZL"    : Process("ZL",       ZLEstimation        (era, directory, em, friend_directory=em_friend_directory)),
        "TTL"   : Process("TTL",      TTLEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "VVL"   : Process("VVL",      VVLEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        "W"     : Process("W",        WEstimation         (era, directory, em, friend_directory=em_friend_directory)),
        "ggH"   : Process("ggH125",   ggHEstimation       ("ggH125", era, directory, em, friend_directory=em_friend_directory)),
        "qqH"   : Process("qqH125",   qqHEstimation       ("qqH125", era, directory, em, friend_directory=em_friend_directory)),
#        "WH"    : Process("WH125",    WHEstimation        (era, directory, em, friend_directory=em_friend_directory)),
#        "ZH"    : Process("ZH125",    ZHEstimation        (era, directory, em, friend_directory=em_friend_directory)),
#        "ttH"   : Process("ttH125",   ttHEstimation       (era, directory, em, friend_directory=em_friend_directory)),
        }

    em_processes["QCDEMB"] = Process("QCDEMB", QCDEstimation_SStoOS_MTETEM(era, directory, em, [em_processes[process] for process in ["EMB", "ZL", "W", "VVL"]], em_processes["data"], extrapolation_factor=1.0, qcd_weight = Weight("em_qcd_extrap_up_Weight","qcd_weight")))

    channels = {
        "mt" : mt,
        "et" : et,
        "tt" : tt,
        "em" : em,
    }

    processes = {
        "mt" : mt_processes,
        "et" : et_processes,
        "tt" : tt_processes,
        "em" : em_processes,
    }

    # Variables and categories
    binning = yaml.load(open(args.binning))

    variable_names = [
        "ME_D",
        "dijetpt", "jdeta", "mjj",# "jpt_1", "jpt_2", "njets",
#        "bpt_1", "bpt_2", "nbtag",
#        "DiTauDeltaR", "ptvis", "pt_tt", "pt_tt_puppi", "pt_ttjj", "pt_ttjj_puppi", "eta_sv", "eta_fastmtt",
        "pt_tt", "pt_tt_puppi", "pt_ttjj", "pt_ttjj_puppi",
#        "mt_1", "mt_2", "mTdileptonMET", "pZetaMissVis",
        "mt_1", "pZetaMissVis",
#        "mt_1_puppi", "mt_2_puppi", "mTdileptonMET_puppi", "pZetaPuppiMissVis",
        "mt_1_puppi", "pZetaPuppiMissVis",
#        "m_sv", "m_fastmtt", "m_vis",
    ]
    categories = {
        "mt" : [],
        "et" : [],
        "tt" : [],
        "em" : [],
    }
    for variable in variable_names:
        for ch in args.channels:
            cut_values = binning["control"][ch][variable]["bins"]
            for cut in cut_values:
                categories[ch].append(Category("%s-less-%s"%(variable, str(cut).replace(".","p")),channels[ch], Cuts(Cut("%s < %s"%(variable, str(cut)))), variable=None))
                categories[ch].append(Category("%s-greater-%s"%(variable, str(cut).replace(".","p")),channels[ch], Cuts(Cut("%s > %s"%(variable, str(cut)))), variable=None))
        

    # Nominal histograms
    for ch in args.channels:
        for process, category in product(processes[ch].values(), categories[ch]):
            systematics.add(
                Systematic(
                    category=category,
                    process=process,
                    analysis="smhtt",
                    era=era,
                    variation=Nominal(),
                    mass="125"))


    # Produce histograms
    systematics.produce()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_shapes.log", logging.INFO)
    main(args)
