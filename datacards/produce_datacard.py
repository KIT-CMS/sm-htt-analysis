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
    parser.add_argument(
        "--channels",
        nargs="+",
        required=True,
        help="Select channels to be included in the datacard.")

    return parser.parse_args()


def main(args):
    db = DatacardBuilder(args.shapes)

    # Register observations, signals and backgrounds
    channels = []
    signals = ["ggH", "qqH"]
    backgrounds = ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "QCD"]

    if "et" in args.channels:
        et_categories = [
            "et_HTT", "et_ZTT", "et_ZLL", "et_W", "et_TT", "et_QCD"
        ]
        et_category_pairs = db.make_pairs(et_categories)

        db.add_observation("125", "smhtt", "Run2016", "et", et_category_pairs)
        db.add_signals("125", "smhtt", "Run2016", "et", signals,
                       et_category_pairs)
        db.add_backgrounds("125", "smhtt", "Run2016", "et", backgrounds,
                           et_category_pairs)

        channels.append("et")

    if "mt" in args.channels:
        mt_categories = [
            "mt_HTT", "mt_ZTT", "mt_ZLL", "mt_W", "mt_TT", "mt_QCD"
        ]
        mt_category_pairs = db.make_pairs(mt_categories)

        db.add_observation("125", "smhtt", "Run2016", "mt", mt_category_pairs)
        db.add_signals("125", "smhtt", "Run2016", "mt", signals,
                       mt_category_pairs)
        db.add_backgrounds("125", "smhtt", "Run2016", "mt", backgrounds,
                           mt_category_pairs)

        channels.append("mt")

    # Add shapes systematics
    db.add_shape_systematic("CMS_scale_t_3prong0pi0", 1.0, channels,
                            ["ggH", "qqH", "ZTT", "TTT", "VV"])
    db.add_shape_systematic("CMS_scale_t_1prong0pi0", 1.0, channels,
                            ["ggH", "qqH", "ZTT", "TTT", "VV"])
    db.add_shape_systematic("CMS_scale_t_1prong1pi0", 1.0, channels,
                            ["ggH", "qqH", "ZTT", "TTT", "VV"])
    db.add_shape_systematic("CMS_htt_dyShape", 1.0, channels,
                            ["ZTT", "ZL", "ZJ"])
    db.add_shape_systematic("CMS_htt_ttbarShape", 1.0, channels,
                            ["TTT", "TTJ"])
    #db.add_shape_systematic("CMS_scale_j", 1.0, channels, ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV"])
    db.add_shape_systematic(
        "CMS_htt_scale_met", 1.0, channels,
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV"])
    db.add_shape_systematic("CMS_htt_jetToTauFake", 1.0, channels,
                            ["ZJ", "W", "TTJ"])

    # Add normalization systematics
    db.add_normalization_systematic(
        "lumi_13TeV", 1.026, channels,
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV"])
    db.add_normalization_systematic(
        "CMS_eff_m", 1.02, "mt",
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV"])
    db.add_normalization_systematic(
        "CMS_eff_e", 1.02, "et",
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV"])
    db.add_normalization_systematic(
        "CMS_eff_trigger_mt", 1.02, "mt",
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV"])
    db.add_normalization_systematic(
        "CMS_eff_trigger_et", 1.02, "et",
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV"])
    db.add_normalization_systematic("CMS_Extrap_SSOS_mt", 1.20, "mt", "QCD")
    db.add_normalization_systematic("CMS_Extrap_SSOS_et", 1.20, "et", "QCD")
    db.add_normalization_systematic("CMS_htt_wjXsec", 1.04, channels, "W")
    db.add_normalization_systematic("CMS_htt_vvXsec", 1.05, channels, "VV")
    db.add_normalization_systematic("CMS_htt_zjXsec", 1.04, channels,
                                    ["ZTT", "ZL", "ZJ"])
    db.add_normalization_systematic("CMS_htt_ttXsec", 1.06, channels,
                                    ["TTT", "TTJ"])
    #db.add_normalization_systematic("CMS_htt_jetFakeTau", 1.2, channels, ["ZJ","TTJ"])
    db.add_normalization_systematic("CMS_htt_mFakeTau", 1.25, "mt", "ZL")
    db.add_normalization_systematic("CMS_htt_eFakeTau", 1.12, "et", "ZL")
    db.add_normalization_systematic("CMS_scale_ggH", 1.039, channels, "ggH")
    db.add_normalization_systematic("pdf_Higgs_ggH", 1.032, channels, "ggH")
    db.add_normalization_systematic("CMS_scale_qqH", 1.004, channels, "qqH")
    db.add_normalization_systematic("pdf_Higgs_qqH", 1.021, channels, "qqH")

    # Extract shapes
    if "et" in args.channels:
        db.extract_shapes("et", "smhtt", "Run2016", "et_keras21_max_score")
    if "mt" in args.channels:
        db.extract_shapes("mt", "smhtt", "Run2016", "mt_keras21_max_score")

    # Replace observation with Asimov dataset
    db.replace_observation_by_asimov_dataset()

    # Add bin-by-bin systematics
    db.add_bin_by_bin_systematics(
        signals + backgrounds,
        add_threshold=0.1,
        merge_threshold=0.5,
        fix_norm=True)

    # Perform auto-rebinning
    #db.auto_rebin(threshold=1.0, mode=0)

    # Write datacard
    #db.print_datacard()
    db.write("datacard.txt", "datacard_shapes.root")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_datacard.log", logging.DEBUG)
    main(args)
