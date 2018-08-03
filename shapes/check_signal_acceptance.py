#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import os
import numpy as np

import logging
import re
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
        description="Check acceptance of signals in different categories.")
    parser.add_argument("shapes", type=str, help="ROOT file with shapes.")
    parser.add_argument(
        "--veto-folder",
        default=["sum", "_ss_", "unrolled"],
        help="Veto folders in the input file with sub-strings.")
    parser.add_argument(
        "--signals",
        default=[
            "qqH_VBFTOPO_JET3VETO", "qqH_VBFTOPO_JET3", "qqH_REST",
            "qqH_PTJET1_GT200", "qqH_VH2JET", "ggH_0J", "ggH_1J_PTH_0_60",
            "ggH_1J_PTH_60_120", "ggH_1J_PTH_120_200", "ggH_1J_PTH_GT200",
            "ggH_GE2J_PTH_0_60", "ggH_GE2J_PTH_60_120", "ggH_GE2J_PTH_120_200",
            "ggH_GE2J_PTH_GT200", "ggH_VBFTOPO_JET3VETO", "ggH_VBFTOPO_JET3"
        ],
        help="Signals to be checked.")
    parser.add_argument("--mass", default=125, help="Mass of the signals.")
    return parser.parse_args()


def main(args):
    # Open file with shapes
    if not os.path.exists(args.shapes):
        logger.fatal("File %s does not exist.", args.shapes)
        raise Exception
    file_ = ROOT.TFile(args.shapes, "READ")

    # Find complete set of folders for the analysis
    dirnames = []
    for key in file_.GetListOfKeys():
        dirname = key.GetName()
        skip = False
        for s in args.veto_folder:
            if s in dirname:
                skip = True
        if skip:
            continue
        dirnames.append(dirname)
    logger.info("Selected directories: %s", dirnames)

    # Cumulate inclusive yield for signals
    yields = {}
    for signal in args.signals:
        yields[signal] = 0.0
        for dirname in dirnames:
            d = file_.Get(dirname)
            histname = "{}{}".format(signal, args.mass)
            h = d.Get(histname)
            if h == None:
                logger.critical("Failed to find histogram %s in folder %s.",
                                histname, dirname)
                raise Exception
            yields[signal] += h.Integral()

    for signal in args.signals:
        logger.info("Inclusive yield for signal %s: %g", signal,
                    yields[signal])

    # Get acceptances for each category
    for signal in args.signals:
        logger.debug("--------------------------------------")
        logger.debug("Acceptances of signal %s.", signal)
        logger.debug("--------------------------------------")
        for dirname in dirnames:
            d = file_.Get(dirname)
            histname = "{}{}".format(signal, args.mass)
            h = d.Get(histname)
            if h == None:
                logger.critical("Failed to find histogram %s in folder %s.",
                                histname, dirname)
                raise Exception
            y = h.Integral()
            a = y / yields[signal]
            if a > 1e-1:
                logger.warning(
                    "Acceptance (and yield) of signal %s in folder %s: %g (%g)",
                    signal, dirname, a, y)
            else:
                logger.info(
                    "Acceptance (and yield) of signal %s in folder %s: %g (%g)",
                    signal, dirname, a, y)

    # Clean-up
    file_.Close()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("check_signal_acceptance.log", logging.DEBUG)
    main(args)
