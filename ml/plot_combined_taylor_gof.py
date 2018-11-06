#!/usr/bin/env python

import matplotlib as mpl
mpl.use('Agg')
mpl.rcParams['font.size'] = 16
import matplotlib.pyplot as plt
from matplotlib import cm

import argparse
import yaml
import json
import os

import numpy as np

import logging
logger = logging.getLogger("keras_taylor_ranking")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def make_cmap(colors, position):
    if len(position) != len(colors):
        raise Exception("position length must be the same as colors")
    elif position[0] != 0 or position[-1] != 1:
        raise Exception("position must start with 0 and end with 1")

    cdict = {'red': [], 'green': [], 'blue': []}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap', cdict, 256)
    return cmap


def parse_arguments():
    parser = argparse.ArgumentParser(description="Produce confusion matrice")
    parser.add_argument(
        "era",
        type=str,
        help="Experiment era.")
    parser.add_argument(
        "taylor_ranking",
        type=str,
        help=
        "YAML output of combined ranking with Taylor coefficient technique.")
    parser.add_argument(
        "gof_results",
        type=str,
        help="Path to directory with saturated goodness of fit results.")
    parser.add_argument("channel", type=str, help="Name of the channel.")
    parser.add_argument(
        "fold", type=int, help="Number of fold used for training of the NN.")
    parser.add_argument(
        "output_path",
        type=str,
        help="Path to the output directory of the plots.")
    return parser.parse_args()


