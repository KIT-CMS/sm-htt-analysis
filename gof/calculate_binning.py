#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

from shape_producer.cutstring import Cut, Cuts
from shape_producer.channel import EMSM2016, ETSM2016, MTSM2016, TTSM2016, EMSM2017, ETSM2017, MTSM2017, TTSM2017, EMSM2018, ETSM2018, MTSM2018, TTSM2018
from shape_producer.process import Process

import argparse
import numpy as np
import yaml
import os

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

    parser.add_argument("--directory",
                        required=True,
                        type=str,
                        help="Directory with Artus outputs.")
    parser.add_argument("--em-friend-directories",
                        nargs='+',
                        default=[],
                        type=str,
                        help="Directories with Artus friend outputs for em channel.")
    parser.add_argument("--et-friend-directories",
                        nargs='+',
                        default=[],
                        type=str,
                        help="Directories with Artus friend outputs for et channel.")
    parser.add_argument("--mt-friend-directories",
                        nargs='+',
                        default=[],
                        type=str,
                        help="Directories with Artus friend outputs for mt channel.")
    parser.add_argument("--tt-friend-directories",
                        nargs='+',
                        default=[],
                        type=str,
                        help="Directories with Artus friend outputs for tt channel.")
    parser.add_argument("--era",
                        required=True,
                        type=str,
                        help="Experiment era.")
    parser.add_argument("--datasets",
                        required=True,
                        type=str,
                        help="Kappa datsets database.")
    parser.add_argument("--output",
                        required=True,
                        type=str,
                        help="Output path for binning config.")
    parser.add_argument("--variables",
                        required=True,
                        help="Variables to be considered.")
    parser.add_argument("--channel",
                        required=True,
                        help="Channel to be considered.")
    return parser.parse_args()


def get_properties(dict_, era, channel, directory, additional_cuts):
    # Get data estimation method
    if "2016" in era.name:
        from shape_producer.estimation_methods_2016 import DataEstimation
    elif "2017" in era.name:
        from shape_producer.estimation_methods_2017 import DataEstimation
    elif "2018" in era.name:
        from shape_producer.estimation_methods_2018 import DataEstimation
    else:
        logger.fatal(
            "Can not import data estimation because era {} is not implemented."
            .format(era.name))
        raise Exception
    estimation = DataEstimation(era, directory, channel)

    # Extract weight string, which should be equal (1.0)
    weight_string = estimation.get_weights().extract()
    logger.debug("Data weight string: %s", weight_string)
    if weight_string != "(1.0)":
        logger.fatal("Weight string is not equal to (1.0).")
        raise Exception

    # Extract cut string
    cut_string = (estimation.get_cuts() + channel.cuts
                  + additional_cuts).expand()
    logger.debug("Data cut string: %s", cut_string)
    dict_["cut_string"] = str(cut_string)

    # Get files
    files = [str(f) for f in estimation.get_files()]
    for i, f in enumerate(files):
        logger.debug("File %d: %s", i + 1, str(f).replace(directory + "/", ""))
    dict_["files"] = files
    dict_["directory"] = directory

    return dict_


def build_chain(dict_, friend_directories):
    # Build chain
    logger.debug("Use tree path %s for chain.", dict_["tree_path"])
    chain = ROOT.TChain(dict_["tree_path"])
    friendchains = {}
    for d in friend_directories:
        friendchains[d] = ROOT.TChain(dict_["tree_path"])
    for f in dict_["files"]:
        chain.AddFile(f)
        # Make sure, that friend files are put in the same order together
        for d in friendchains:
            friendfile = os.path.join(d,f.replace(dict_["directory"], ""))
            friendchains[d].AddFile(friendfile)
    chain_numentries = chain.GetEntries()
    if not chain_numentries > 0:
        logger.fatal("Chain (before skimming) does not contain any events.")
        raise Exception
    logger.debug("Found %s events before skimming with cut string.",
                 chain_numentries)

    # Skim chain
    chain_skimmed = chain.CopyTree(dict_["cut_string"])
    chain_skimmed_numentries = chain_skimmed.GetEntries()
    friendchains_skimmed = {}
    # Apply skim selection also to friend chains
    for d in friendchains:
        friendchains[d].AddFriend(chain)
        friendchains_skimmed[d] = friendchains[d].CopyTree(dict_["cut_string"])
    if not chain_skimmed_numentries > 0:
        logger.fatal("Chain (after skimming) does not contain any events.")
        raise Exception
    logger.debug("Found %s events after skimming with cut string.",
                 chain_skimmed_numentries)
    for d in friendchains_skimmed:
        chain_skimmed.AddFriend(friendchains_skimmed[d], "fr_{}".format(os.path.basename(d.rstrip("/"))))

    return chain_skimmed


