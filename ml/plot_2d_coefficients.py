#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
from array import array
import yaml
import pickle
import numpy as np
import os
import sys

import matplotlib as mpl
mpl.use('Agg')
mpl.rcParams['font.size'] = 16
import matplotlib.pyplot as plt
from matplotlib import cm

import logging
logger = logging.getLogger("plot_2d_coefficients")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Plot 2D coefficients.")
    parser.add_argument("--era", required=True, help="Era")
    parser.add_argument("--channel", required=True, help="Channel")
    parser.add_argument("--fold", required=True, help="Training fold")
    parser.add_argument("--process", required=True, help="Process")
    return parser.parse_args()

def main(args):
    logger.info("Era: {}".format(args.era))
    logger.info("Channel: {}".format(args.channel))
    logger.info("Process: {}".format(args.process))
    logger.info("Fold: {}".format(args.fold))

    # Load training config and extract variables
    config_path = "ml/{}_{}_training.yaml".format(args.era, args.channel)
    if not os.path.exists(config_path):
        logger.fatal("Training config {} not found.".format(config_path))
        raise Exception
    config = yaml.load(open(config_path))
    variables = config["variables"]

    logger.info("Use variables {}.".format(variables))

    # Load coefficients
    matrix = np.zeros((len(variables), len(variables)))

    path = "ml/{}_{}/fold{}_keras_taylor_ranking_{}.txt".format(args.era, args.channel, args.fold, args.process)
    if not os.path.exists(path):
        logger.fatal("Failed to load {}.".format(path))
        raise Exception

    for line in open(path).readlines():
        rank, var, score = line.split(":")
        score = float(score.strip())
        var = var.strip().split(", ")
        if len(var) != 2:
            continue
        i1 = variables.index(var[0])
        i2 = variables.index(var[1])
        matrix[i1, i2] = score

    # Make plot
    plt.figure(0, figsize=(len(variables), len(variables)))
    axis = plt.gca()
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if i>j:
                continue
            axis.text(
                i + 0.5,
                j + 0.5,
                '{:.2f}'.format(matrix[i, j]),
                ha='center',
                va='center')
    q = plt.pcolormesh(matrix.T, cmap='Wistia')
    plt.xticks(
        np.array(range(len(variables))) + 0.5, variables, rotation='vertical')
    plt.yticks(
        np.array(range(len(variables))) + 0.5, variables, rotation='horizontal')
    #plt.text(0.7, 0.15, args.process, fontsize=80, transform=plt.gca().transAxes)#, fontweight="bold")
    plt.savefig("ml/{}_{}/fold{}_2d_coefficients_{}.png".format(args.era, args.channel, args.fold, args.process), bbox_inches="tight")


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
