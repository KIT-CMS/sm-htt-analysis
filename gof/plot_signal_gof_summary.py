#!/usr/bin/env python

import argparse
import os
import json
import numpy as np
from scipy.stats import chisquare

import matplotlib as mpl
from matplotlib import rc
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
rc('text', usetex=True)

mpl.use("Agg")
mpl.rcParams["font.size"] = 16
import matplotlib.pyplot as plt
from matplotlib import cm

import logging

logger = logging.getLogger("plot_gof")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

category_dict = {
    "1":   r"2D $ggh/qqh $",
    "12":  r"$ztt$",
    "15":  r"$zll$",
    "11":  r"$wjets$",
    "13":  r"$tt$",
    "14":  r"$qcd$",
    "16":  r"$misc$",
    "17":  r"$qcd$",
    "19":  r"$diboson$",
    "20":  r"Genuine $\tau$",
    "21":  r"Jet $\rightarrow$ $\tau_{h}$",
    "100": r"ggh 0-jet, $p_{T}^{H} [0,10]$",
    "101": r"ggh 0-jet, $p_{T}^{H} > 10$",
    "102": r"ggh 1-jet, $p_{T}^{H} [0,60]$",
    "103": r"ggh 1-jet, $p_{T}^{H} [60,120]$",
    "104": r"ggh 1-jet, $p_{T}^{H} [120,200]$",
    "105": r"ggh 2-jet, $mjj [0,350], p_{T}^{H} [0,60]$",
    "106": r"ggh 2-jet, $mjj [0,350], p_{T}^{H} [60,120]$",
    "107": r"ggh 2-jet, $mjj [0,350], p_{T}^{H} [120,200]$",
    "108": r"ggh $p_{T}^{H} [200,300]$",
    "109": r"ggh $p_{T}^{H} > 300$",
    "110": r"ggh 2-jet, $mjj > 350, p_{T}^{H} [0,200]$",
    "200": r"qqh 2-jet $low mjj$",
    "201": r"qqh $p_{T}^{H} > 200$",
    "202": r"qqh vbftopo $mjj > 700$",
    "203": r"qqh vbftopo $mjj [350,700]$",
}


def csv_list(string):
    return string.split(",")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Plot goodness of fit results")
    parser.add_argument("--path",
                        help="Path to directory with goodness of fit results")
    parser.add_argument("--outputpath",
                        help="Path where to save the output plots")
    parser.add_argument("--mode", help="Plotting mode")
    parser.add_argument("--tags", help="tags of the shapes", type=csv_list)
    parser.add_argument("--channels",
                        help="list of selected channels",
                        type=csv_list)
    parser.add_argument("--eras", help="list of selected eras", type=csv_list)
    return parser.parse_args()


def make_cmap(colors, position):
    if len(position) != len(colors):
        raise Exception("position length must be the same as colors")
    elif position[0] != 0 or position[-1] != 1:
        raise Exception("position must start with 0 and end with 1")

    cdict = {"red": [], "green": [], "blue": []}
    for pos, color in zip(position, colors):
        cdict["red"].append((pos, color[0], color[0]))
        cdict["green"].append((pos, color[1], color[1]))
        cdict["blue"].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap("my_colormap", cdict, 256)
    return cmap


def gen_catlist(channel, tag):
    catlist = []
    if "stage0" in tag:
        signallist = ["1"]
    elif "stage1p1" in tag:
        signallist = [
            "100", "101", "102", "103", "104", "105", "106", "107", "108",
            "109", "110", "200", "201", "202", "203"
        ]
    if channel == "em":
        catlist = ["13", "14", "16", "19", "20"]
    elif channel == "et":
        catlist = ["13", "15", "16", "20", "21"]
    elif channel == "mt":
        catlist = ["13", "15", "16", "20", "21"]
    elif channel == "tt":
        catlist = ["16", "20", "21"]
    logger.debug("Using {}".format(catlist + signallist))
    return catlist + signallist


