#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import os
from multiprocessing import Pool
import glob

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

    parser.add_argument("cores", type=int, help="Cores for multiprocessing.")
    parser.add_argument("era", type=str, help="Experiment era.")
    parser.add_argument("variable", type=str, help="Variable for final discriminator.")
    parser.add_argument("input", type=str, help="Path to single input ROOT file.")
    parser.add_argument("output", type=str, help="Path to output directory.")
    return parser.parse_args()

def create_properties(histname):
    properties = [x for x in histname.split("#") if not x == ""]
    if not len(properties) in [7, 8]:
        return None
    channel = properties[0]
    category = properties[1].replace(properties[0] + "_", "", 1)
    process = properties[2]
    outputname = process
    if len(properties) == 8:
        outputname += "_" + properties[7] # adding systematic name to process in case needed
    return {"inputname" : histname, "channel" : channel, "category" : category, "process" : process, "outputname" : outputname}

def merge_to_synced_file(info):
    filename_outputs = os.path.join(info["path"], "htt_{CHANNEL}_*.inputs-nmssm-{ERA}-{VARIABLE}.root").format(
        CHANNEL=info["channel"], ERA=info["era"], VARIABLE=info["variable"])
    merged_output = os.path.join(info["path"], "htt_{CHANNEL}.inputs-nmssm-{ERA}-{VARIABLE}.root").format(
        CHANNEL=info["channel"], ERA=info["era"], VARIABLE=info["variable"])
    outputlist = glob.glob(filename_outputs)
    hadd_cmd = "hadd -f " + merged_output + " " + " ".join(outputlist)
    os.system(hadd_cmd)

def create_synced_category_files(info):
    filename_output = os.path.join(info["path"], "htt_{CHANNEL}_{CATEGORY}.inputs-nmssm-{ERA}-{VARIABLE}.root").format(
        CHANNEL=info["channel"], CATEGORY=info["category"], ERA=info["era"], VARIABLE=info["variable"])
    print "Creating: %s"%filename_output
    if not os.path.exists(info["path"]):
        os.mkdir(info["path"])
    file_input = ROOT.TFile(info["input"], "read")
    file_output = ROOT.TFile(filename_output, "recreate")
    file_output.cd()
    dir_name = "{CHANNEL}_{CATEGORY}".format(
        CHANNEL=info["channel"], CATEGORY=info["category"])
    file_output.mkdir(dir_name)
    file_output.cd(dir_name)
    for name in sorted(info["processes"]):
        hist = file_input.Get(name)
        name_output = info["processes"][name]
        hist.SetTitle(name_output)
        hist.SetName(name_output)
        hist.Write()
        if "201" in name_output:
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
                hist.SetTitle(name_output.replace("_2016", "").replace("_2017", "").replace("_2018",""))
                hist.SetName(name_output.replace("_2016", "").replace("_2017", "").replace("_2018",""))
                hist.Write()
    file_output.Close()
    file_input.Close()

def main(args):
    # create Pool for multiprocessing
    pool = Pool(args.cores)

    # Open input ROOT file and output ROOT file
    file_input = ROOT.TFile(args.input)

    # Loop over shapes of input ROOT file and create map of input/output names
    hist_map = {}
    histnames = sorted([k.GetName() for k in file_input.GetListOfKeys() if k.GetName() != "output_tree" and not
        ((k.GetName().strip("#").split("#")[1] != "em_ss" and k.GetName().strip("#").split("#")[1].endswith("_ss")) or
        k.GetName().strip("#").split("#")[1].endswith("_B") or
        k.GetName().strip("#").split("#")[1].endswith("_FF"))])
    properties_list = sorted(pool.map(create_properties, histnames))
    for p in properties_list:

        # Check that in the mapping of the names the channel and category is existent
        if not p["channel"] in hist_map:
            hist_map[p["channel"]] = {}
        if not p["category"] in hist_map[p["channel"]]:
            hist_map[p["channel"]][p["category"]] = {}
        hist_map[p["channel"]][p["category"]][p["inputname"]] = p["outputname"]

    infolist =  []
    for channel in hist_map:
        for category in hist_map[channel]:
            infolist.append({"processes" : hist_map[channel][category], "channel" : channel, "category": category, "era" : args.era, "variable" : args.variable, "input" : args.input, "path" : args.output})

    file_input.Close()
    pool.map(create_synced_category_files, infolist)

    # Merge files together per channel
    channelsinfo = [{"channel" : ch, "path" : args.output, "era" : args.era, "variable" : args.variable} for ch in hist_map]
    pool.map(merge_to_synced_file, channelsinfo)



if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("convert_synced_shapes.log", logging.DEBUG)
    main(args)
