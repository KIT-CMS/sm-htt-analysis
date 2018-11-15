#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

import argparse
import yaml
import os
import numpy as np

import matplotlib as mpl
mpl.use('Agg')
mpl.rcParams['font.size'] = 16
import matplotlib.pyplot as plt
from matplotlib import cm

import logging
logger = logging.getLogger("plot_training_variable_2d")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Plot in a 2D plane the composition of variables in the training datset.")
    parser.add_argument("era", type=str, help="Experiment era.")
    parser.add_argument("channel", type=str, help="Analysis channel.")
    parser.add_argument("target_process", type=str, help="Process considered as target.")
    parser.add_argument("var1", type=str, help="First variable.")
    parser.add_argument("var2", type=str, help="Second variable.")
    parser.add_argument("weight_branch", type=str, help="Branch in dataset with weights.")
    return parser.parse_args()


def main(args):
    # Open file
    path_dataset = "ml/{}_{}/combined_training_dataset.root".format(args.era, args.channel)
    if not os.path.exists(path_dataset):
        logger.fatal("Failed to open {}.".format(path_dataset))
        raise Exception
    logger.info("Process training dataset %s.", path_dataset)
    f = ROOT.TFile(path_dataset)

    # Find background processes
    logger.info("Selected target process: {}".format(args.target_process))
    backgrounds = []
    for key in f.GetListOfKeys():
        name = key.GetName()
        if name not in ["ntuple", args.target_process]:
            backgrounds.append(name)
    logger.info("Selected background processes: {}".format(backgrounds))

    # Load class weights
    path_config = "ml/{}_{}_training.yaml".format(args.era, args.channel)
    logger.info("Load training config: {}".format(path_config))
    config = yaml.load(open(path_config))
    class_weights = config["class_weights"]

    # Fill lists with variables
    logger.info("Aggregate values and weights for variables {} and {}.".format(args.var1, args.var2))
    values_var1 = {}
    values_var2 = {}
    weights = {}
    vetoed_values = [-1, -10, -11, -999, -9]
    for process in [args.target_process] + backgrounds:
        if not process in values_var1:
            values_var1[process] = []
            values_var2[process] = []
            weights[process] = []
        for event in f.Get(process):
            v1 = getattr(event, args.var1)
            v2 = getattr(event, args.var2)
            w = getattr(event, args.weight_branch)#*class_weights[process]
            if v1 in vetoed_values:
                continue
            if v2 in vetoed_values:
                continue
            values_var1[process].append(v1)
            values_var2[process].append(v2)
            weights[process].append(w)

    # Make lists composed of target process and all other processes
    sig_var1 = []
    sig_var2 = []
    sig_weight = []
    bkg_var1 = []
    bkg_var2 = []
    bkg_weight = []
    for process in values_var1:
        if process == args.target_process:
            sig_var1 += values_var1[process]
            sig_var2 += values_var2[process]
            sig_weight += weights[process]
        else:
            bkg_var1 += values_var1[process]
            bkg_var2 += values_var2[process]
            bkg_weight += weights[process]

    # Calculate plotting ranges with percentiles of the signal value ranges
    range_var1 = np.percentile(sig_var1+bkg_var1, [5, 95])
    range_var2 = np.percentile(sig_var2+bkg_var2, [5, 95])
    #range_var1[1] = 50
    #range_var2[1] = 50

    # Plot
    plt.figure(figsize=(7,7))
    plt.xlabel(args.var1)
    plt.ylabel(args.var2)
    range_ = ((range_var1[0], range_var1[-1]), (range_var2[0], range_var2[-1]))
    for var1, var2, weights, cmap, label, color in zip([bkg_var1, sig_var1], [bkg_var2, sig_var2], [bkg_weight, sig_weight], [plt.cm.Blues, plt.cm.Reds], ["Other classes", args.target_process], ["blue", "red"]):
        counts, xbins, ybins, image = plt.hist2d(
            var1,
            var2,
            bins=10,
            range=range_,
            cmap=cmap,
            weights=weights,
            normed=True,
            alpha=0.0)
        plt.contour(
           counts.T,
           extent=[xbins.min(),
           xbins.max(),
           ybins.min(),
           ybins.max()],
           linewidths=3,
           cmap=cmap,
           alpha=1.0)
        plt.plot([-999], [-999], color=color, label=label, lw=3)
    """
    ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels))
    """
    plt.savefig("plot_training_variable_{}_{}_{}_{}_{}.png".format(args.era, args.channel, args.target_process, args.var1, args.var2), bbox_inches="tight")

    # Clean-up
    f.Close()

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
