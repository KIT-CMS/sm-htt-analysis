#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import yaml
import os
import subprocess
from array import array

import logging
logger = logging.getLogger("create_training_dataset")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    logger.debug("Parse arguments.")
    parser = argparse.ArgumentParser(description="Create training dataset")
    parser.add_argument("config", help="Datasets config file")
    return parser.parse_args()


def parse_config(filename):
    logger.debug("Load YAML config: {}".format(filename))
    return yaml.load(open(filename, "r"))


def main(args, config):
        created_files = []
        for process in config["processes"]:
            logger.debug("Collect events of process {}.".format(
                process))

            # Create output file
            created_files.append(
                os.path.join(config["output_path"],
                             "output_{}.root".format(process)))
            file_ = ROOT.TFile(created_files[-1], "RECREATE")

            # Collect all files for this process in a chain. Create also chains for friend files
            chain = ROOT.TChain(config["tree_path"])
            friendchains = {}
            for d in config["friend_paths"]:
                friendchains[d] = ROOT.TChain(config["tree_path"])

            for filename in config["processes"][process]["files"]:
                path = os.path.join(config["base_path"], filename)
                if not os.path.exists(path):
                    logger.fatal("File does not exist: {}".format(path))
                chain.AddFile(path)
                # Make sure, that friend files are put in the same order together
                for d in friendchains:
                    friendfile = os.path.join(d,filename)
                    friendchains[d].AddFile(friendfile)

            chain_numentries = chain.GetEntries()
            if not chain_numentries > 0:
                logger.fatal(
                    "Chain (before skimming) does not contain any events.")
                raise Exception
            logger.debug("Found {} events for process {}.".format(
                chain_numentries, process))

            # Skim the events with the cut string
            cut_string = config["processes"][process]["cut_string"]
            logger.debug("Skim events with cut string: {}".format(cut_string))

            chain_skimmed = chain.CopyTree(cut_string)
            chain_skimmed_numentries = chain_skimmed.GetEntries()
            friendchains_skimmed = {}
            # Apply skim selection also to friend chains
            for d in friendchains:
                friendchains[d].AddFriend(chain)
                friendchains_skimmed[d] = friendchains[d].CopyTree(cut_string)
            if not chain_skimmed_numentries > 0:
                logger.fatal(
                    "Chain (after skimming) does not contain any events.")
                raise Exception
            logger.debug("Found {} events for process {} after skimming.".
                         format(chain_skimmed_numentries, process))

            # Write training weight to new branch
            logger.debug("Add training weights with weight string: {}".format(
                config["processes"][process]["weight_string"]))
            formula = ROOT.TTreeFormula(
                "training_weight",
                config["processes"][process]["weight_string"], chain_skimmed)
            training_weight = array('f', [-999.0])
            branch_training_weight = chain_skimmed.Branch(
                config["training_weight_branch"], training_weight,
                config["training_weight_branch"] + "/F")
            for i_event in range(chain_skimmed.GetEntries()):
                chain_skimmed.GetEntry(i_event)
                training_weight[0] = formula.EvalInstance()
                branch_training_weight.Fill()

            # Rename chain to process name and write to output file
            logger.debug("Write output file for this process.")
            chain_skimmed.SetName(process)
            chain_skimmed.Write("",ROOT.TObject.kOverwrite)
            for index, d in enumerate(friendchains_skimmed):
                friendchains_skimmed[d].SetName("_".join([process, "friend", str(index)]))
                friendchains_skimmed[d].Write("",ROOT.TObject.kOverwrite)
            file_.Delete("ntuple;*")
            file_.Close()

        # Combine all skimmed files using `hadd`
        logger.debug("Call `hadd` to combine files of processes.")
        output_file = os.path.join(config["output_path"], config["output_filename"])
        subprocess.call(["hadd", "-f", output_file] + created_files)
        logger.info("Created output file: {}".format(output_file))


if __name__ == "__main__":
    args = parse_arguments()
    config = parse_config(args.config)
    main(args, config)
