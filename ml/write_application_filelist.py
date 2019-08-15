#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

from shape_producer.channel import *
from shape_producer.era import *

import argparse
import yaml
import os

import logging
logger = logging.getLogger("write_application_filelist")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    logger.debug("Parse arguments.")
    parser = argparse.ArgumentParser(
        description="Create filelist for application.")
    parser.add_argument(
        "--directory", required=True, help="Path to Artus output files")
    parser.add_argument(
        "--database", required=True, help="Path to Kappa datasets database")
    parser.add_argument("--era", required=True, help="Experiment era")
    parser.add_argument("--channel", required=True, help="Analysis channel")
    parser.add_argument("--output", required=True, help="Output filelist")
    return parser.parse_args()


def main(args):
    # Write arparse arguments to YAML config
    filelist = {}

    # Define era
    if "2016" in args.era:
        from shape_producer.estimation_methods_2016 import DataEstimation, ggHEstimation, qqHEstimation, ZTTEstimation, ZLEstimation, ZJEstimation, WEstimation, TTTEstimation, TTJEstimation, ZTTEmbeddedEstimation, TTLEstimation, EWKZEstimation, VVLEstimation, VVJEstimation, VVEstimation, VVTEstimation, VHEstimation,  EWKWpEstimation, EWKWmEstimation, ttHEstimation, ggHWWEstimation, qqHWWEstimation
        #QCDEstimation_SStoOS_MTETEM, QCDEstimationTT, HTTEstimation,

        from shape_producer.era import Run2016
        era = Run2016(args.database)
    elif "2017" in args.era:
        from shape_producer.estimation_methods_2017 import DataEstimation, ZTTEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVTEstimation, VVJEstimation, VVLEstimation, WEstimation, ggHEstimation, qqHEstimation, VHEstimation, EWKZEstimation, ZTTEmbeddedEstimation, ttHEstimation

        from shape_producer.era import Run2017
        era = Run2017(args.database)
    elif "2018" in args.era:
        from shape_producer.estimation_methods_2018 import DataEstimation, ZTTEstimation, ZLEstimation, ZJEstimation, TTLEstimation, TTJEstimation, TTTEstimation, VVTEstimation, VVJEstimation, VVLEstimation, WEstimation, ggHEstimation, qqHEstimation, VHEstimation, EWKZEstimation, ZTTEmbeddedEstimation, ttHEstimation

        from shape_producer.era import Run2018
        era = Run2018(args.database)

    else:
        logger.fatal("Era {} is not implemented.".format(args.era))
        raise Exception

    logger.debug("Write filelist for channel %s in era %s.", args.channel,
                 args.era)

    ############################################################################

    # Era: 2016, Channel: mt
    if "2016" in args.era and args.channel == "mt":
        channel = MTSM2016()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),    
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                #ZTTEmbeddedEstimation(era, args.directory, channel), #TODO include EMB again once samples are there
                ZLEstimation(era, args.directory, channel),
                ZJEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                TTJEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                EWKWpEstimation(era, args.directory, channel),
                EWKWmEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel),
                ggHWWEstimation(era, args.directory, channel),
                qqHWWEstimation(era, args.directory, channel)
        ]:
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders

    ############################################################################

    # Era: 2017, Channel: mt
    if "2017" in args.era and args.channel == "mt":
        channel = MTSM2017()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                ZTTEmbeddedEstimation(era, args.directory, channel),
                ZLEstimation(era, args.directory, channel),
                ZJEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTJEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVJEstimation(era, args.directory, channel),
                VVTEstimation(era, args.directory, channel),
                VVLEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel)
        ]:
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders

    ############################################################################

    # Era: 2018, Channel: mt
    if "2018" in args.era and args.channel == "mt":
        channel = MTSM2018()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                ZTTEmbeddedEstimation(era, args.directory, channel),
                ZLEstimation(era, args.directory, channel),
                ZJEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTJEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVJEstimation(era, args.directory, channel),
                VVTEstimation(era, args.directory, channel),
                VVLEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel)
        ]:  
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders


    ############################################################################

    # Era: 2016, Channel: et
    if "2016" in args.era and args.channel == "et":
        channel = ETSM2016()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),    
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                #ZTTEmbeddedEstimation(era, args.directory, channel), #TODO include EMB again once samples are there
                ZLEstimation(era, args.directory, channel),
                ZJEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                TTJEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                EWKWpEstimation(era, args.directory, channel),
                EWKWmEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel),
                ggHWWEstimation(era, args.directory, channel),
                qqHWWEstimation(era, args.directory, channel)
        ]:
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders

    ############################################################################

    # Era: 2017, Channel: et
    if "2017" in args.era and args.channel == "et":
        channel = ETSM2017()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                ZTTEmbeddedEstimation(era, args.directory, channel),
                ZLEstimation(era, args.directory, channel),
                ZJEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTJEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVJEstimation(era, args.directory, channel),
                VVTEstimation(era, args.directory, channel),
                VVLEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel)
        ]:
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders

    ############################################################################

    # Era: 2018, Channel: et
    if "2018" in args.era and args.channel == "et":
        channel = ETSM2018()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                ZTTEmbeddedEstimation(era, args.directory, channel),
                ZLEstimation(era, args.directory, channel),
                ZJEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTJEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVJEstimation(era, args.directory, channel),
                VVTEstimation(era, args.directory, channel),
                VVLEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel)
        ]:  
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders

    ############################################################################

    # Era: 2016, Channel: tt
    if "2016" in args.era and args.channel == "tt":
        channel = TTSM2016()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),    
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                #ZTTEmbeddedEstimation(era, args.directory, channel), #TODO include EMB again once samples are there
                ZLEstimation(era, args.directory, channel),
                ZJEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                TTJEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                EWKWpEstimation(era, args.directory, channel),
                EWKWmEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel),
                ggHWWEstimation(era, args.directory, channel),
                qqHWWEstimation(era, args.directory, channel)
        ]:
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders

    ############################################################################

    # Era 2017, Channel: tt
    if "2017" in args.era and args.channel == "tt":
        channel = TTSM2017()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                ZTTEmbeddedEstimation(era, args.directory, channel),
                ZLEstimation(era, args.directory, channel),
                ZJEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTJEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVJEstimation(era, args.directory, channel),
                VVTEstimation(era, args.directory, channel),
                VVLEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel)
        ]:
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders

    ############################################################################

    # Era 2018, Channel: tt
    if "2018" in args.era and args.channel == "tt":
        channel = TTSM2018()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                ZTTEmbeddedEstimation(era, args.directory, channel),
                ZLEstimation(era, args.directory, channel),
                ZJEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTJEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVJEstimation(era, args.directory, channel),
                VVTEstimation(era, args.directory, channel),
                VVLEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel)
        ]:
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders


    ############################################################################

    # Era: 2016, Channel: em
    if "2016" in args.era and args.channel == "em":
        channel = EMSM2016()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),    
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                #ZTTEmbeddedEstimation(era, args.directory, channel), #TODO include EMB again once samples are there
                ZLEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                EWKWpEstimation(era, args.directory, channel),
                EWKWmEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel),
                ggHWWEstimation(era, args.directory, channel),
                qqHWWEstimation(era, args.directory, channel)
        ]:
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders

    ############################################################################

    # Era: 2017, Channel: em
    if "2017" in args.era and args.channel == "em":
        channel = EMSM2017()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                ZTTEmbeddedEstimation(era, args.directory, channel),
                ZLEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVTEstimation(era, args.directory, channel),
                VVLEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel)
        ]:
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders

    ############################################################################

    # Era: 2018, Channel: em
    if "2018" in args.era and args.channel == "em":
        channel = EMSM2018()
        for estimation in [
                ggHEstimation("ggH", era, args.directory, channel),
                qqHEstimation("qqH", era, args.directory, channel),
                ttHEstimation(era, args.directory, channel),
                VHEstimation(era, args.directory, channel),
                ZTTEstimation(era, args.directory, channel),
                ZTTEmbeddedEstimation(era, args.directory, channel),
                ZLEstimation(era, args.directory, channel),
                TTTEstimation(era, args.directory, channel),
                TTLEstimation(era, args.directory, channel),
                WEstimation(era, args.directory, channel),
                VVTEstimation(era, args.directory, channel),
                VVLEstimation(era, args.directory, channel),
                EWKZEstimation(era, args.directory, channel),
                DataEstimation(era, args.directory, channel)
        ]:
            # Get files for estimation method
            logger.debug("Get files for estimation method %s.",
                         estimation.name)
            files = [str(f) for f in estimation.get_files()]

            # Go through files and get folders for channel
            for f in files:
                if not os.path.exists(f):
                    logger.fatal("File does not exist: %s", f)
                    raise Exception

                folders = []
                f_ = ROOT.TFile(f)
                for k in f_.GetListOfKeys():
                    if "{}_".format(args.channel) in k.GetName():
                        folders.append(k.GetName())
                f_.Close()

                filelist[f] = folders

    ############################################################################

    # Write output filelist
    logger.info("Write filelist to file: {}".format(args.output))
    yaml.dump(filelist, open(args.output, 'w'), default_flow_style=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
