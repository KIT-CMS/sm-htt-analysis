#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import os

import logging
logger = logging.getLogger("")


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
        description="Convert shapes from the shape producer to the sync format."
    )
    parser.add_argument("--era", required=True, type=str, help="Analysis era")
    parser.add_argument("--input", required=True, type=str, help="Path to single input ROOT file.")
    parser.add_argument("--output", required=True, type=str, help="Path to output directory")
    parser.add_argument("--train-method", required=False, type=str, help="Name to add to the output filename")
    return parser.parse_args()


def main(args):
    # Open input ROOT file and output ROOT file
    file_input = ROOT.TFile(args.input)

    # Loop over shapes of input ROOT file and create map of input/output names
    hist_map = {}
    for key in file_input.GetListOfKeys():
        if key.GetName() == "output_tree":
            continue
        # Read name and extract shape properties
        name = key.GetName()
        properties = [x for x in name.split("#") if not x == ""]

        # Get category name (and remove CHANNEL_ from category name)
        category = properties[1].replace(properties[0] + "_", "", 1)

        # Get other properties
        channel = properties[0]
        process = properties[2]

        # Check that in the mapping of the names the channel and category is existent
        if not channel in hist_map:
            hist_map[channel] = {}
        if not category in hist_map[channel]:
            hist_map[channel][category] = {}

        # Push name of histogram to dict
        if not len(properties) in [7, 8]:
            logger.critical(
                "Shape {} has an unexpected number of properties.".format(
                    name))
            raise Exception
        name_output = "{PROCESS}".format(PROCESS=process)
        if len(properties) == 8:
            systematic = properties[7]
            name_output += "_" + systematic
        hist_map[channel][category][name] = name_output

    # Loop over map once and create respective output files
    for channel in hist_map:
        if args.train_method in [None, ""]:
            filename_output = os.path.join(
                args.output,
                "{ERA}-{CHANNELS}-synced-ML.root").format(CHANNELS=channel, ERA=args.era)
        else:
            filename_output = os.path.join(
                args.output,
                "{ERA}-{METHOD}-{CHANNELS}-synced-ML.root").format(CHANNELS=channel,METHOD=args.train_method, ERA=args.era)
        if not os.path.exists(args.output):
            os.mkdir(args.output)
        file_output = ROOT.TFile(filename_output, "RECREATE")
        for category in sorted(hist_map[channel]):
            if category.endswith("_ss") or category.endswith("_B") or category.endswith("_FF"):
                continue
            file_output.cd()
            dir_name = "{CHANNEL}_{CATEGORY}".format(
                CHANNEL=channel, CATEGORY=category)
            file_output.mkdir(dir_name)
            file_output.cd(dir_name)
            for name in sorted(hist_map[channel][category]):
                hist = file_input.Get(name)
                if (not "ZTTpTTTauTau" in name) and ("CMS_htt_emb_ttbar" in name):
                    continue
                name_output = hist_map[channel][category][name]
                if "ZTTpTTTauTauUp" in name_output:
                    name_output = name_output.replace("ZTTpTTTauTauUp","EMB")
                if "ZTTpTTTauTauDown" in name_output:
                    name_output = name_output.replace("ZTTpTTTauTauDown","EMB")               
                hist.SetTitle(name_output)
                hist.SetName(name_output)
                hist.Write()
                if "Run201" in name_output:
                    if ("scale_t_" in name_output
                            or "prefiring" in name_output
                            or "scale_mc_e_" in name_output
                            or "reso_mc_e_" in name_output
                            or "scale_mc_t_" in name_output
                            or "scale_emb_t_" in name_output
                            or "scale_j_" in name_output
                            or "_1ProngPi0Eff_" in name_output
                            or "_3ProngEff_" in name_output
                            or ("_ff_" in name_output and "_syst_" in name_output)):
                        hist.SetTitle(name_output.replace("_Run2016", "").replace("_Run2017", "").replace("_Run2018", ""))
                        hist.SetName(name_output.replace("_Run2016", "").replace("_Run2017", "").replace("_Run2018", ""))
                        hist.Write()
        file_output.Close()

    # Clean-up
    file_input.Close()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("convert_synced_shapes.log", logging.DEBUG)
    main(args)
