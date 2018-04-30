#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

from shape_producer.cutstring import Cut, Cuts
from shape_producer.channel import ETSM, MTSM, TTSM
from shape_producer.process import Process

import argparse
import numpy as np
import yaml

import logging
logger = logging.getLogger("calculate_binning.py")


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Calculate binning for goodness of fit tests.")

    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--era", required=True, type=str, help="Experiment era.")
    parser.add_argument(
        "--datasets", required=True, type=str, help="Kappa datsets database.")
    parser.add_argument(
        "--output",
        required=True,
        type=str,
        help="Output path for binning config.")
    parser.add_argument(
        "--variables", required=True, help="Variables to be considered.")
    return parser.parse_args()


def get_properties(dict_, era, channel, directory, additional_cuts):
    # Get data estimation method
    if "2016" in era.name:
        from shape_producer.estimation_methods_2016 import DataEstimation
    else:
        logger.fatal("Can not import data estimation because era {} is not implemented.".format(era.name))
        raise Exception
    estimation = DataEstimation(era, directory, channel)

    # Extract weight string, which should be equal (1.0)
    weight_string = estimation.get_weights().extract()
    logger.debug("Data weight string: %s", weight_string)
    if weight_string != "(1.0)":
        logger.fatal("Weight string is not equal to (1.0).")
        raise Exception

    # Extract cut string
    cut_string = (
        estimation.get_cuts() + channel.cuts + additional_cuts).expand()
    logger.debug("Data cut string: %s", cut_string)
    dict_["cut_string"] = str(cut_string)

    # Get files
    files = [str(f) for f in estimation.get_files()]
    for i, f in enumerate(files):
        logger.debug("File %d: %s", i + 1, str(f).replace(directory + "/", ""))
    dict_["files"] = files

    return dict_


def build_chain(dict_):
    # Build chain
    logger.debug("Use tree path %s for chain.", dict_["tree_path"])
    chain = ROOT.TChain(dict_["tree_path"])
    for f in dict_["files"]:
        chain.AddFile(f)
    chain_numentries = chain.GetEntries()
    if not chain_numentries > 0:
        logger.fatal("Chain (before skimming) does not contain any events.")
        raise Exception
    logger.debug("Found %s events before skimming with cut string.",
                 chain_numentries)

    # Skim chain
    chain_skimmed = chain.CopyTree(dict_["cut_string"])
    chain_skimmed_numentries = chain_skimmed.GetEntries()
    if not chain_skimmed_numentries > 0:
        logger.fatal("Chain (after skimming) does not contain any events.")
        raise Exception
    logger.debug("Found %s events after skimming with cut string.",
                 chain_skimmed_numentries)

    return chain_skimmed


def get_1d_binning(channel, chain, variables, percentile_min, percentile_max,
                   num_bins):
    # Collect values
    values = [[] for v in variables]
    for event in chain:
        for i, v in enumerate(variables):
            value = getattr(event, v)
            if value not in [-11.0, -999.0, -10.0, -1.0]:
                values[i].append(value)

    # Get min and max by percentiles
    binning = {}
    for i, v in enumerate(variables):
        binning[v] = {}
        min_max = np.percentile(values[i], [percentile_min, percentile_max])
        binning[v]["bins"] = [
            float(x) for x in np.linspace(min_max[0], min_max[1], num_bins)
        ]
        binning[v]["expression"] = v
        binning[v]["cut"] = "({VAR}>{MIN})&&({VAR}<{MAX})".format(
            VAR=v, MIN=min_max[0], MAX=min_max[1])
        logger.debug("Binning for variable %s: %s", v, binning[v]["bins"])

    return binning


