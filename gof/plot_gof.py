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
logger = logging.getLogger("plot_gof")
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
    parser.add_argument(
        "--channels",
        default=["et", "mt", "tt"],
        nargs='+',
        help="Select channels to be plotted")
    return parser.parse_args()


def plot_1d(variables, results, filename):
    labels = [v for v in variables if v in results]
    plt.figure(figsize=(len(labels) * 0.5, 5.0))
    y = [results[v] for v in labels]
    x = range(len(y))
    plt.plot(x, y, '+', mew=4, ms=16)
    plt.ylim((-0.05, 1.05))
    plt.xlim((-0.5, len(x) - 0.5))
    plt.xticks(x, labels, rotation='vertical')
    plt.axhline(y=0.05, linewidth=3, color='r')
    plt.ylabel('Saturated goodness of fit p-value', labelpad=20)
    ax = plt.gca()
    ax.xaxis.grid()
    plt.savefig(filename, bbox_inches="tight")


def search_results_1d(path, channels, variables):
    results = {}
    missing = {}
    for channel in channels:
        results[channel] = {}
        missing[channel] = []
        for variable in variables:
            filename = os.path.join(path, "{}_{}".format(channel, variable),
                                    "gof.json")
            if not os.path.exists(filename):
                missing[channel].append(variable)
                continue
            logger.debug(
                "Found goodness of fit result for variable %s in channel %s.",
                variable, channel)

            p_value = json.load(open(filename))
            results[channel][variable] = p_value["125.0"]["p"]

    return missing, results


def main(args):
    if not os.path.exists(args.variables):
        logger.fatal("File %s does not exist.")
        raise Exception
    if not os.path.exists(args.path):
        logger.fatal("Path %s does not exist.")
        raise Exception

    # Plot 1D gof results
    variables = yaml.load(open(args.variables))["variables"]
    missing_1d, results_1d = search_results_1d(args.path, args.channels,
                                               variables)
    for channel in args.channels:
        logger.debug("Missing variables for 1D plots in channel %s.", channel)
        for variable in missing_1d[channel]:
            print("{} {}".format(channel, variable))

    for channel in args.channels:
        if results_1d[channel] == {}:
            logger.warning("No results found for channel %s.", channel)
            continue
        plot_1d(variables, results_1d[channel],
                "{}_gof_1d.png".format(channel))


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
