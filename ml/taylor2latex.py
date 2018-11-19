#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import numpy as np
import os
import sys

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
    parser.add_argument("--processes", nargs="+", required=True, help="Processes")
    parser.add_argument("--rows", required=True, type=int, help="Number of rows in the table")
    return parser.parse_args()

def main(args):
    logger.info("Era: {}".format(args.era))
    logger.info("Channel: {}".format(args.channel))
    logger.info("Processes: {}".format(args.processes))

    # Load coefficients
    coef = {}
    for process in args.processes:
        coef[process] = {}
        for fold in [0, 1]:
            path = "ml/{}_{}/fold{}_keras_taylor_ranking_{}.txt".format(args.era, args.channel, fold, process)
            if not os.path.exists(path):
                logger.fatal("Failed to load {}.".format(path))
                raise Exception
            for line in open(path).readlines():
                var, score = line.split(":")[1:]
                var = var.strip()
                score = float(score.strip())
                if not var in coef[process].keys():
                    coef[process][var] = score
                else:
                    coef[process][var] += score
                    coef[process][var] *= 0.5

    # Sort and reduce data
    table = {}
    for process in args.processes:
        table[process] = []
        for key, value in reversed(sorted(coef[process].iteritems(), key=lambda (k,v): (v,k))):
            table[process].append((key, value))

    # Print table
    table_str = ""
    for process in args.processes:
        table_str += "  \\multicolumn{3}{c}{\\texttt{%s}} &" % process
    table_str = table_str[:-1]
    table_str += "\\\\\n"
    table_str += "\\hline\n"
    for i in range(args.rows):
        line = ""
        for process in args.processes:
            var = table[process][i][0].replace("_", "\\_").split(", ")
            score = table[process][i][1]
            if len(var) == 2:
                line += " \\texttt{%s} & \\texttt{%s} & %.2f &" % (var[0], var[1], score)
            else:
                line += " \\multicolumn{2}{c}{\\texttt{%s}} & %.2f &" % (var[0], score)
        line = line[:-1]
        line += "\\\\\n"
        table_str += line
    table_str += "\\hline\n"

    print(table_str)

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