def plot_1d(era, channel, labels, results, filename):
    plt.figure(figsize=(len(labels) * 0.5, 5.0))
    y = results
    x = range(len(y))
    plt.plot(x, y, "+", mew=4, ms=16)
    plt.ylim((-0.05, 1.05))
    plt.xlim((-0.5, len(x) - 0.5))
    plt.xticks(x, labels, rotation="vertical")
    plt.axhline(y=0.05, linewidth=3, color="r")
    plt.ylabel("Saturated goodness of fit p-value", labelpad=20)
    ax = plt.gca()
    if args.mode == "2":
        ax.set_xticks([x_mod - 1.5 for x_mod in x if x_mod % 12 == 1],
                      minor=True)
    elif args.mode == "1":
        if len(labels) > 40:
            # in this case stage1 results
            if channel == "tt":
                ax.set_xticks([x_mod - 1.5 for x_mod in x if x_mod % 18 == 1],
                            minor=True)
            else:
                ax.set_xticks([x_mod - 1.5 for x_mod in x if x_mod % 20 == 1],
                            minor=True)
        else:
            if channel == "tt":
                ax.set_xticks([x_mod - 1.5 for x_mod in x if x_mod % 4 == 1],
                            minor=True)
            else:
                ax.set_xticks([x_mod - 1.5 for x_mod in x if x_mod % 6 == 1],
                            minor=True)
    for i, v in enumerate(y):
        if v <= 0.05:
            ax.text(i - 0.25, 0.25, str(v), rotation="vertical")
    # ax.xaxis.grid()
    ax.xaxis.grid(True, which="minor")
    logger.info("Generating {}.png".format(filename))
    plt.savefig("{}/{}.png".format(args.outputpath, filename),
                bbox_inches="tight")
    plt.savefig("{}/{}.pdf".format(args.outputpath, filename),
                bbox_inches="tight")

def plot_test_dist(tag, results, filename):
    plt.figure(figsize=(5.0, 5.0))
    n, bins, patched = plt.hist(results, bins=10)
    print(n)
    print(chisquare(n))
    plt.xlim((0.0, 1.0))
    plt.axvline(x=0.05, linewidth=3, color="r")
    plt.xlabel("Saturated goodness of fit p-value", labelpad=20)
    plt.ylabel("Number of Tests", labelpad=20)
    logger.info("Generating {}.png".format(filename))
    #ax = plt.gca()
    #ax.set_xscale('log')
    plt.savefig("{}/{}.png".format(args.outputpath, filename),
                bbox_inches="tight")
    plt.savefig("{}/{}.pdf".format(args.outputpath, filename),
                bbox_inches="tight")


def search_results_1d(path, channel, era, variable, tag):
    filename = os.path.join(path, "{}-{}-{}-{}".format(tag, era, channel,
                                                       variable), "gof.json")
    logger.debug("Parsing {}".format(filename))
    if not os.path.exists(filename):
        result = -1.0
    else:
        logger.debug(
            "Found goodness of fit result for variable %s in channel %s.",
            variable,
            channel,
        )
        p_value = json.load(open(filename))
        result = p_value["125.0"]["p"]
    return result


def main(args):
    if not os.path.exists(args.path):
        logger.fatal("Path %s does not exist.")
        raise Exception
    if args.mode == "1":
        print(args.tags, args.channels, args.eras)
        # Plot 1D gof results
        for tag in args.tags:
            for channel in args.channels:
                results = []
                labels = []
                print(channel, tag)
                for era in args.eras:
                    for category in gen_catlist(channel, tag):
                        results.append(
                            search_results_1d(
                                args.path,
                                channel,
                                era,
                                "NNOutput-{}".format(category),
                                tag,
                            ))
                        labels.append("{} {} {}".format(
                            channel, category_dict[category], era))
                logger.debug("Data for plot: {}".format(results))
                logger.debug("Data for plot: {}".format(labels))
                plot_1d(
                    era,
                    channel,
                    labels,
                    results,
                    "gof_1d_{}_{}".format(channel, tag),
                )
    if args.mode == "2":
        results = []
        labels = []
        filename = ""
        if len(args.tags) > 1:
            filename = "all"
        else:
            filename = args.tags[0]
        for tag in args.tags:
            for era in args.eras:
                for channel in args.channels:
                    results.append(
                        search_results_1d(args.path, channel, era,
                                          "NNOutput-{}".format(999), tag))
                    labels.append("{} {}".format(channel, era))

        plot_1d(era, channel, labels, results,
                "gof_1d_{}_{}".format("combined", filename))
    if args.mode == "3":
        for tag in args.tags:
            results = []
            labels = []
            for era in args.eras:
                for channel in args.channels:
                    for category in gen_catlist(channel, tag):
                        result = search_results_1d(
                            args.path, channel, era,
                            "NNOutput-{}".format(category), tag)
                        if result <= 0.05:
                            results.append(result)
                            labels.append("{}-{}-{}".format(
                                category, channel, era))
                        logger.debug("Data for plot: {}".format(results))
                        logger.debug("Data for plot: {}".format(labels))
            if len(results) > 0:
                plot_1d(
                    era,
                    channel,
                    labels,
                    results,
                    "gof_1d_{}_{}".format("failing", tag),
                )
    if args.mode == "4":
        for tag in args.tags:
            results = []
            for era in args.eras:
                for channel in args.channels:
                    for category in gen_catlist(channel, tag):
                        result = search_results_1d(
                            args.path, channel, era,
                            "NNOutput-{}".format(category), tag)
                        if result >= 0.90:
                            print("High value for {}-{}-{}: {}".format(era,channel,category,result))
                        if result >= 0.00:
                            results.append(result)
            plot_test_dist(tag, results, "{}_p_dist".format(tag))


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
