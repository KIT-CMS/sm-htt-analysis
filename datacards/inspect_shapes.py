#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import ROOT
import os

import logging
logger = logging.getLogger("")


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "a")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Inspect shapes from ROOT file for the datacards.")
    parser.add_argument(
        "--files",
        "-f",
        required=True,
        type=str,
        nargs="+",
        help="Datacard ROOT files to be compared.")
    parser.add_argument(
        "--processes",
        "-p",
        required=True,
        type=str,
        nargs="+",
        help=
        "Processes to be compared. If only one name is given, then this name is searched in all input files. Otherwise, the same number of processes as input files have to be declared."
    )
    parser.add_argument(
        "--tag",
        "-t",
        type=str,
        default=None,
        help=
        "Substring that has to be present in the directory name in the ROOT file so that the histograms are considered in the inspection."
    )
    return parser.parse_args()


def main(args):
    if len(args.processes) == 1:
        args.processes = args.processes * len(args.files)
    elif len(args.files) != len(args.processes):
        logger.fatal("Number of files has to match number of processes.")
        raise Exception
    for index, (path, process) in enumerate(zip(args.files, args.processes)):
        f = ROOT.TFile(path)
        if f == None:
            logger.fatal("File {} does not exist.".format(path))
            raise Exception
        basename = os.path.basename(path)
        for key in f.GetListOfKeys():
            name = key.GetName()
            if args.tag != None:
                if not args.tag in name:
                    continue
            h = f.Get(os.path.join(name, process))
            if not h == None:
                logger.info("{:<4} : {:<20} : {:<10} : {:<20} : {:.2f}".format(
                    index + 1, basename, process, name, h.Integral()))


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("inspect_shapes.log", logging.DEBUG)
    main(args)