def main(args):
    # Load Taylor ranking results
    ranking = yaml.load(open(args.taylor_ranking))

    # Get variables, variable pairs and ranking results
    variables = []
    ranking_variables = []
    variable_pairs = []
    ranking_variable_pairs = []
    for entry in ranking:
        v = entry["variables"]
        s = entry["score"]
        if len(v) == 1:
            variables.append(v[0])
            ranking_variables.append(s)
            logger.info("Registered variable {} with ranking {}.".format(
                v[0], s))
        elif len(v) == 2:
            variable_pairs.append(v)
            ranking_variable_pairs.append(s)
            logger.info("Registered variable pair {} with ranking {}.".format(
                v, s))
        else:
            logger.fatal("Invalid entry found.")
            raise Exception

    # Create labels for variables and pairs
    labels_variables = variables
    labels_variable_pairs = [", ".join(p) for p in variable_pairs]

    # Search for gof results in directory
    gof_variables = []
    for v in variables:
        dir_name = "{}_{}_{}".format(args.era, args.channel, v)
        path = os.path.join(args.gof_results, dir_name)
        if not os.path.exists(path):
            logger.warning(
                "Failed to find goodness of fit directory for channel {} and variable {}.".
                format(args.channel, v))
            gof_variables.append(np.nan)
            continue

        path = os.path.join(path, "gof.json")
        if not os.path.exists(path):
            logger.warning(
                "Failed to find goodness of fit result for channel {} and variable {}.".
                format(args.channel, v))
            gof_variables.append(np.nan)
            continue

        p = json.load(open(path))["125.0"]["p"]
        gof_variables.append(p)

    gof_variable_pairs = []
    for v in variable_pairs:
        if v[0] == v[1]:
            gof_variable_pairs.append(np.nan)
            continue

        path_1 = os.path.join(args.gof_results, "{}_{}_{}".format(
            args.era, args.channel, "_".join(v)))
        path_2 = os.path.join(args.gof_results, "{}_{}_{}".format(
            args.era, args.channel, "_".join(reversed(v))))
        if not (os.path.exists(path_1) or os.path.exists(path_2)):
            logger.warning(
                "Failed to find goodness of fit directory for channel {} and variable pair {}.".
                format(args.channel, v))
            gof_variable_pairs.append(np.nan)
            continue
        else:
            if os.path.exists(path_1):
                path = path_1
            else:
                path = path_2

        path = os.path.join(path, "gof.json")
        if not os.path.exists(path):
            logger.warning(
                "Failed to find goodness of fit result for channel {} and variable pair {}.".
                format(args.channel, v))
            gof_variable_pairs.append(np.nan)
            continue

        p = json.load(open(path))["125.0"]["p"]
        gof_variable_pairs.append(p)

    # Plot combination of gof and Taylor ranking for variables (1D)
    plt.figure(figsize=(len(variables) * 0.5, 5.0))
    x = range(len(variables))
    ax1 = plt.gca()
    ax1.axhline(y=0.05, linewidth=3, color='tab:red', alpha=0.8)
    ax1.plot(x, gof_variables, "+", mew=4, ms=16, alpha=0.8, color="tab:blue")
    ax1.set_ylabel(
        "Saturated goodness of fit p-value", labelpad=20, color="tab:blue")
    ax1.set_ylim((-0.05, 1.05))
    ax1.set_xlim((-0.5, len(variables) - 0.5))
    ax1.set_xticks(x)
    ax1.set_xticklabels(variables, rotation=90)
    ax1.xaxis.grid()

    ax2 = ax1.twinx()
    ax2.plot(
        x, ranking_variables, "+", mew=4, ms=16, alpha=0.8, color="tab:orange")
    ax2.set_ylabel(
        "Neural network sensitivity $\\langle t_{i} \\rangle$",
        labelpad=20,
        color="tab:orange")
    ax2.set_ylim((-0.01, np.max(ranking_variables) * 1.05))

    plot_path = os.path.join(args.output_path,
                             "fold{}_combined_taylor_gof_1D.png".format(
                                 args.fold))
    logger.info("Save plot to {}.".format(plot_path))
    plt.savefig(plot_path, bbox_inches="tight")

    # Plot combination of gof and Taylor ranking for variable pairs (2D)
    matrix_ranking = np.ones((len(variables), len(variables))) * (np.nan)
    matrix_gof = np.ones((len(variables), len(variables))) * (np.nan)
    for p, r, g in zip(variable_pairs, ranking_variable_pairs,
                       gof_variable_pairs):
        idx_1 = variables.index(p[0])
        idx_2 = variables.index(p[1])

        matrix_ranking[idx_1, idx_2] = r
        matrix_ranking[idx_2, idx_1] = r

        if idx_1 == idx_2:
            matrix_gof[idx_1, idx_1] = gof_variables[idx_1]
        else:
            matrix_gof[idx_1, idx_2] = g
            matrix_gof[idx_2, idx_1] = g

    plt.figure(figsize=(1.5 * len(variables), 1.0 * len(variables)))
    ax = plt.gca()

    for i1 in range(len(variables)):
        for i2 in range(len(variables)):
            ax.text(
                i1 + 0.5,
                i2 + 0.5,
                "{0:.2f}\n".format(matrix_gof[i1, i2], matrix_ranking[i1, i2]),
                ha="center",
                va="center")
            ax.text(
                i1 + 0.5,
                i2 + 0.5,
                "\n{1:.2f}".format(matrix_gof[i1, i2], matrix_ranking[i1, i2]),
                ha="center",
                va="center",
                weight="bold")

    cmap = make_cmap([(1, 0, 0), (1, 1, 0), (0, 1, 0)],
                     np.array([0.0, 0.05, 1.0]))
    cmap.set_bad(color='w')
    matrix_ranking = np.ma.masked_invalid(matrix_ranking)
    matrix_gof = np.ma.masked_invalid(matrix_gof)
    p = plt.pcolormesh(matrix_gof.T, vmin=0.0, vmax=1.0, cmap=cmap)
    cbar = plt.colorbar(p)
    cbar.set_label(
        'Saturated goodness of fit p-value', rotation=270, labelpad=30)

    plt.xticks(
        np.array(range(len(variables))) + 0.5, variables, rotation='vertical')
    plt.yticks(
        np.array(range(len(variables))) + 0.5,
        variables,
        rotation='horizontal')
    plt.xlim(0, len(variables))
    plt.ylim(0, len(variables))
    plot_path = os.path.join(args.output_path,
                             "fold{}_combined_taylor_gof_2D.png".format(
                                 args.fold))
    logger.info("Save plot to {}.".format(plot_path))
    plt.savefig(plot_path, bbox_inches="tight")


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
