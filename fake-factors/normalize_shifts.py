#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
import argparse
import logging
import copy
logger = logging.getLogger()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Calculate fake factors and create friend trees.")
    parser.add_argument("input", type=str, help="Shape-producer output file.")
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


def interpolateHistos(h1_old, h2_old):

        h1,h2 = copy.deepcopy(h1_old),copy.deepcopy(h2_old)

        nbins=h1_old.GetNbinsX()
        for ibin in xrange(nbins+2):     #includes under- and overflow
            cont1,cont2=h1_old.GetBinContent(ibin),h2_old.GetBinContent(ibin)
            h1.SetBinContent( ibin, cont2* float(nbins-ibin)/nbins + cont1* float(ibin)/nbins )
            h2.SetBinContent( ibin, cont1* float(nbins-ibin)/nbins + cont2* float(ibin)/nbins )

        return h1,h2


def main(args):
    file_ = ROOT.TFile(args.input, "UPDATE")
    for key in file_.GetListOfKeys():
        # Parse name
        name = key.GetName()

        if name[-1] == "#":  # shape is nominal shape
            continue

        split = [x for x in name.split("#") if not x == ""]
        channel = split[0]
        category = split[1]
        process = split[2]

        if not process == "jetFakes":  # ff uncertainties apply only on jetFakes process
            continue

        shift = split[7]
        if shift[-4:] == "Down":
            shift_type = "down"
            continue #run down together with up
        elif shift[-2:] == "Up":
            shift_type = "up"
        else:
            logger.critical("Cannot determine shift type of systematic %s.",
                            name)
            raise Exception

        # Renormalize if systematic has sub-string _ff_
        if "_ff_" in name:
            h_shift_raw = file_.Get(name)
            h_shift_down_raw = file_.Get(name.replace("Up", "Down"))
            if h_shift_raw == None or h_shift_down_raw == None:
                logger.critical("Failed to get shape syst. histogram %s.",
                                name)
                raise Exception

            h_shift, h_shift_down = interpolateHistos(h_shift_raw, h_shift_down_raw)

            nominal = "#" + "#".join(split[:-1]) + "#"
            h_nominal = file_.Get(nominal)
            if h_nominal == None:
                logger.critical("Failed to get nominal histogram %s.", nominal)
                raise Exception

            norm_shift = h_shift.Integral()
            norm_shift_down = h_shift_down.Integral()
            norm_nominal = h_nominal.Integral()
            if norm_shift == 0 or norm_shift_down == 0:
                logger.warning("Found shift with integral of zero for systematic %s. Continue.",
                        name)
                continue
            scale = norm_nominal / norm_shift
            scale_down = norm_nominal / norm_shift_down
            logger.debug(
                "Renormalize systematic %s (%f) with integral of %s (%f): %f",
                name, norm_shift, nominal, norm_nominal, scale)
            h_shift.Scale(scale)
            h_shift.Write()
            logger.debug(
                "Renormalize systematic %s (%f) with integral of %s (%f): %f",
                name.replace("Up", "Down"), norm_shift, nominal, norm_nominal, scale)
            h_shift_down.Scale(scale_down)
            h_shift_down.Write()
    logger.info("Successfully normalized fake factor systematics to nominal.")
    file_.Close()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("normalize_shifts.log", logging.INFO)
    main(args)
