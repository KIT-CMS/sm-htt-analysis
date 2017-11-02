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
    signals = ["HTT"]
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
                            ["Htt", "ZTT"])
    db.add_shape_systematic("CMS_scale_t_1prong0pi0", 1.0, channels,
                            ["Htt", "ZTT"])
    db.add_shape_systematic("CMS_scale_t_1prong1pi0", 1.0, channels,
                            ["Htt", "ZTT"])
    db.add_shape_systematic("CMS_htt_dyShape", 1.0, channels, ["ZTT", "ZL"])

    # Add normalization systematics
    db.add_normalization_systematic("lumi_13TeV", 1.026, channels,
                                    signals + backgrounds)
    db.add_normalization_systematic("CMS_eff_m", 1.02, ["et", "mt"],
                                    signals + backgrounds)
    db.add_normalization_systematic("CMS_eff_trigger_mt", 1.02, "mt",
                                    signals + backgrounds)
    db.add_normalization_systematic("CMS_eff_trigger_et", 1.02, "et",
                                    signals + backgrounds)
    db.add_normalization_systematic("CMS_Extrap_SSOS_mt", 1.20, "mt", "QCD")
    db.add_normalization_systematic("CMS_Extrap_SSOS_et", 1.20, "et", "QCD")
    db.add_normalization_systematic("CMS_htt_wjXsec", 1.04, channels, "W")
    db.add_normalization_systematic("CMS_htt_vvXsec", 1.06, channels, "VV")
    # TODO: tt and z normalizations

    # Extract shapes
    if "et" in args.channels:
        db.extract_shapes("et", "smhtt", "Run2016", "et_keras1_max_score")
    if "mt" in args.channels:
        db.extract_shapes("mt", "smhtt", "Run2016", "mt_keras13_max_score")

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