def get_1d_binning(channel, chain, variables, percentiles):
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
        if len(values[i]) > 0:
            borders = [float(x) for x in np.percentile(values[i], percentiles)]
            # remove duplicates in bins for integer binning
            borders = sorted(list(set(borders)))
            # epsilon offset for integer variables to make it more stable
            borders = [b - 0.0001 for b in borders ]
            # stretch last one to include the last border in case it is an integer
            borders[-1] += 0.0002
        else:
            logger.fatal(
                "No valid values found for variable {}. Please remove from list for channel {}."
                .format(v, channel))
            raise Exception

        binning[v]["bins"] = borders
        binning[v]["expression"] = v
        if len(borders) >= 2:
            binning[v]["cut"] = "({VAR}>{MIN})&&({VAR}<{MAX})".format(
                VAR=v, MIN=borders[0], MAX=borders[-1])
        else:
            binning[v]["cut"] = "(1 == 0)"
        logger.debug("Binning for variable %s: %s", v, binning[v]["bins"])

    return binning


def add_2d_unrolled_binning(variables, binning):
    for i1, v1 in enumerate(variables):
        for i2, v2 in enumerate(variables):
            if i2 <= i1:
                continue

            if len(binning[v1]["bins"]) < 11:
                bins1 = binning[v1]["bins"]
            else:
                bins1 = binning[v1]["bins"][::2]
            if len(binning[v2]["bins"]) < 11:
                bins2 = binning[v2]["bins"]
            else:
                bins2 = binning[v2]["bins"][::2]
            range_ = max(bins1) - min(bins1)

            bins = [bins1[0]]
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
                for c in range(len(bins1)-1):
                    bins.append(b * range_ + bins1[c+1])
            # Add separate term shifting undefined values away from zero.
            # If this is not done the bin including zero is populated with all events
            # with default values.
            # This problem only occurs for variables taking integer values.
            jet_variables = ["mjj", "jdeta", "dijetpt", "ME_q2v1", "ME_q2v2"]
            default_val = -10.
            if v1 in ["njets", "nbtag"]:
                if v2 in jet_variables:
                    expression += "({DEF})*(({VAR2}<{MIN})+({VAR2}>{MAX}))".format(
                            DEF=default_val,
                            VAR2=v2,
                            MIN=bins2[0],
                            MAX=bins2[-1])

            name = "{}_{}".format(v1, v2)
            binning[name] = {}
            binning[name]["bins"] = bins
            binning[name]["expression"] = expression
            binning[name]["cut"] = "({VAR}>{MIN})&&({VAR}<{MAX})".format(
                VAR=v1, MIN=bins1[0], MAX=bins1[-1])

    return binning


def main(args):
    # Define era
    if "2016" in args.era:
        from shape_producer.era import Run2016
        era = Run2016(args.datasets)
    elif "2017" in args.era:
        from shape_producer.era import Run2017
        era = Run2017(args.datasets)
    elif "2018" in args.era:
        from shape_producer.era import Run2018
        era = Run2018(args.datasets)
    else:
        logger.fatal("Era {} is not implemented.".format(args.era))
        raise Exception

    # Load variables
    variables = yaml.load(open(args.variables))["selected_variables"]

    # Define bins and range of binning for variables in enabled channels
    channel_dict = {
        "et" : { "2016": ETSM2016(), "2017" : ETSM2017(), "2018" : ETSM2018()},
        "mt" : { "2016": MTSM2016(), "2017" : MTSM2017(), "2018" : MTSM2018()},
        "tt" : { "2016": TTSM2016(), "2017" : TTSM2017(), "2018" : TTSM2018()},
        "em" : { "2016": EMSM2016(), "2017" : EMSM2017(), "2018" : EMSM2018()},
    }
    friend_directories_dict = {
        "em": args.em_friend_directories,
        "et": args.et_friend_directories,
        "mt": args.mt_friend_directories,
        "tt": args.tt_friend_directories,
    }
    percentiles = [
            0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0
    ]

    config = {"gof": {}}

    for ch in channel_dict.keys():
        if ch != args.channel:
            continue
        # Get properties
        if "2016" in args.era:
            eraname = "2016"
        elif "2017" in args.era:
            eraname = "2017"
        elif "2018" in args.era:
            eraname = "2018"
        channel = channel_dict[ch][eraname]
        logger.info("Channel: %s" % ch)
        dict_ = {}
        additional_cuts = Cuts()
        logger.warning("Use additional cuts for %s: %s" %
                       (ch,additional_cuts.expand()))
        dict_ = get_properties(dict_, era, channel, args.directory,
                               additional_cuts)

        # Build chain
        dict_["tree_path"] = "%s_nominal/ntuple" % ch

        chain = build_chain(dict_, friend_directories_dict[ch])

        # Get percentiles and calculate 1d binning
        binning = get_1d_binning(ch, chain, variables[int(eraname)][ch], percentiles)

        # Add binning for unrolled 2d distributions
        binning = add_2d_unrolled_binning(variables[int(eraname)][ch], binning)

        # Append binning to config
        config["gof"][ch] = binning

    # Write config
    logger.info("Write binning config to %s.", args.output)
    yaml.dump(config, open(args.output, 'w'))


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("calculate_binning.log", logging.DEBUG)
    main(args)
