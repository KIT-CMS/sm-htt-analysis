#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

from shape_producer.channel import *
from shape_producer.estimation_methods_2016 import *
from shape_producer.era import Run2016

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
    parser.add_argument("--channel", required=True, help="Analysis channel")
    parser.add_argument("--output", required=True, help="Output filelist")
    return parser.parse_args()


def main(args):
    # Write arparse arguments to YAML config
    filelist = {}

    # Set up era and channel
    era = Run2016(args.database)

    if args.channel == "mt":
        channel = MT()
    else:
        logger.fatal("Channel %s is not implemented.", args.channel)
        raise Exception

    for estimation in [
            ggHEstimation(era, args.directory, channel),
            qqHEstimation(era, args.directory, channel),
            VHEstimation(era, args.directory, channel),
            ZTTEstimation(era, args.directory, channel),
            ZLEstimationMT(era, args.directory, channel),
            ZJEstimationMT(era, args.directory, channel),
            TTTEstimationMT(era, args.directory, channel),
            TTJEstimationMT(era, args.directory, channel),
            WEstimation(era, args.directory, channel),
            VVEstimation(era, args.directory, channel),
            DataEstimation(era, args.directory, channel)
    ]:
        # Get files for estimation method
        logger.debug("Get files for estimation method %s.", estimation.name)
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

    # Write output filelist
    logger.info("Write filelist to file: {}".format(args.output))
    yaml.dump(filelist, open(args.output, 'w'), default_flow_style=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
