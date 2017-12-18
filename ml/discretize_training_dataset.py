#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import yaml
import numpy as np
from array import array

import logging
logger = logging.getLogger("write_application_filelist")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Discretize training dataset.")
    parser.add_argument(
        "binning", help="Path to variable binning from goodness of fit tests.")
    parser.add_argument("channel", help="Select the channel.")
    parser.add_argument("input", help="Path to input training dataset.")
    parser.add_argument(
        "output", help="Path to discretized output training dataset.")
    parser.add_argument(
        "--training-weight-branch",
        default="training_weight",
        help="Branch with training weights.")
    parser.add_argument(
        "--modify-num-bins",
        default=0,
        type=int,
        help=
        "Modify the number of bins used for discretization. The min and max of the range is still taken from the goodness of fit binning."
    )
    return parser.parse_args()


def main(args):
    # Load binning
    logger.debug("Load binning from {} for channel {}.".format(
        args.binning, args.channel))
    config = yaml.load(open(args.binning))
    binning_all = config["gof"][args.channel]
    variables = binning_all.keys()
    binning = {v: binning_all[v]["bins"] for v in binning_all}
    logger.debug("Use variables {}.".format(variables))

    # Calculate mids
    mids = {}
    ranges = {}
    for variable in variables:
        x = binning[variable]
        ranges[variable] = [x[0], x[-1]]
        if args.modify_num_bins != 0:
            x = np.linspace(x[0], x[-1], args.modify_num_bins)
        mids[variable] = np.array(x[1:]) - 0.5 * (x[1] - x[0])

    # Read variables and discretize them
    logger.debug(
        "Load input file {} and extract training dataset with discretized values.".
        format(args.input))
    file_in = ROOT.TFile(args.input, "READ")
    classes = {}
    weights = {}
    for key in file_in.GetListOfKeys():
        name = key.GetName()
        tree = file_in.Get(name)
        logger.debug("Process class {}.".format(name))
        classes[name] = np.zeros((tree.GetEntries(), len(variables)))
        weights[name] = np.zeros(tree.GetEntries())
        for i_event, event in enumerate(tree):
            weights[name][i_event] = getattr(event,
                                             args.training_weight_branch)
            for i_variable, variable in enumerate(variables):
                x = getattr(event, variable)
                if x in [-11, -10, -9, -999]:
                    x_discretized = x
                else:
                    i_bin = np.argmin(np.abs(mids[variable] - x))
                    x_discretized = mids[variable][i_bin]
                classes[name][i_event, i_variable] = x_discretized

    # Write out the new dataset
    logger.debug("Write output file {} with discretized values.".format(
        args.output))
    file_out = ROOT.TFile(args.output, "RECREATE")

    for name in classes:
        logger.debug("Write class %s.", name)
        tree = ROOT.TTree(name, name)

        values = {}
        for v in variables:
            values[v] = array("f", [-999])
            tree.Branch(str(v), values[v], str(v) + "/F")
        value_weight = array("f", [-999])
        name_weight = args.training_weight_branch
        tree.Branch(str(name_weight), value_weight, str(name_weight) + "/F")

        for weight, event in zip(weights[name], classes[name]):
            value_weight[0] = weight
            for i, v in enumerate(variables):
                values[v][0] = event[i]
            tree.Fill()
        tree.Write()

    # Clean-up
    file_in.Close()
    file_out.Write()
    file_out.Close()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