def add_2d_unrolled_binning(variables, binning):
    for i1, v1 in enumerate(variables):
        for i2, v2 in enumerate(variables):
            if i2 <= i1:
                continue

            bins1 = binning[v1]["bins"]
            bins2 = binning[v2]["bins"]
            range_ = max(bins1) - min(bins1)
            bins = np.linspace(
                min(bins1),
                min(bins1) + range_ * (len(bins2) - 1),
                (len(bins1) - 1) * (len(bins2) - 1) + 1)

            expression = ""
            for b in range(len(bins2) - 1):
                expression += "({OFFSET}+{VAR1})*({VAR2}>{MIN})*({VAR2}<={MAX})".format(
                    VAR1=v1,
                    VAR2=v2,
                    MIN=bins2[b],
                    MAX=bins2[b + 1],
                    OFFSET=b * range_)
                if b != len(bins2) - 2:
                    expression += "+"

            name = "{}_{}".format(v1, v2)
            binning[name] = {}
            binning[name]["bins"] = [float(x) for x in bins]
            binning[name]["expression"] = expression
            binning[name]["cut"] = "({VAR}>{MIN})&&({VAR}<{MAX})".format(
                VAR=v1, MIN=bins1[0], MAX=bins1[-1])

    return binning


def main(args):
    # Define era
    if "2016" in args.era:
        from shape_producer.era import Run2016
        era = Run2016(args.datasets)
    else:
        logger.fatal("Era {} is not implemented.".format(args.era))
        raise Exception

    # Load variables
    variables = yaml.load(open(args.variables))["variables"]

    # Define bins and range of binning for variables in enabled channels
    channels = ["et", "mt", "tt"]
    num_borders = 9
    min_percentile = 1.0
    max_percentile = 99.0

    config = {"gof": {}}

    # Channel: ET
    if "et" in channels:
        # Get properties
        channel = ETSM()
        logger.info("Channel: et")
        dict_ = {}
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for et: %s",
                       additional_cuts.expand())
        dict_ = get_properties(dict_, era, channel, args.directory,
                               additional_cuts)

        # Build chain
        dict_["tree_path"] = "et_nominal/ntuple"
        chain = build_chain(dict_)

        # Get percentiles and calculate 1d binning
        binning = get_1d_binning("et", chain, variables, min_percentile,
                                 max_percentile, num_borders)

        # Add binning for unrolled 2d distributions
        binning = add_2d_unrolled_binning(variables, binning)

        # Append binning to config
        config["gof"]["et"] = binning

    # Channel: MT
    if "mt" in channels:
        # Get properties
        channel = MTSM()
        logger.info("Channel: mt")
        dict_ = {}
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for mt: %s",
                       additional_cuts.expand())
        dict_ = get_properties(dict_, era, channel, args.directory,
                               additional_cuts)

        # Build chain
        dict_["tree_path"] = "mt_nominal/ntuple"
        chain = build_chain(dict_)

        # Get percentiles
        binning = get_1d_binning("mt", chain, variables, min_percentile,
                                 max_percentile, num_borders)

        # Add binning for unrolled 2d distributions
        binning = add_2d_unrolled_binning(variables, binning)

        # Append binning to config
        config["gof"]["mt"] = binning

    # Channel: TT
    if "tt" in channels:
        # Get properties
        channel = TTSM()
        logger.info("Channel: tt")
        dict_ = {}
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for tt: %s",
                       additional_cuts.expand())
        dict_ = get_properties(dict_, era, channel, args.directory,
                               additional_cuts)

        # Build chain
        dict_["tree_path"] = "tt_nominal/ntuple"
        chain = build_chain(dict_)

        # Get percentiles
        binning = get_1d_binning("tt", chain, variables, min_percentile,
                                 max_percentile, num_borders)

        # Add binning for unrolled 2d distributions
        binning = add_2d_unrolled_binning(variables, binning)

        # Append binning to config
        config["gof"]["tt"] = binning

    # Write config
    logger.info("Write binning config to %s.", args.output)
    yaml.dump(config, open(args.output, 'w'))


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("calculate_binning.log", logging.DEBUG)
    main(args)
