#!/usr/bin/env python
# -*- coding: utf-8 -*-

import CombineHarvester.CombineTools.ch as ch
from datacard_producer.datacard_builder import DatacardBuilder

import argparse

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
        description="Produce datacards for 2016 Standard Model analysis.")

    parser.add_argument(
        "--shapes",
        default="shapes.root",
        type=str,
        help="Nominal shapes and systematic variations.")

    return parser.parse_args()


def main(args):
    db = DatacardBuilder(args.shapes)

    # Register observations, signals and backgrounds
    categories = ["mt_inclusive"]
    category_pairs = db.make_pairs(categories)

    db.add_observation("125", "smhtt", "Run2016", "mt", category_pairs)

    signals = ["Htt"]
    db.add_signals("125", "smhtt", "Run2016", "mt", signals, category_pairs)

    backgrounds = ["Ztt", "Zll", "WJets", "VV", "tt", "QCD"]
    db.add_backgrounds("125", "smhtt", "Run2016", "mt", backgrounds,
                       category_pairs)

    # Add shapes systematics
    db.add_shape_systematic("tauEsThreeProng", 1.0, ["Htt", "Ztt"])
    db.add_shape_systematic("tauEsOneProng", 1.0, ["Htt", "Ztt"])
    db.add_shape_systematic("tauEsOneProngPiZeros", 1.0, ["Htt", "Ztt"])
    db.add_shape_systematic("zPtReweightWeight", 1.0, ["Ztt", "Zll"])

    # Add normalization systematics
    db.add_normalization_systematic("lumi", signals + backgrounds, 1.025)
    db.add_normalization_systematic("trigger_efficiency",
                                    signals + backgrounds, 1.02)
    db.add_normalization_systematic("muon_efficiency", signals + backgrounds,
                                    1.02)
    db.add_normalization_systematic("tau_efficiency", signals + backgrounds,
                                    1.02)
    db.add_normalization_systematic("norm_Ztt", "Ztt", 1.04)
    db.add_normalization_systematic("norm_Zll", "Zll", 1.04)
    db.add_normalization_systematic("norm_tt", "tt", 1.06)
    db.add_normalization_systematic("norm_VV", "VV", 1.05)
    db.add_normalization_systematic("norm_WJets", "WJets", 1.04)
    db.add_normalization_systematic("QCD_extrapolation", "QCD", 1.06)

    # Extract shapes
    db.extract_shapes("mt", "smhtt", "Run2016", "pt_1")

    # Replace observation with Asimov dataset
    db.replace_observation_by_asimov_dataset()

    # Add bin-by-bin systematics
    db.add_bin_by_bin_systematics(
        signals + backgrounds,
        add_threshold=0.1,
        merge_threshold=0.5,
        fix_norm=True)

    # Perform auto-rebinning
    db.auto_rebin(threshold=1.0, mode=0)

    # Write datacard
    db.print_datacard()
    db.write("datacard")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_datacard.log", logging.DEBUG)
    main(args)
