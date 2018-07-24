#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser as rootfile_parser
import Dumbledraw.styles as styles

import argparse
import copy
import yaml

import logging
logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Plot categories using Dumbledraw from shapes produced by shape-producer module."
    )
    parser.add_argument(
        "-l", "--linear", action="store_true", help="Enable linear x-axis")
    parser.add_argument(
        "-c",
        "--channels",
        nargs="+",
        type=str,
        required=True,
        help="Channels")
    parser.add_argument("-e", "--era", type=str, required=True, help="Era")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="ROOT file with shapes of processes")
    parser.add_argument(
        "--gof-variable",
        type=str,
        default=None,
        help="Enable plotting goodness of fit shapes for given variable")
    parser.add_argument(
        "--png", action="store_true", help="Save plots in png format")
    parser.add_argument(
        "--stxs-categories",
        type=int,
        required=True,
        help="Select STXS categorization.")
    parser.add_argument(
        "--normalize-by-bin-width",
        action="store_true",
        help="Normelize plots by bin width")
    parser.add_argument(
        "--fake-factor",
        action="store_true",
        help="Fake factor estimation method used")
    parser.add_argument(
        "--embedding",
        action="store_true",
        help="Fake factor estimation method used")
    parser.add_argument(
        "--chi2test",
        action="store_true",
        help="Print chi2/ndf result in upper-right of subplot")

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
    if args.gof_variable != None:
        channel_categories = {c: [args.gof_variable] for c in args.channels}
    else:
        channel_categories = {
            #"et": ["ztt", "zll", "w", "tt", "ss", "misc"],
            "et": ["12", "15", "11", "13", "14", "16"],
            #"mt": ["ztt", "zll", "w", "tt", "ss", "misc"],
            "mt": ["12", "15", "11", "13", "14", "16"],
            #"tt": ["ztt", "noniso", "misc"]
            "tt": ["12", "17", "16"]
        }
        if args.stxs_categories == 0:
            for channel in ["et", "mt", "tt"]:
                channel_categories[channel] += ["1", "2"]
        elif args.stxs_categories == 1:
            for channel in ["et", "mt", "tt"]:
                channel_categories[channel] += ["1", "2"]
        else:
            logger.critical("Selected unkown STXS categorization {}",
                            args.stxs_categories)
            raise Exception
    channel_dict = {
        "ee": "ee",
        "em": "e#mu",
        "et": "e#tau_{h}",
        "mm": "#mu#mu",
        "mt": "#mu#tau_{h}",
        "tt": "#tau_{h}#tau_{h}"
    }
    if args.gof_variable != None:
        category_dict = {args.gof_variable: "inclusive"}
    else:
        category_dict = {
            "1": "ggH",
            "2": "VBF",
            "3": "ggH, unrolled",
            "4": "VBF, unrolled",
            "12": "Z#rightarrow#tau#tau",
            "15": "Z#rightarrowll",
            "11": "W+jets",
            "13": "t#bar{t}",
            "14": "same sign",
            "16": "misc",
            "17": "noniso"
        }
    if args.linear == True:
        split_value = 0
    else:
        if args.normalize_by_bin_width:
            split_value = 10001
        else:
            split_value = 101

    split_dict = {c: split_value for c in ["et", "mt", "tt"]}

    bkg_processes = [
        "EWKZ", "QCD", "VVT", "VVJ", "W", "TTT", "TTJ", "ZJ", "ZL", "ZTT"
    ]

    if args.embedding:
        bkg_processes = [b for b in bkg_processes
                         if b not in ["ZTT", "TTT"]] + ["EMB", "TTL"]
    if args.fake_factor:
        bkg_processes = [
            b for b in bkg_processes if b not in ["QCD", "VVJ", "TTJ", "W", "ZJ"]
        ] + ["jetFakes"]
    all_bkg_processes = [b for b in bkg_processes]
    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()

    rootfile = rootfile_parser.Rootfile_parser(args.input)

    plots = []
    for channel in args.channels:
        if channel == "tt":
            if args.embedding:
                bkg_processes = [
                    b for b in all_bkg_processes if b is not "TTL"
                ]
            else:
                bkg_processes = [b for b in all_bkg_processes]
        else:
            bkg_processes = [b for b in all_bkg_processes]
        legend_bkg_processes = copy.deepcopy(bkg_processes)
        legend_bkg_processes.reverse()

        for category in channel_categories[channel]:
            # create plot
            width = 600
            if args.stxs_categories == 1:
                if category in ["1", "2"]:
                    width = 1200
            if args.linear == True:
                plot = dd.Plot(
                    [0.3, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)
            else:
                plot = dd.Plot(
                    [0.5, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)

            # get background histograms
            for process in bkg_processes:
                plot.add_hist(
                    rootfile.get(channel, category, process), process, "bkg")
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict[process])

            # get signal histograms
            for i in range(2):
                plot.subplot(i + 1).add_hist(
                    rootfile.get(channel, category, "ggH"), "ggH")
                plot.subplot(i + 1).add_hist(
                    rootfile.get(channel, category, "ggH"), "ggH_top")
                plot.subplot(i + 1).add_hist(
                    rootfile.get(channel, category, "qqH"), "qqH")
                plot.subplot(i + 1).add_hist(
                    rootfile.get(channel, category, "qqH"), "qqH_top")

            # get observed data and total background histograms
            plot.add_hist(
                rootfile.get(channel, category, "data_obs"), "data_obs")
            plot.add_hist(
                rootfile.get(channel, category, "TotalBkg"), "total_bkg")

            plot.subplot(0).setGraphStyle("data_obs", "e0")
            plot.subplot(1).setGraphStyle(
                "ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
            plot.subplot(1).setGraphStyle("ggH_top", "hist", linecolor=0)
            plot.subplot(1).setGraphStyle(
                "qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
            plot.subplot(1).setGraphStyle("qqH_top", "hist", linecolor=0)
            plot.setGraphStyle(
                "total_bkg",
                "e2",
                markersize=0,
                fillcolor=styles.color_dict["unc"],
                linecolor=0)

            # assemble ratio
            bkg_ggH = plot.subplot(2).get_hist("ggH")
            bkg_qqH = plot.subplot(2).get_hist("qqH")
            bkg_ggH.Add(plot.subplot(2).get_hist("total_bkg"))
            bkg_qqH.Add(plot.subplot(2).get_hist("total_bkg"))
            plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH")
            plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH_top")
            plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH")
            plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH_top")
            plot.subplot(2).setGraphStyle(
                "bkg_ggH",
                "hist",
                linecolor=styles.color_dict["ggH"],
                linewidth=3)
            plot.subplot(2).setGraphStyle("bkg_ggH_top", "hist", linecolor=0)
            plot.subplot(2).setGraphStyle(
                "bkg_qqH",
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
                max(2 * plot.subplot(0).get_hist("total_bkg").GetMaximum(),
                    split_dict[channel] * 2))

            plot.subplot(2).setYlims(0.75, 1.45)
            if channel == "tt" and category == "qqh":
                plot.subplot(2).setYlims(0.75, 2.65)
            if args.linear != True:
                plot.subplot(1).setYlims(0.1, split_dict[channel])
                plot.subplot(1).setLogY()
                plot.subplot(1).setYlabel(
                    "")  # otherwise number labels are not drawn on axis
            if args.gof_variable != None:
                if args.gof_variable in styles.x_label_dict[args.channels[0]]:
                    x_label = styles.x_label_dict[args.channels[0]][
                        args.gof_variable]
                else:
                    x_label = args.gof_variable
                plot.subplot(2).setXlabel(x_label)
            else:
                plot.subplot(2).setXlabel("NN score")
            if args.normalize_by_bin_width:
                plot.subplot(0).setYlabel("N_{events}/bin width")
            else:
                plot.subplot(0).setYlabel("N_{events}")

            plot.subplot(2).setYlabel("Ratio to Bkg.")

            #plot.scaleXTitleSize(0.8)
            #plot.scaleXLabelSize(0.8)
            #plot.scaleYTitleSize(0.8)
            plot.scaleYLabelSize(0.8)
            #plot.scaleXLabelOffset(2.0)
            plot.scaleYTitleOffset(1.1)

            #plot.subplot(2).setNYdivisions(3, 5)

            # draw subplots. Argument contains names of objects to be drawn in corresponding order.
            plot.subplot(0).Draw(["stack", "total_bkg", "data_obs"])
            if args.linear != True:
                plot.subplot(1).Draw([
                    "stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top",
                    "data_obs"
                ])
            plot.subplot(2).Draw([
                "total_bkg", "bkg_ggH", "bkg_ggH_top", "bkg_qqH",
                "bkg_qqH_top", "data_obs"
            ])

            # create legends
            suffix = ["", "_top"]
            for i in range(2):

                plot.add_legend(width=0.48, height=0.15)
                for process in legend_bkg_processes:
                    plot.legend(i).add_entry(
                        0, process, styles.legend_label_dict[process], 'f')
                plot.legend(i).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
                plot.legend(i).add_entry(1, "ggH%s" % suffix[i], "ggH", 'l')
                plot.legend(i).add_entry(1, "qqH%s" % suffix[i], "qqH", 'l')
                plot.legend(i).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i).setNColumns(3)
            plot.legend(0).Draw()
            plot.legend(1).setAlpha(0.0)
            plot.legend(1).Draw()

            if args.chi2test:
                import ROOT as r
                f = r.TFile(args.input, "read")
                background = f.Get("htt_{}_{}_13TeV_{}/TotalBkg".format(
                    channel, category, "prefit"
                    if "prefit" in args.input else "postfit"))
                data = f.Get("htt_{}_{}_13TeV_{}/data_obs".format(
                    channel, category, "prefit"
                    if "prefit" in args.input else "postfit"))
                chi2 = data.Chi2Test(background, "UW CHI2/NDF")
                plot.DrawText(0.7, 0.3,
                              "\chi^{2}/ndf = " + str(round(chi2, 3)))

            for i in range(2):
                plot.add_legend(
                    reference_subplot=2, pos=1, width=0.5, height=0.03)
                plot.legend(i + 2).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i + 2).add_entry(1, "ggH%s" % suffix[i],
                                             "ggH+bkg.", 'l')
                plot.legend(i + 2).add_entry(1, "qqH%s" % suffix[i],
                                             "qqH+bkg.", 'l')
                plot.legend(i + 2).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
                plot.legend(i + 2).setNColumns(4)
            plot.legend(2).Draw()
            plot.legend(3).setAlpha(0.0)
            plot.legend(3).Draw()

            # draw additional labels
            plot.DrawCMS()
            if "2016" in args.era:
                plot.DrawLumi("35.9 fb^{-1} (13 TeV)")
            elif "2017" in args.era:
                plot.DrawLumi("41.3 fb^{-1} (13 TeV)")
            else:
                logger.critical("Era {} is not implemented.".format(args.era))
                raise Exception

            posChannelCategoryLabelLeft = None
            if args.stxs_categories == 1:
                if category in ["1", "2"]:
                    posChannelCategoryLabelLeft = 0.075
            plot.DrawChannelCategoryLabel(
                "%s, %s" % (channel_dict[channel], category_dict[category]),
                begin_left=posChannelCategoryLabelLeft)

            # save plot
            postfix = "prefit" if "prefit" in args.input else "postfit" if "postfit" in args.input else "undefined"
            plot.save("plots/%s_%s_%s_%s.%s" % (args.era, channel, category,
                                                postfix, "png"
                                                if args.png else "pdf"))
            plots.append(
                plot
            )  # work around to have clean up seg faults only at the end of the script


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_plot_shapes.log".format(args.era), logging.INFO)
    main(args)
