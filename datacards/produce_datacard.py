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
    parser.add_argument(
        "--gof",
        default=None,
        help=
        "Produce datacard for goodness of fit test of inclusive distributions."
    )
    parser.add_argument(
        "--QCD-extrap-fit",
        default=False,
        action='store_true',
        help="Create datacard for QCD extrapolation factor determination.")
    parser.add_argument(
        "--HIG16043",
        action="store_true",
        default=False,
        help="Create datacard for HIG16043 reference analysis.")
    parser.add_argument(
        "--use-data-for-observation",
        action="store_true",
        help="Use data for the observation and not an Asimov dataset.")
    parser.add_argument(
        "--emb",
        action="store_true",
        default=False,
        help=
        "Create systematics custom to embedded events instead of ZTT simulation."
    )
    return parser.parse_args()


def main(args):
    db = DatacardBuilder(args.shapes)

    # Register observations, signals and backgrounds
    channels = []
    categories = []
    signals = ["ggH", "qqH"]
    backgrounds = ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK", "QCD"]
    if args.QCD_extrap_fit:
        signals = ["QCD"]
        backgrounds = ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"]

    if "et" in args.channels:
        if args.gof != None:
            et_categories = ["et_{}".format(args.gof)]
        elif args.QCD_extrap_fit:
            et_categories = [
                "et_ztt", "et_zll", "et_w", "et_tt", "et_ss", "et_misc"
            ]
        elif args.HIG16043:
            et_categories = ["et_0jet", "et_vbf", "et_boosted"]
        else:
            et_categories = [
                "et_ggh", "et_qqh", "et_ztt", "et_zll", "et_w", "et_tt",
                "et_ss", "et_misc"
            ]
        et_category_pairs = db.make_pairs(et_categories)

        db.add_observation("125", "smhtt", "Run2016", "et", et_category_pairs)
        db.add_signals("125", "smhtt", "Run2016", "et", signals,
                       et_category_pairs)
        db.add_backgrounds("125", "smhtt", "Run2016", "et", backgrounds,
                           et_category_pairs)

        channels.append("et")
        categories += et_categories

    if "mt" in args.channels:
        if args.gof != None:
            mt_categories = ["mt_{}".format(args.gof)]
        elif args.QCD_extrap_fit:
            mt_categories = [
                "mt_ztt", "mt_zll", "mt_w", "mt_tt", "mt_ss", "mt_misc"
            ]
        elif args.HIG16043:
            mt_categories = ["mt_0jet", "mt_vbf", "mt_boosted"]
        else:
            mt_categories = [
                "mt_ggh", "mt_qqh", "mt_ztt", "mt_zll", "mt_w", "mt_tt",
                "mt_ss", "mt_misc"
            ]
        mt_category_pairs = db.make_pairs(mt_categories)

        db.add_observation("125", "smhtt", "Run2016", "mt", mt_category_pairs)
        db.add_signals("125", "smhtt", "Run2016", "mt", signals,
                       mt_category_pairs)
        db.add_backgrounds("125", "smhtt", "Run2016", "mt", backgrounds,
                           mt_category_pairs)

        channels.append("mt")
        categories += mt_categories

    if "tt" in args.channels:
        if args.gof != None:
            tt_categories = ["tt_{}".format(args.gof)]
        elif args.QCD_extrap_fit:
            tt_categories = ["tt_noniso", "tt_misc"]
        elif args.HIG16043:
            tt_categories = ["tt_0jet", "tt_vbf", "tt_boosted"]
        else:
            tt_categories = [
                "tt_ggh", "tt_qqh", "tt_ztt", "tt_noniso", "tt_misc"
            ]
        tt_category_pairs = db.make_pairs(tt_categories)

        db.add_observation("125", "smhtt", "Run2016", "tt", tt_category_pairs)
        db.add_signals("125", "smhtt", "Run2016", "tt", signals,
                       tt_category_pairs)
        db.add_backgrounds("125", "smhtt", "Run2016", "tt", backgrounds,
                           tt_category_pairs)

        channels.append("tt")
        categories += tt_categories

    # Add shapes systematics
    if args.emb:
        db.add_shape_systematic("CMS_htt_dyShape", 1.0, channels, ["ZL", "ZJ"])
        db.add_shape_systematic(
            "CMS_htt_eff_b", 1.0, channels,
            ["ggH", "qqH", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
        db.add_shape_systematic(
            "CMS_htt_mistag_b", 1.0, channels,
            ["ggH", "qqH", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
        db.add_shape_systematic(
            "CMS_scale_j", 1.0, channels,
            ["ggH", "qqH", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
        db.add_shape_systematic(
            "CMS_scale_met_unclustered", 1.0, channels,
            ["ggH", "qqH", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
    else:
        db.add_shape_systematic("CMS_htt_dyShape", 1.0, channels,
                                ["ZTT", "ZL", "ZJ"])
        db.add_shape_systematic(
            "CMS_htt_eff_b", 1.0, channels,
            ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
        db.add_shape_systematic(
            "CMS_htt_mistag_b", 1.0, channels,
            ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
        db.add_shape_systematic(
            "CMS_scale_j", 1.0, channels,
            ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
        db.add_shape_systematic(
            "CMS_scale_met_unclustered", 1.0, channels,
            ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])

    db.add_shape_systematic("CMS_scale_t_3prong0pi0", 1.0, channels,
                            ["ggH", "qqH", "ZTT", "TTT", "VV", "EWK"])
    db.add_shape_systematic("CMS_scale_t_1prong0pi0", 1.0, channels,
                            ["ggH", "qqH", "ZTT", "TTT", "VV", "EWK"])
    db.add_shape_systematic("CMS_htt_ttbarShape", 1.0, channels,
                            ["TTT", "TTJ"])
    db.add_shape_systematic("CMS_htt_jetToTauFake", 1.0, channels,
                            ["ZJ", "W", "TTJ"])
    db.add_shape_systematic("CMS_htt_eToTauFake_OneProng", 1.0, "et", ["ZL"])
    db.add_shape_systematic("CMS_htt_eToTauFake_OneProngPiZeros", 1.0, "et",
                            ["ZL"])
    db.add_shape_systematic("CMS_htt_mToTauFake_OneProng", 1.0, "mt", ["ZL"])
    db.add_shape_systematic("CMS_htt_mToTauFake_OneProngPiZeros", 1.0, "mt",
                            ["ZL"])

    # Add normalization systematics
    db.add_normalization_systematic(
        "lumi_13TeV", 1.026, channels,
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
    db.add_normalization_systematic(
        "CMS_eff_m", 1.02, "mt",
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
    db.add_normalization_systematic(
        "CMS_eff_e", 1.02, "et",
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
    db.add_normalization_systematic(
        "CMS_eff_t_corr", 1.08, "tt",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VV", "EWK"])
    db.add_normalization_systematic(
        "CMS_eff_t_corr", 1.04, ["et", "mt"],
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VV", "EWK"])
    db.add_normalization_systematic(
        "CMS_eff_t_et", 1.03, "et",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VV", "EWK"])
    db.add_normalization_systematic(
        "CMS_eff_t_mt", 1.03, "mt",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VV", "EWK"])
    db.add_normalization_systematic(
        "CMS_eff_t_tt", 1.06, "tt",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VV", "EWK"])
    db.add_normalization_systematic(
        "CMS_eff_trigger_mt", 1.02, "mt",
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
    db.add_normalization_systematic(
        "CMS_eff_trigger_et", 1.02, "et",
        ["ggH", "qqH", "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VV", "EWK"])
    if not args.QCD_extrap_fit:
        db.add_normalization_systematic("CMS_Extrap_SSOS_mt", 1.03, "mt",
                                        "QCD")
        db.add_normalization_systematic("CMS_Extrap_SSOS_et", 1.05, "et",
                                        "QCD")
        db.add_normalization_systematic("CMS_Extrap_ABCD_tt", 1.03, "tt",
                                        "QCD")
    db.add_normalization_systematic("CMS_htt_wjXsec", 1.04, channels, "W")
    db.add_normalization_systematic("CMS_htt_vvXsec", 1.06, channels, "VV")
    db.add_normalization_systematic("CMS_htt_zjXsec", 1.04, channels,
                                    ["ZTT", "ZL", "ZJ"])
    db.add_normalization_systematic("CMS_htt_ttXsec", 1.06, channels,
                                    ["TTT", "TTJ"])
    db.add_normalization_systematic("CMS_htt_mFakeTau", 1.25, "mt", "ZL")
    db.add_normalization_systematic("CMS_htt_eFakeTau", 1.12, "et", "ZL")
    db.add_normalization_systematic("CMS_scale_ggH", 1.039, channels, "ggH")
    db.add_normalization_systematic("pdf_Higgs_ggH", 1.032, channels, "ggH")
    db.add_normalization_systematic("CMS_scale_qqH", 1.004, channels, "qqH")
    db.add_normalization_systematic("pdf_Higgs_qqH", 1.021, channels, "qqH")

    if args.emb:
        # embedded event systematics
        db.add_shape_systematic("CMS_htt_emb_ttbar_", 1.0, channels, ["ZTT"])
        db.add_shape_systematic("CMS_scale_muonES", 1.0, "mt", ["ZTT"])
    # Extract shapes
    for channel in args.channels:
        if args.gof != None:
            db.extract_shapes(channel, "smhtt", "Run2016", args.gof)
        elif args.HIG16043:
            if channel in ["et", "mt"]:
                db.extract_shapes(channel, "smhtt", "Run2016", "m_vis",
                                  channel + "_0jet")
                db.extract_shapes(channel, "smhtt", "Run2016", "m_sv",
                                  [channel + "_vbf", channel + "_boosted"])
            else:
                db.extract_shapes(channel, "smhtt", "Run2016", "m_sv")
        else:
            db.extract_shapes(channel, "smhtt", "Run2016",
                              "{}_max_score".format(channel))

    # Replace observation with Asimov dataset
    if not args.use_data_for_observation:
        db.replace_observation_by_asimov_dataset(categories)

    # Add bin-by-bin systematics
    db.add_bin_by_bin_systematics(
        signals + backgrounds,
        add_threshold=0.1,
        merge_threshold=0.5,
        fix_norm=True)

    # Perform auto-rebinning
    db.auto_rebin(threshold=1.0, mode=0)

    # Write datacard
    #db.print_datacard()
    db.write("datacard.txt", "datacard_shapes.root")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("produce_datacard.log", logging.DEBUG)
    main(args)
