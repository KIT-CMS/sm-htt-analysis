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
        "--era", type=str, required=True, help="Experiment era.")
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
        "--stxs-signals",
        type=int,
        required=True,
        help="Select STXS signal templates.")
    parser.add_argument(
        "--stxs-categories",
        type=int,
        required=True,
        help="Select STXS categorization.")
    parser.add_argument(
        "--embedding",
        action="store_true",
        default=False,
        help=
        "Create systematics custom to embedded events instead of ZTT simulation."
    )
    parser.add_argument(
        "--fake-factor",
        action="store_true",
        default=False,
        help="Use fake factor estimation.")
    return parser.parse_args()


def main(args):
    db = DatacardBuilder(args.shapes)

    # Select era
    if "2016" in args.era:
        era = "Run2016"
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    # Register observations, signals and backgrounds
    channels = []
    categories = []
    if args.stxs_signals == 0:
        signals = ["ggH125", "qqH125"]
    elif args.stxs_signals == 1:
        signals = [
            "ggH125_0J", "ggH125_1J", "ggH125_GE2J", "ggH125_VBFTOPO",
            "qqH125_VBFTOPO_JET3VETO", "qqH125_VBFTOPO_JET3", "qqH125_REST",
            "qqH125_PTJET1_GT200"
        ]
    else:
        logger.critical("Unknown STXS stage {} for signals selected.".format(
            args.stxs_signals))
        raise Exception
    tau_fakes = ["jetFakes"] if args.fake_factor else [
        "ZJ", "W", "TTJ", "VVJ", "QCD"
    ]
    backgrounds = ["ZTT", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes
    if args.QCD_extrap_fit:
        signals = ["QCD"]
        backgrounds = [
            "ZTT", "ZL", "ZJ", "W", "TTT", "TTJ", "VVT", "VVJ", "EWKZ"
        ]

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
                "et_ztt", "et_zll", "et_w", "et_tt", "et_ss", "et_misc"
            ]
            if args.stxs_categories == 0:
                et_categories += ["et_ggh", "et_qqh"]
            elif args.stxs_categories == 1:
                et_categories += [
                    "et_ggh_0jet", "et_ggh_1jet", "et_ggh_ge2jets",
                    "et_qqh_l2jets", "et_qqh_2jets", "et_qqh_g2jets"
                ]
            else:
                logger.critical(
                    "Unknown STXS stage {} for categories selected.".format(
                        args.stxs_signals))
                raise Exception
        et_category_pairs = db.make_pairs(et_categories)

        db.add_observation("125", "smhtt", era, "et", et_category_pairs)
        db.add_signals("125", "smhtt", era, "et", signals, et_category_pairs)
        db.add_backgrounds("125", "smhtt", era, "et", backgrounds,
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
                "mt_ztt", "mt_zll", "mt_w", "mt_tt", "mt_ss", "mt_misc"
            ]
            if args.stxs_categories == 0:
                mt_categories += ["mt_ggh", "mt_qqh"]
            elif args.stxs_categories == 1:
                mt_categories += [
                    "mt_ggh_0jet", "mt_ggh_1jet", "mt_ggh_ge2jets",
                    "mt_qqh_l2jets", "mt_qqh_2jets", "mt_qqh_g2jets"
                ]
            else:
                logger.critical(
                    "Unknown STXS stage {} for categories selected.".format(
                        args.stxs_signals))
                raise Exception
        mt_category_pairs = db.make_pairs(mt_categories)

        db.add_observation("125", "smhtt", era, "mt", mt_category_pairs)
        db.add_signals("125", "smhtt", era, "mt", signals, mt_category_pairs)
        db.add_backgrounds("125", "smhtt", era, "mt", backgrounds,
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
            tt_categories = ["tt_ztt", "tt_noniso", "tt_misc"]
            if args.stxs_categories == 0:
                tt_categories += ["tt_ggh", "tt_qqh"]
            elif args.stxs_categories == 1:
                tt_categories += [
                    "tt_ggh_0jet", "tt_ggh_1jet", "tt_ggh_ge2jets",
                    "tt_qqh_l2jets", "tt_qqh_2jets", "tt_qqh_g2jets"
                ]
            else:
                logger.critical(
                    "Unknown STXS stage {} for categories selected.".format(
                        args.stxs_signals))
                raise Exception
        tt_category_pairs = db.make_pairs(tt_categories)

        db.add_observation("125", "smhtt", era, "tt", tt_category_pairs)
        db.add_signals("125", "smhtt", era, "tt", signals, tt_category_pairs)
        db.add_backgrounds("125", "smhtt", era, "tt", backgrounds,
                           tt_category_pairs)

        channels.append("tt")
        categories += tt_categories

    # Add shapes systematics
    if args.fake_factor:
        tau_fakes = [
        ]  #leave out data driven processes for systematic processes and treat them separately
        for channel in ["et", "mt", "tt"]:
            db.add_shape_systematic("norm_ff_qcd_%s_syst" % channel, 1.0,
                                    channel, "jetFakes")

            db.add_shape_systematic("norm_ff_qcd_dm0_njet0_%s_stat" % channel,
                                    1.0, channel, "jetFakes")
            db.add_shape_systematic("norm_ff_qcd_dm0_njet1_%s_stat" % channel,
                                    1.0, channel, "jetFakes")
            db.add_shape_systematic("norm_ff_qcd_dm1_njet0_%s_stat" % channel,
                                    1.0, channel, "jetFakes")
            db.add_shape_systematic("norm_ff_qcd_dm1_njet1_%s_stat" % channel,
                                    1.0, channel, "jetFakes")

            db.add_shape_systematic("norm_ff_w_dm0_njet0_%s_stat" % channel,
                                    1.0, channel, "jetFakes")
            db.add_shape_systematic("norm_ff_w_dm0_njet1_%s_stat" % channel,
                                    1.0, channel, "jetFakes")
            db.add_shape_systematic("norm_ff_w_dm1_njet0_%s_stat" % channel,
                                    1.0, channel, "jetFakes")
            db.add_shape_systematic("norm_ff_w_dm1_njet1_%s_stat" % channel,
                                    1.0, channel, "jetFakes")

        db.add_shape_systematic("norm_ff_tt_dm0_njet0_stat", 1.0, ["et", "mt"],
                                "jetFakes")
        db.add_shape_systematic("norm_ff_tt_dm0_njet1_stat", 1.0, ["et", "mt"],
                                "jetFakes")
        db.add_shape_systematic("norm_ff_tt_dm1_njet0_stat", 1.0, ["et", "mt"],
                                "jetFakes")
        db.add_shape_systematic("norm_ff_tt_dm1_njet1_stat", 1.0, ["et", "mt"],
                                "jetFakes")

        db.add_shape_systematic("norm_ff_w_syst", 1.0, ["et", "mt"],
                                "jetFakes")
        db.add_shape_systematic("norm_ff_w_tt_syst", 1.0, "tt",
                                "jetFakes")
        db.add_shape_systematic("norm_ff_tt_syst", 1.0, ["et", "mt"],
                                "jetFakes")
        db.add_shape_systematic("norm_ff_tt_tt_syst", 1.0, "tt",
                                "jetFakes")

        db.add_shape_systematic("norm_ff_w_frac_tt_syst", 1.0, "tt",
                                "jetFakes")
        db.add_shape_systematic("norm_ff_tt_frac_tt_syst", 1.0, "tt",
                                "jetFakes")
        db.add_shape_systematic("norm_ff_dy_frac_tt_syst", 1.0, "tt",
                                "jetFakes")

    else:
        tau_fakes = [
            "ZJ", "W", "TTJ", "VVJ"
        ]  #leave out data driven processes for systematic processes and treat them separately
    if args.embedding:
        db.add_shape_systematic("CMS_htt_dyShape_13TeV", 1.0, channels, ["ZL"]
                                if args.fake_factor else ["ZL", "ZJ"])
        db.add_shape_systematic(
            "CMS_htt_eff_b_13TeV", 1.0, channels,
            ["ggH", "qqH", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
        db.add_shape_systematic(
            "CMS_htt_mistag_b_13TeV", 1.0, channels,
            ["ggH", "qqH", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
        db.add_shape_systematic(
            "CMS_scale_j_13TeV", 1.0, channels,
            ["ggH", "qqH", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
        db.add_shape_systematic(
            "CMS_scale_met_unclustered_13TeV", 1.0, channels,
            ["ggH", "qqH", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
    else:
        db.add_shape_systematic("CMS_htt_dyShape_13TeV", 1.0, channels,
                                ["ZTT", "ZL", "ZJ"])
        db.add_shape_systematic(
            "CMS_htt_eff_b_13TeV", 1.0, channels,
            ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
        db.add_shape_systematic(
            "CMS_htt_mistag_b_13TeV", 1.0, channels,
            ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
        db.add_shape_systematic(
            "CMS_scale_j_13TeV", 1.0, channels,
            ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
        db.add_shape_systematic(
            "CMS_scale_met_unclustered_13TeV", 1.0, channels,
            ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)

    db.add_shape_systematic("CMS_scale_t_3prong_13TeV", 1.0, channels,
                            ["ggH", "qqH", "ZTT", "TTT", "VVT", "EWKZ"])
    db.add_shape_systematic("CMS_scale_t_1prong_13TeV", 1.0, channels,
                            ["ggH", "qqH", "ZTT", "TTT", "VVT", "EWKZ"])
    db.add_shape_systematic("CMS_scale_t_1prong1pizero_13TeV", 1.0, channels,
                            ["ggH", "qqH", "ZTT", "TTT", "VVT", "EWKZ"])
    db.add_shape_systematic("CMS_htt_ttbarShape_13TeV", 1.0, channels,
                            ["TTT", "TTJ"])
    db.add_shape_systematic("CMS_htt_jetToTauFake_13TeV", 1.0, channels,
                            ["ZJ", "W", "TTJ", "VVJ"])
    db.add_shape_systematic("CMS_eFakeTau_1prong_13TeV", 1.0, "et", ["ZL"])
    db.add_shape_systematic("CMS_eFakeTau_1prong1pizero_13TeV", 1.0, "et",
                            ["ZL"])
    db.add_shape_systematic("CMS_ZLShape_et_1prong_13TeV", 1.0, "et", ["ZL"])
    db.add_shape_systematic("CMS_ZLShape_et_1prong1pizero_13TeV", 1.0, "et", ["ZL"])
    db.add_shape_systematic("CMS_mFakeTau_1prong_13TeV", 1.0, "mt", ["ZL"])
    db.add_shape_systematic("CMS_mFakeTau_1prong1pizero_13TeV", 1.0, "mt",
                            ["ZL"])
    db.add_shape_systematic("CMS_ZLShape_mt_1prong_13TeV", 1.0, "mt", ["ZL"])
    db.add_shape_systematic("CMS_ZLShape_mt_1prong1pizero_13TeV", 1.0, "mt", ["ZL"])

    # Add normalization systematics
    db.add_normalization_systematic(
        "lumi_13TeV", 1.026, channels,
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
    db.add_normalization_systematic(
        "CMS_eff_m", 1.02, "mt",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
    db.add_normalization_systematic(
        "CMS_eff_e", 1.02, "et",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
    db.add_normalization_systematic(
        "CMS_eff_t_corr", 1.08, "tt",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"])
    db.add_normalization_systematic(
        "CMS_eff_t_corr", 1.04, ["et", "mt"],
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"])
    db.add_normalization_systematic(
        "CMS_eff_t_et", 1.03, "et",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"])
    db.add_normalization_systematic(
        "CMS_eff_t_mt", 1.03, "mt",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"])
    db.add_normalization_systematic(
        "CMS_eff_t_tt", 1.06, "tt",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"])
    db.add_normalization_systematic(
        "CMS_eff_trigger_mt", 1.02, "mt",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
    db.add_normalization_systematic(
        "CMS_eff_trigger_et", 1.02, "et",
        ["ggH", "qqH", "ZTT", "ZL", "TTT", "VVT", "EWKZ"] + tau_fakes)
    if not args.QCD_extrap_fit and not args.fake_factor:
        db.add_normalization_systematic("CMS_Extrap_SSOS_mt", 1.03, "mt",
                                        "QCD")
        db.add_normalization_systematic("CMS_Extrap_SSOS_et", 1.05, "et",
                                        "QCD")
        db.add_normalization_systematic("CMS_Extrap_ABCD_tt", 1.03, "tt",
                                        "QCD")
    if args.fake_factor:
        db.add_normalization_systematic("CMS_htt_vvXsec", 1.06, channels,
                                        ["VVT"])
        db.add_normalization_systematic("CMS_htt_zjXsec", 1.04, channels,
                                        ["ZTT", "ZL"])
        db.add_normalization_systematic("CMS_htt_ttXsec", 1.06, channels,
                                        ["TTT"])
        #TODO add fake factor norm uncs.
    else:
        db.add_normalization_systematic("CMS_htt_wjXsec", 1.04, channels, "W")
        db.add_normalization_systematic("CMS_htt_vvXsec", 1.06, channels,
                                        ["VVT", "VVJ"])
        db.add_normalization_systematic("CMS_htt_zjXsec", 1.04, channels,
                                        ["ZTT", "ZL", "ZJ"])
        db.add_normalization_systematic("CMS_htt_ttXsec", 1.06, channels,
                                        ["TTT", "TTJ"])
    db.add_normalization_systematic("CMS_mFakeTau", 1.25, "mt", "ZL")
    db.add_normalization_systematic("CMS_eFakeTau", 1.12, "et", "ZL")
    db.add_normalization_systematic("CMS_scale_ggH", 1.039, channels, "ggH")
    db.add_normalization_systematic("pdf_Higgs_ggH", 1.032, channels, "ggH")
    db.add_normalization_systematic("CMS_scale_qqH", 1.004, channels, "qqH")
    db.add_normalization_systematic("pdf_Higgs_qqH", 1.021, channels, "qqH")

    if args.embedding:
        # embedded event systematics
        db.add_shape_systematic("CMS_htt_emb_ttbar", 1.0, channels, ["ZTT"])
        db.add_shape_systematic("CMS_scale_muonES", 1.0, "mt", ["ZTT"])
    # Extract shapes
    for channel in args.channels:
        if args.gof != None:
            db.extract_shapes(channel, "smhtt", era, args.gof)
        elif args.HIG16043:
            if channel in ["et", "mt"]:
                db.extract_shapes(channel, "smhtt", era, "m_vis",
                                  channel + "_0jet")
                db.extract_shapes(channel, "smhtt", era, "m_sv",
                                  [channel + "_vbf", channel + "_boosted"])
            else:
                db.extract_shapes(channel, "smhtt", era, "m_sv")
        else:
            db.extract_shapes(channel, "smhtt", era,
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
    db.write("{}_datacard.txt".format(args.era),
             "{}_datacard_shapes.root".format(args.era))


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_produce_datacard.log".format(args.era), logging.DEBUG)
    main(args)
