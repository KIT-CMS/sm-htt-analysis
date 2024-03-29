#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser as rootfile_parser
import Dumbledraw.styles as styles
import ROOT

import argparse
import copy
import yaml
import distutils.util
import logging
logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Plot categories using Dumbledraw from shapes produced by shape-producer module."
    )
    parser.add_argument("-l",
                        "--linear",
                        action="store_true",
                        help="Enable linear x-axis")
    parser.add_argument("-c",
                        "--channels",
                        nargs="+",
                        type=str,
                        required=True,
                        help="Channels")
    parser.add_argument("-e", "--era", type=str, required=True, help="Era")
    parser.add_argument("-o",
                        "--outputfolder",
                        type=str,
                        required=True,
                        help="...yourself")
    parser.add_argument("-i",
                        "--input",
                        type=str,
                        required=True,
                        help="ROOT file with shapes of processes")
    parser.add_argument(
        "--gof-variable",
        type=str,
        default=None,
        help="Enable plotting goodness of fit shapes for given variable")
    parser.add_argument("--png",
                        action="store_true",
                        help="Save plots in png format")
    parser.add_argument("--categories",
                        type=str,
                        required=True,
                        choices=[
                            'inclusive', 'stxs_stage0', "stxs_stage1p1",
                            'stxs_stage1p1cut', 'stxs_stage1p1_15node', 'None'
                        ],
                        help="Select categorization.")
    parser.add_argument("--single-category",
                        type=str,
                        default="",
                        help="Plot single category")
    parser.add_argument("--normalize-by-bin-width",
                        action="store_true",
                        help="Normelize plots by bin width")
    parser.add_argument("--fake-factor",
                        action="store_true",
                        help="Fake factor estimation method used")
    parser.add_argument("--embedding",
                        action="store_true",
                        help="Fake factor estimation method used")
    parser.add_argument("--train-emb",
                        type=lambda x: bool(distutils.util.strtobool(x)),
                        default=True,
                        help="Use fake factor training category")
    parser.add_argument("--train-ff",
                        type=lambda x: bool(distutils.util.strtobool(x)),
                        default=True,
                        help="Use fake factor training category")

    parser.add_argument("--chi2test",
                        action="store_true",
                        help="Print chi2/ndf result in upper-right of subplot")

    parser.add_argument(
        "--blind-data",
        action="store_true",
        help="if set, data is not plotted in signal categories above 0.5")

    parser.add_argument(
        "--blinded-shapes",
        action="store_true",
        help=
        "if set, plotting blinded shapes with no entries above threshold in  signal categories"
    )
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
    # plot signals
    logger.debug("Arguments: {}".format(args))
    if args.gof_variable is not None:
        channel_categories = {
            "et": ["300"],
            "mt": ["300"],
            "tt": ["300"],
            "em": ["300"]
        }
    else:
        channel_categories = {
            # "et": ["ztt", "zll", "w", "tt", "ss", "misc"],
            "et": ["12", "15", "11", "13", "14", "16"],
            # "mt": ["ztt", "zll", "w", "tt", "ss", "misc"],
            "mt": ["12", "15", "11", "13", "14", "16"],
            # "tt": ["ztt", "noniso", "misc"]
            "tt": ["12", "17", "16"],
            # "em": ["ztt", "tt", "ss", "misc", "db"]
            "em": ["12", "13", "14", "16", "19"]
        }
        if args.train_emb:  # swap ztt for embedding
            for chn in ["em", "mt", "et", "tt"]:
                channel_categories[chn].remove("12")
                channel_categories[chn].append("20")
        if args.train_ff:
            for chn in ["mt", "et", "tt"]:  # no change for em
                if chn == "tt":
                    channel_categories[chn].remove("17")
                else:
                    channel_categories[chn].remove("11")
                    channel_categories[chn].remove("14")
                channel_categories[chn].append("21")  # add ff
        if args.categories == "stxs_stage0":
            signalcats = ["1"]  # only 2D Category
        elif args.categories == "stxs_stage1p1":
            signalcats = [str(100 + i) for i in range(5)
                          ] + [str(200 + i) for i in range(4)]
        elif args.categories == "stxs_stage1p1_15node":
            signalcats = [str(100 + i) for i in range(11)
                          ] + [str(200 + i) for i in range(4)]
        elif args.categories == "stxs_stage1p1cut":
            signalcats = [str(100 + i) for i in range(5)
                          ] + [str(200 + i) for i in range(4)]
        elif args.categories == "None":
            signalcats = []
        for channel in ["et", "mt", "tt", "em"]:
            channel_categories[channel] += signalcats
    background_categories = [
            "12", "15", "11", "13", "14", "16", "17", "19", "20", "21"
        ]
    channel_dict = {
        "ee": "ee",
        "em": "e#mu",
        "et": "e#tau_{h}",
        "mm": "#mu#mu",
        "mt": "#mu#tau_{h}",
        "tt": "#tau_{h}#tau_{h}"
    }
    if args.gof_variable is not None:
        category_dict = {"300": "inclusive"}
    else:
        # bkgs+stage1
        category_dict = {
            "1": "ggh",
            "2": "qqh",
            "12": "ztt",
            "15": "zll",
            "11": "wjets",
            "13": "tt",
            "14": "qcd",
            "16": "misc",
            "17": "qcd",
            "19": "diboson",
            "20": "Genuine #tau",
            "21": "Jet #rightarrow #tau_{h}"
        }
        if args.categories == "stxs_stage1p1":
            category_dict.update({
                "100": "ggh 0-jet",
                "101": "ggh 1-jet p_{T}^{H} [0,120]",
                "102": "ggh 1-jet p_{T}^{H} [120,200]",
                "103": "ggh #geq 2-jet",
                "104": "ggh p_{T}^{H} > 200",
                "200": "qqh 2J low mjj",
                "201": "qqh p_{T}^{H}>200",
                "202": "qqh vbftopo mjj>700",
                "203": "qqh vbftopo mjj [350,700]",
            })
        elif args.categories == "stxs_stage1p1cut":
            category_dict.update({
                "100": "ggh 0-jet",
                "101": "ggh 1-jet p_{T}^{H} [0,120]",
                "102": "ggh 1-jet p_{T}^{H} [120,#infty]",
                "103": "ggh #geq 2-jet",
                "104": "ggh p_{T}^{H} #gt 200",
                "200": "qqh 2J",
                "201": "qqh p_{T}^{H} #gt 200",
                "202": "qqh vbftopo_highmjj",
                "203": "qqh vbftopo lowmjj",
            })
        elif args.categories == "stxs_stage1p1_15node":
            category_dict.update({
                "100": "ggh 0-jet, p_{T}^{H} [0,10]",
                "101": "ggh 0-jet, p_{T}^{H} > 10",
                "102": "ggh 1-jet, p_{T}^{H} [0,60]",
                "103": "ggh 1-jet, p_{T}^{H} [60,120]",
                "104": "ggh 1-jet, p_{T}^{H} [120,200]",
                "105": "ggh 2-jet, mjj [0,350], p_{T}^{H} [0,60]",
                "106": "ggh 2-jet, mjj [0,350], p_{T}^{H} [60,120]",
                "107": "ggh 2-jet, mjj [0,350], p_{T}^{H} [120,200]",
                "108": "ggh p_{T}^{H} [200,300]",
                "109": "ggh p_{T}^{H} > 300",
                "110": "ggh 2-jet, mjj > 350, p_{T}^{H} [0,200]",
                "200": "qqh 2-jet low mjj",
                "201": "qqh p_{T}^{H} > 200",
                "202": "qqh vbftopo mjj > 700",
                "203": "qqh vbftopo mjj [350,700]",
            })
        elif args.categories == "stxs_stage0":
            category_dict.update({"1": "2D ggh/qqh category"})
    if args.linear:
        split_value = 0
    else:
        if args.normalize_by_bin_width:
            split_value = 10001
        else:
            split_value = 101

    split_dict = {c: split_value for c in ["et", "mt", "tt", "em"]}

    bkg_processes = ["VVL", "TTL", "ZL", "jetFakes", "EMB"]
    if not args.fake_factor and args.embedding:
        bkg_processes = ["QCD", "VVJ", "W", "TTJ", "ZJ", "ZL", "EMB"]
    if not args.embedding and args.fake_factor:
        bkg_processes = [
            "VVT", "VVJ", "TTT", "TTJ", "ZJ", "ZL", "jetFakes", "ZTT"
        ]
    if not args.embedding and not args.fake_factor:
        bkg_processes = [
            "QCD", "VVT", "VVL", "VVJ", "W", "TTT", "TTL", "TTJ", "ZJ", "ZL",
            "ZTT"
        ]
    all_bkg_processes = [b for b in bkg_processes]
    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()

    if "2016" in args.era:
        era = "2016"
    elif "2017" in args.era:
        era = "2017"
    elif "2018" in args.era:
        era = "2018"
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception
    logger.debug("Channel Categories: {}".format(channel_categories))
    plots = []
    if args.categories == "stxs_stage0" and args.single_category == "1":
        # special for 2D category
        dummy = ROOT.TH1F("dummy", "dummy", 28, 0.0, 28.0)
    else:
        dummy = ROOT.TH1F("dummy", "dummy", 5, 0.0, 1.0)
        dummy_signal = ROOT.TH1F("dummy", "dummy", 28, 0.0, 28.0)
    for channel in args.channels:
        if args.single_category is not "":
            categories = set(channel_categories[channel]).intersection(set([args.single_category]))
        else:
            categories = channel_categories[channel]
        for category in categories:
            if args.categories == "stxs_stage0" and category == "1":
                dummy = dummy_signal
            rootfile = rootfile_parser.Rootfile_parser(args.input)
            if channel == "em" and args.embedding:
                bkg_processes = ["VVL", "W", "TTL", "ZL", "QCD", "EMB"]
            elif channel == "em" and not args.embedding:
                bkg_processes = ["VVL", "W", "TTL", "ZL", "QCD", "ZTT"]
            else:
                bkg_processes = [b for b in all_bkg_processes]
            legend_bkg_processes = copy.deepcopy(bkg_processes)
            legend_bkg_processes.reverse()
            # create plot
            width = 600
            if args.linear:
                plot = dd.Plot([0.3, [0.3, 0.28]],
                               "ModTDR",
                               r=0.04,
                               l=0.14,
                               width=width)
            else:
                plot = dd.Plot([0.5, [0.3, 0.28]],
                               "ModTDR",
                               r=0.04,
                               l=0.14,
                               width=width)

            # get background histograms
            for process in bkg_processes:
                try:
                    plot.add_hist(
                        rootfile.get(era, channel, category, process), process,
                        "bkg")
                    plot.setGraphStyle(process,
                                       "hist",
                                       fillcolor=styles.color_dict[process])
                except BaseException:
                    pass

            # get signal histograms
            plot_idx_to_add_signal = [0, 2] if args.linear else [1, 2]
            for i in plot_idx_to_add_signal:
                try:
                    plot.subplot(i).add_hist(
                        rootfile.get(era, channel, category, "ggH_htt"), "ggH")
                    plot.subplot(i).add_hist(
                        rootfile.get(era, channel, category, "ggH_htt"), "ggH_top")
                    plot.subplot(i).add_hist(
                        rootfile.get(era, channel, category, "qqH_htt"), "qqH")
                    plot.subplot(i).add_hist(
                        rootfile.get(era, channel, category, "qqH_htt"), "qqH_top")
                    if isinstance(
                            rootfile.get(era, channel, category, "ZH_htt"),
                            ROOT.TH1):
                        VHhist = rootfile.get(era, channel, category,
                                              "ZH_htt").Clone("VH")
                    WHhist = rootfile.get(era, channel, category, "WH_htt")
                    if isinstance(WHhist, ROOT.TH1) and VHhist:
                        VHhist.Add(WHhist)
                    elif WHhist:
                        VHhist = WHhist
                    plot.subplot(i).add_hist(VHhist, "VH")
                    plot.subplot(i).add_hist(VHhist, "VH_top")

                    if isinstance(
                            rootfile.get(era, channel, category, "ttH_htt"),
                            ROOT.TH1):
                        plot.subplot(i).add_hist(
                            rootfile.get(era, channel, category, "ttH_htt"),
                            "ttH")
                        plot.subplot(i).add_hist(
                            rootfile.get(era, channel, category, "ttH_htt"),
                            "ttH_top")

                    HWWhist = rootfile.get(era, channel, category, "ggH_hww")
                    if isinstance(
                            rootfile.get(era, channel, category, "ggH_hww"),
                            ROOT.TH1):
                        HWWhist = rootfile.get(era, channel, category,
                                               "ggH_hww").Clone("ggH_hww")
                    qqHWWhist = rootfile.get(era, channel, category,
                                             "qqH_hww")
                    if isinstance(qqHWWhist, ROOT.TH1) and HWWhist:
                        HWWhist.Add(qqHWWhist)
                    elif qqHWWhist:
                        HWWhist = qqHWWhist
                    plot.subplot(i).add_hist(HWWhist, "HWW")
                    plot.subplot(i).add_hist(HWWhist, "HWW_top")
                    # add dummy histogram for range
                    #if args.blinded_shapes:
                    plot.subplot(i).add_hist(dummy, "dummy")

                except BaseException:
                    pass

            # get observed data and total background histograms
            # NOTE: With CMSSW_8_1_0 the TotalBkg definition has changed.
            # print('plot.add_hist(rootfile.get({}, {}, {}, "data_obs")'.format(
            #     era, channel, category))
            data_obs = rootfile.get(era, channel, category, "data_obs")
            if args.blind_data:
                # in this case, all entries above 0.5 are set to zero
                if args.categories == "stxs_stage0" and category == "1":
                    # special case for 2D discriminant
                    for i in xrange(data_obs.GetNbinsX() + 1):
                        if data_obs.GetBinLowEdge(i) in [
                                4.0, 5.0, 6.0
                        ] or data_obs.GetBinLowEdge(i) >= 10.0:
                            data_obs.SetBinContent(i, 0.0)
                            data_obs.SetBinError(i, 0.0)
                elif category not in background_categories:
                    for i in xrange(data_obs.GetNbinsX() + 1):
                        if data_obs.GetBinLowEdge(i) + data_obs.GetBinWidth(i) > 0.5:
                            data_obs.SetBinContent(i, 0.0)
                            data_obs.SetBinError(i, 0.0)
            plot.add_hist(data_obs, "data_obs")

            total_bkg = rootfile.get(era, channel, category, "TotalBkg")
            #ggHHist = rootfile.get(era, channel, category, "ggH")
            #qqHHist = rootfile.get(era, channel, category, "qqH")
            #total_bkg.Add(ggHHist, -1)
            # if qqHHist:
            #     total_bkg.Add(qqHHist, -1)
            plot.add_hist(total_bkg, "total_bkg")

            plot.subplot(0).setGraphStyle("data_obs", "e0")
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                "ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
            plot.subplot(0 if args.linear else 1).setGraphStyle("ggH_top",
                                                                "hist",
                                                                linecolor=0)
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                "qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
            plot.subplot(0 if args.linear else 1).setGraphStyle("qqH_top",
                                                                "hist",
                                                                linecolor=0)
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                "VH", "hist", linecolor=styles.color_dict["VH"], linewidth=3)
            plot.subplot(0 if args.linear else 1).setGraphStyle("VH_top",
                                                                "hist",
                                                                linecolor=0)
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                "ttH", "hist", linecolor=styles.color_dict["ttH"], linewidth=3)
            plot.subplot(0 if args.linear else 1).setGraphStyle("ttH_top",
                                                                "hist",
                                                                linecolor=0)
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                "HWW", "hist", linecolor=styles.color_dict["HWW"], linewidth=3)
            plot.subplot(0 if args.linear else 1).setGraphStyle("HWW_top",
                                                                "hist",
                                                                linecolor=0)
            plot.setGraphStyle("total_bkg",
                               "e2",
                               markersize=0,
                               fillcolor=styles.color_dict["unc"],
                               linecolor=0)
            #if args.blinded_shapes:
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                    "dummy", "hist", linecolor=0, linewidth=0)
            plot.subplot(2).setGraphStyle(
                    "dummy", "hist", linecolor=0, linewidth=0)

            # assemble ratio
            bkg_ggH = plot.subplot(2).get_hist("ggH")
            bkg_qqH = plot.subplot(2).get_hist("qqH")
            bkg_ggH.Add(plot.subplot(2).get_hist("total_bkg"))
            if bkg_qqH:
                bkg_qqH.Add(plot.subplot(2).get_hist("total_bkg"))
            plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH")
            plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH_top")
            plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH")
            plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH_top")
            plot.subplot(2).setGraphStyle("bkg_ggH",
                                          "hist",
                                          linecolor=styles.color_dict["ggH"],
                                          linewidth=3)
            plot.subplot(2).setGraphStyle("bkg_ggH_top", "hist", linecolor=0)
            plot.subplot(2).setGraphStyle("bkg_qqH",
                                          "hist",
                                          linecolor=styles.color_dict["qqH"],
                                          linewidth=3)
            plot.subplot(2).setGraphStyle("bkg_qqH_top", "hist", linecolor=0)

            plot.subplot(2).normalize([
                "total_bkg", "bkg_ggH", "bkg_ggH_top", "bkg_qqH",
                "bkg_qqH_top", "data_obs"
            ], "total_bkg")

            # stack background processes
            plot.create_stack(bkg_processes, "stack")

            # normalize stacks by bin-width
            if args.normalize_by_bin_width:
                plot.subplot(0).normalizeByBinWidth()
                plot.subplot(1).normalizeByBinWidth()

            # set axes limits and labels
            plot.subplot(0).setYlims(
                split_dict[channel],
                max(2 * plot.subplot(0).get_hist("data_obs").GetMaximum(),
                    split_dict[channel] * 2))

            if args.categories == "stxs_stage1p1_15node":
                plot.subplot(2).setYlims(0.45, 1.65)
            else:
                plot.subplot(2).setYlims(0.85, 1.25)
            if category in signalcats:
                plot.subplot(0).setLogY()
                plot.subplot(0).setYlims(1, 150000000)
                if channel == "em":
                    plot.subplot(0).setYlims(1, 150000000)

            if not args.linear:
                plot.subplot(1).setYlims(0.1, split_dict[channel])
                plot.subplot(1).setLogY()
                plot.subplot(1).setYlabel(
                    "")  # otherwise number labels are not drawn on axis
            if args.gof_variable is not None:
                if args.gof_variable in styles.x_label_dict[args.channels[0]]:
                    x_label = styles.x_label_dict[args.channels[0]][
                        args.gof_variable]
                else:
                    x_label = args.gof_variable
                plot.subplot(2).setXlabel(x_label)
            elif args.categories == "stxs_stage0" and category == "1":
                plot.subplot(2).setXlabel("2D discriminator bin index")
            else:
                plot.subplot(2).setXlabel("NN output")
            if args.normalize_by_bin_width:
                plot.subplot(0).setYlabel("dN/d(NN output)")
            else:
                plot.subplot(0).setYlabel("N_{events}")

            plot.subplot(2).setYlabel("")

            # plot.scaleXTitleSize(0.8)
            if args.categories == "stxs_stage1p1_15node":
                plot.subplot(2).setXlims(0.0, 1.0)
                plot.subplot(0).setXlims(0.0, 1.0)
            # plot.scaleXLabelSize(0.8)
            # plot.scaleYTitleSize(0.8)
            plot.scaleYLabelSize(0.8)
            # plot.scaleXLabelOffset(2.0)
            plot.scaleYTitleOffset(1.1)
            plot.subplot(2).setNYdivisions(3, 5)
            plot.subplot(2).setNXdivisions(5, 3)
            # if not channel == "tt" and category in ["11", "12", "13", "14", "15", "16"]:
            #    plot.subplot(2).changeXLabels(["0.2", "0.4", "0.6", "0.8", "1.0"])

            # draw subplots. Argument contains names of objects to be drawn in
            # corresponding order.
            
            procs_to_draw_0 = [
                "stack", "total_bkg", "data_obs"
            ] if args.linear else ["stack", "total_bkg", "data_obs"]
            procs_to_draw_1 = [
                "stack", "total_bkg", "data_obs"
            ]
            procs_to_draw_2 = [
                "total_bkg", "bkg_ggH", "bkg_ggH_top", "bkg_qqH",
                "bkg_qqH_top", "data_obs"
            ]
            if category not in background_categories:
                signals = [ "ggH", "ggH_top", "qqH", "qqH_top", "VH", "VH_top", "ttH", "ttH_top", "HWW", "HWW_top"]
                procs_to_draw_0 = procs_to_draw_0 + signals
                procs_to_draw_1 = procs_to_draw_1 + signals
            # if args.blinded_shapes and category not in background_categories:
            #     procs_to_draw_0 = ["dummy"] + procs_to_draw_0
            #     procs_to_draw_1 = ["dummy"] + procs_to_draw_1
            #     procs_to_draw_2 = ["dummy"] + procs_to_draw_2
            #if args.blinded_shapes:
            procs_to_draw_0 = ["dummy"] + procs_to_draw_0
            procs_to_draw_1 = ["dummy"] + procs_to_draw_1
            procs_to_draw_2 = ["dummy"] + procs_to_draw_2
            plot.subplot(0).Draw(procs_to_draw_0)
            if not args.linear:
                plot.subplot(1).Draw(procs_to_draw_1)
            plot.subplot(2).Draw(procs_to_draw_2)
            if not (args.categories == "stxs_stage0" and category == "1"):
                plot.subplot(2).setXlims(0.0, 1.0)
                plot.subplot(0).setXlims(0.0, 1.0)
            # create legends
            suffix = ["", "_top"]
            for i in range(2):
                plot.add_legend(width=0.6, height=0.15)
                for process in legend_bkg_processes:
                    try:
                        plot.legend(i).add_entry(
                            0, process,
                            styles.legend_label_dict[process.replace(
                                "TTL", "TT").replace("VVL", "VV")], 'f')
                    except BaseException:
                        pass
                plot.legend(i).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
                if category not in background_categories:
                    plot.legend(i).add_entry(0 if args.linear else 1,
                                            "ggH%s" % suffix[i], "gg#rightarrowH",
                                            'l')
                    plot.legend(i).add_entry(0 if args.linear else 1,
                                            "qqH%s" % suffix[i], "qq#rightarrowH",
                                            'l')
                    plot.legend(i).add_entry(0 if args.linear else 1,
                                            "VH%s" % suffix[i], "qq#rightarrowVH",
                                            'l')
                    try:
                        plot.legend(i).add_entry(0 if args.linear else 1,
                                                "ttH%s" % suffix[i], "ttH", 'l')
                        plot.legend(i).add_entry(0 if args.linear else 1,
                                                "HWW%s" % suffix[i],
                                                "H#rightarrowWW", 'l')
                    except BaseException:
                        pass
                plot.legend(i).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i).setNColumns(3)
            plot.legend(0).Draw()
            plot.legend(1).setAlpha(0.0)
            plot.legend(1).Draw()

            if args.chi2test:
                f = ROOT.TFile(args.input, "read")
                background = f.Get("htt_{}_{}_Run{}_{}/TotalBkg".format(
                    channel, category, args.era,
                    "prefit" if "prefit" in args.input else "postfit"))
                data = f.Get("htt_{}_{}_Run{}_{}/data_obs".format(
                    channel, category, args.era,
                    "prefit" if "prefit" in args.input else "postfit"))
                chi2 = data.Chi2Test(background, "UW CHI2/NDF")
                plot.DrawText(0.7, 0.3,
                              "\chi^{2}/ndf = " + str(round(chi2, 3)))

            for i in range(2):
                plot.add_legend(reference_subplot=2,
                                pos=1,
                                width=0.5,
                                height=0.03)
                plot.legend(i + 2).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i + 2).add_entry(0 if args.linear else 1,
                                             "ggH%s" % suffix[i], "ggH+bkg.",
                                             'l')
                plot.legend(i + 2).add_entry(0 if args.linear else 1,
                                             "qqH%s" % suffix[i], "qqH+bkg.",
                                             'l')
                plot.legend(i + 2).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
                plot.legend(i + 2).setNColumns(4)
            plot.legend(2).Draw()
            plot.legend(3).setAlpha(0.0)
            plot.legend(3).Draw()

            # draw additional labels
            plot.DrawCMS()
            if "2016" in args.era:
                plot.DrawLumi("35.9 fb^{-1} (2016, 13 TeV)", textsize=0.5)
            elif "2017" in args.era:
                plot.DrawLumi("41.5 fb^{-1} (2017, 13 TeV)", textsize=0.5)
            elif "2018" in args.era:
                plot.DrawLumi("59.7 fb^{-1} (2018, 13 TeV)", textsize=0.5)
            elif "all" in args.era:
                plot.DrawLumi(
                    "(35.9 + 41.5 + 59.7) fb^{-1} (2016+2017+2018, 13 TeV)", textsize=0.5)
            else:
                logger.critical("Era {} is not implemented.".format(args.era))
                raise Exception

            plot.DrawChannelCategoryLabel(
                "%s, %s" % (channel_dict[channel], category_dict[category]),
                begin_left=None, textsize=0.032)    

            # save plot
            postfix = "prefit" if "prefit" in args.input else "postfit" if "postfit" in args.input else "undefined"
            plot.save(
                "%s/%s_%s_%s_%s.%s" %
                (args.outputfolder, args.era, channel, args.gof_variable if
                 args.gof_variable is not None else category, postfix, "png"))
            plot.save(
                "%s/%s_%s_%s_%s.%s" %
                (args.outputfolder, args.era, channel, args.gof_variable if
                 args.gof_variable is not None else category, postfix, "pdf"))
            # work around to have clean up seg faults only at the end of the
            # script
            plots.append(plot)


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_plot_shapes.log".format(args.era), logging.WARNING)
    main(args)
