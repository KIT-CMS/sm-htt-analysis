#!/usr/bin/env python

import argparse
import os
import json
import yaml

import matplotlib as mpl
mpl.use('Agg')
mpl.rcParams['font.size'] = 16
import matplotlib.pyplot as plt
from matplotlib import cm

import logging
logger = logging.getLogger("keras_confusion_matrix")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Plot goodness of fit results")
    parser.add_argument(
        "variables", help="Considered variables in goodness of fit test")
    parser.add_argument(
        "path", help="Path to directory with goodness of fit results")
    return parser.parse_args()


def plot_1d(variables, results, filename):
    labels = [v for v in variables if v in results]
    plt.figure(figsize=(len(labels) * 1.0, 7.0))
    y = [results[v] for v in labels]
    x = range(len(y))
    plt.plot(x, y, '+', mew=5, ms=20)
    plt.ylim((-0.05, 1.05))
    plt.xlim((-0.5, len(x) - 0.5))
    plt.xticks(x, labels, rotation='vertical')
    plt.axhline(y=0.05, linewidth=3, color='r')
    plt.ylabel('Saturated goodness of fit p-value', labelpad=20)
    plt.savefig(filename, bbox_inches="tight")


def search_results_1d(path, variables):
    results = {}
    for dir_ in os.listdir(path):
        filename = os.path.join(path, dir_, "gof.json")
        if not os.path.exists(filename):
            continue

        channel = dir_[0:2]
        variable = dir_[3:]
        if not variable in variables:
            continue
        logger.debug(
            "Found goodness of fit result for variable %s in channel %s.",
            variable, channel)

        p_value = json.load(open(filename))

        if not channel in results:
            results[channel] = {}
        results[channel][variable] = p_value["125.0"]["p"]

    return results


def main(args):
    if not os.path.exists(args.variables):
        logger.fatal("File %s does not exist.")
        raise Exception
    if not os.path.exists(args.path):
        logger.fatal("Path %s does not exist.")
        raise Exception

    variables = yaml.load(open(args.variables))["variables"]
    results_1d = search_results_1d(args.path, variables)
    for channel in results_1d:
        plot_1d(variables, results_1d[channel],
                "{}_gof_1d.png".format(channel))


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
