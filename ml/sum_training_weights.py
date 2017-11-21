#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

import argparse

import logging
logger = logging.getLogger("write_dataset_config")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Sum training weights of classes in training dataset.")
    parser.add_argument("dataset", type=str, help="Training dataset.")
    parser.add_argument(
        "classes", type=str, nargs="+", help="Classes to be considered.")
    parser.add_argument(
        "--weight-branch",
        default="training_weight",
        type=str,
        help="Branch with weights.")
    return parser.parse_args()


def main(args):
    logger.info("Process training dataset %s.", args.dataset)
    f = ROOT.TFile(args.dataset)
    counts = []
    sum_all = 0.0
    for name in args.classes:
        logger.debug("Process class %s.", name)
        sum_ = 0.0
        tree = f.Get(name)
        if tree == None:
            logger.fatal("Tree %s does not exist in file.", name)
            raise Exception
        for event in tree:
            sum_ += getattr(event, args.weight_branch)
        sum_all += sum_
        counts.append(sum_)

    for i, name in enumerate(args.classes):
        logger.info(
            "Class {} (sum, fraction, inverse): {:g}, {:g}, {:g}".format(
                name, counts[i], counts[i] / sum_all, sum_all / counts[i]))


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
