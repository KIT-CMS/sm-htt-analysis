#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
import argparse
import logging
logger = logging.getLogger()

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Calculate fake factors and create friend trees.")
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="Shape-producer output file.")
    return parser.parse_args()

def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def main(args):
    file0 = ROOT.TFile(args.input, "UPDATE")
    content = ROOT.gDirectory.GetListOfKeys()
    histnames = []
    nominal_name = ""
    for entry in content:
        name = entry.GetTitle() #entry.split('"')[1]
        if "jetFakes" in name:
            if "_ff_" in name:
                histnames.append(name)
            else:
                nominal_name = name
    norm = file0.Get(nominal_name).Integral(-1, -1)
    logger.debug("Found nominal histogram %s with norm %f"%(nominal_name, norm))
    for syst in histnames:
        syst_hist = file0.Get(syst)
        norm_syst = syst_hist.Integral(-1, -1)
        logger.debug("Found systematic shift histogram %s with norm %f. Renormalize..."%(syst, norm_syst))
        syst_hist.Scale(norm/norm_syst)
        syst_hist.Write()
    logger.info("Successfully normalized fake factor systematics to nominal")
    file0.Close()
        

if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("normalize_shifts.log",
                  logging.INFO)
    main(args)