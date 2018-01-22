#!/usr/bin/env python

import argparse
import numpy as np
import yaml
import os
from copy import deepcopy

import logging
logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Create binning for HIG16043 analysis and write to output YAML file.")

    parser.add_argument("output", type=str, help="Output YAML file")

    return parser.parse_args()


def main(args):
    output = {"HIG16043": {}}

    et = {}
    mt = {}
    tt = {}

    ###########################################################################

    # Category: 0jet

    # Channel: et, mt

    cat = {"variable": None, "binning": None, "expression": None, "cut": None}

    cat["variable"] = "m_vis"

    binning_steps = range(60, 115, 5) + [400]
    binning = [0]
    for i in range(3):
        binning += [b + i * binning_steps[-1] for b in binning_steps]
    cat["binning"] = binning

    expression_bins = ["decayMode_2==0", "decayMode_2==1", "decayMode_2==10"]
    expression = ""
    for i, e in enumerate(expression_bins):
        expression += "({BIN})*({VARIABLE}+{OFFSET}*{NUM_BIN})".format(
            BIN=e,
            VARIABLE=cat["variable"],
            OFFSET=binning_steps[-1],
            NUM_BIN=i)
        if i != len(expression_bins) - 1:
            expression += " + "
    cat["expression"] = expression

    cat["cut"] = "(m_vis<400)&&(njets==0)"

    et["0jet"] = deepcopy(cat)
    mt["0jet"] = deepcopy(cat)

    # Channel: tt

    cat["variable"] = "m_sv"
    cat["expression"] = None
    cat["cut"] = "njets==0"
    cat["binning"] = [0] + range(50, 310, 10)

    tt["0jet"] = deepcopy(cat)

    ###########################################################################

    # Category: VBF

    # Channel: et, mt

    cat["variable"] = "m_sv"
    cat["cut"] = "(m_sv<400)&&(mjj>300)&&(njets>1)"

    binning_steps = range(95, 160, 20) + [400]
    binning = [0]
    for i in range(4):
        binning += [b + i * binning_steps[-1] for b in binning_steps]
    cat["binning"] = binning

    expression_bins = [
        "(mjj>300)*(mjj<700)", "(mjj>700)*(mjj<1100)", "(mjj>1100)*(mjj<1500)",
        "(mjj>1500)"
    ]
    expression = ""
    for i, e in enumerate(expression_bins):
        expression += "({BIN})*({VARIABLE}+{OFFSET}*{NUM_BIN})".format(
            BIN=e,
            VARIABLE=cat["variable"],
            OFFSET=binning_steps[-1],
            NUM_BIN=i)
        if i != len(expression_bins) - 1:
            expression += " + "
    cat["expression"] = expression

    et["vbf"] = deepcopy(cat)
    mt["vbf"] = deepcopy(cat)

    # Channel: tt

    cat["variable"] = "m_sv"
    cat["cut"] = "(m_sv<250)&&(mjj>0)&&(njets>1)"

    binning_steps = [40, 60] + range(70, 140, 10) + [150, 200, 250]
    binning = [0]
    for i in range(4):
        binning += [b + i * binning_steps[-1] for b in binning_steps]
    cat["binning"] = binning

    expression_bins = [
        "(mjj>0)*(mjj<300)", "(mjj>300)*(mjj<500)", "(mjj>500)*(mjj<800)",
        "(mjj>800)"
    ]
    expression = ""
    for i, e in enumerate(expression_bins):
        expression += "({BIN})*({VARIABLE}+{OFFSET}*{NUM_BIN})".format(
            BIN=e,
            VARIABLE=cat["variable"],
            OFFSET=binning_steps[-1],
            NUM_BIN=i)
        if i != len(expression_bins) - 1:
            expression += " + "
    cat["expression"] = expression

    tt["vbf"] = deepcopy(cat)

    ###########################################################################

    # Category: Boosted

    # Channel: et, mt

    cat["variable"] = "m_sv"
    cat["cut"] = "(m_sv<300)&&(pt_tt>0)&&(njets==1)"

    binning_steps = range(80, 170, 10) + [300]
    binning = [0]
    for i in range(6):
        binning += [b + i * binning_steps[-1] for b in binning_steps]
    cat["binning"] = binning

    expression_bins = [
        "(pt_tt>{})*(pt_tt<{})".format(a, b)
        for a, b in [[0, 100], [100, 150], [150, 200], [200, 250], [250, 300]]
    ] + ["pt_tt>300"]
    expression = ""
    for i, e in enumerate(expression_bins):
        expression += "({BIN})*({VARIABLE}+{OFFSET}*{NUM_BIN})".format(
            BIN=e,
            VARIABLE=cat["variable"],
            OFFSET=binning_steps[-1],
            NUM_BIN=i)
        if i != len(expression_bins) - 1:
            expression += " + "
    cat["expression"] = expression

    et["boosted"] = deepcopy(cat)
    mt["boosted"] = deepcopy(cat)

    # Channel: tt

    cat["variable"] = "m_sv"
    cat["cut"] = "(m_sv<250)*(pt_tt>0)&&(njets==1)"

    binning_steps = [40] + range(60, 140, 10) + [150, 200, 250]
    binning = [0]
    for i in range(4):
        binning += [b + i * binning_steps[-1] for b in binning_steps]
    cat["binning"] = binning

    expression_bins = [
        "(pt_tt>{})*(pt_tt<{})".format(a, b)
        for a, b in [[0, 100], [100, 170], [170, 300]]
    ] + ["pt_tt>300"]
    expression = ""
    for i, e in enumerate(expression_bins):
        expression += "({BIN})*({VARIABLE}+{OFFSET}*{NUM_BIN})".format(
            BIN=e,
            VARIABLE=cat["variable"],
            OFFSET=binning_steps[-1],
            NUM_BIN=i)
        if i != len(expression_bins) - 1:
            expression += " + "
    cat["expression"] = expression

    tt["boosted"] = deepcopy(cat)

    ###########################################################################

    # Write output

    output["HIG16043"]["et"] = et
    output["HIG16043"]["mt"] = mt
    output["HIG16043"]["tt"] = tt
    yaml.dump(output, open(args.output, "w"))


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
