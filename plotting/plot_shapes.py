#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser as rootfile_parser
import Dumbledraw.styles as styles

import argparse
import copy

import logging
logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Plot categories using Dumbledraw from shapes produced by shape-producer module."
    )
    '''parser.add_argument(
        "-c",
        "--categories",
        nargs="+",
        type=str,
        required=True,
        help="Categories")'''
    parser.add_argument(
        "-c",
        "--channels",
        nargs="+",
        type=str,
        required=True,
        help="Channels")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="ROOT file with shapes of processes")
    parser.add_argument(
        "--x-label", type=str, default="NN score", help="Label on x-axis")
    parser.add_argument(
        "--png", action='store_true', help="Save plots in png format")
    '''parser.add_argument(
        "--num-processes",
        type=int,
        default=10,
        help="Number of processes used for plotting")'''
    '''parser.add_argument(
        "--scale-signal",
        type=int,
        default=1,
        help="Scale the signal yield by this factor")'''

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
    channel_categories = {
        "et": ["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"],
        "mt": ["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"],
        "tt": ["ggh", "qqh", "ztt", "noniso", "misc"]
    }
    channel_dict = {
        "ee": "ee",
        "em": "e#mu",
        "et": "e#tau_{h}",
        "mm": "#mu#mu",
        "mt": "#mu#tau_{h}",
        "tt": "#tau_{h}#tau_{h}"
    }
    category_dict = {
        "ggh": "ggH",
        "qqh": "VBF",
        "ztt": "Z#rightarrow#tau#tau",
        "zll": "Z#rightarrowll",
        "w": "W+jets",
        "tt": "t#bar{t}",
        "ss": "same sign",
        "misc": "misc",
        "noniso": "noniso"
    }
    split_dict = {"et": 50, "mt": 200, "tt": 20}

    bkg_processes = ["EWK", "QCD", "VV", "W", "TTT", "TTJ", "ZJ", "ZL", "ZTT"]
    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()

    rootfile = rootfile_parser.Rootfile_parser(args.input)

    plots = []

    for channel in args.channels:
        for category in channel_categories[channel]:
            plot = dd.Plot([0.5, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14)
            for process in bkg_processes:
                plot.add_hist(
                    rootfile.get(channel, category, process), process, "bkg")
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict[process])
            for i in range(2):
                plot.subplot(i + 1).add_hist(
                    rootfile.get(channel, category, "ggH"), "ggH")
                plot.subplot(i + 1).add_hist(
                    rootfile.get(channel, category, "ggH"), "ggH_top")
                plot.subplot(i + 1).add_hist(
                    rootfile.get(channel, category, "qqH"), "qqH")
                plot.subplot(i + 1).add_hist(
                    rootfile.get(channel, category, "qqH"), "qqH_top")
            plot.add_hist(
                rootfile.get(channel, category, "data_obs"), "data_obs")
            plot.add_hist(
                rootfile.get(channel, category, "TotalBkg"), "total_bkg")

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
                linecolor=0,
                fillstyle=3001 if args.png else 1001)

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

            plot.create_stack(bkg_processes, "stack")

            plot.subplot(0).setYlims(
                split_dict[channel],
                2 * plot.subplot(0).get_hist("total_bkg").GetMaximum())
            plot.subplot(1).setYlims(0.1, split_dict[channel])
            plot.subplot(2).setYlims(0.75, 1.45)
            if channel == "tt" and category == "qqh":
                plot.subplot(2).setYlims(0.75, 2.15)
            plot.subplot(1).setLogY()
            plot.subplot(2).setXlabel(args.x_label)
            plot.subplot(0).setYlabel("N_{events}")
            plot.subplot(1).setYlabel(
                "")  # otherwise number labels are not drawn on axis
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
                    plot.legend(i).add_entry(0, process,
                                             styles.label_dict[process.replace(
                                                 "EWK", "EWKZ")], 'f')
                plot.legend(i).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
                plot.legend(i).add_entry(1, "ggH%s" % suffix[i], "ggH", 'l')
                plot.legend(i).add_entry(1, "qqH%s" % suffix[i], "qqH", 'l')
                plot.legend(i).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i).setNColumns(3)
            plot.legend(0).Draw()
            plot.legend(1).setAlpha(0.0)
            plot.legend(1).Draw()

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
            plot.DrawLumi("35.9 fb^{-1} (13 TeV)")
            plot.DrawChannelCategoryLabel("%s, %s" % (channel_dict[channel],
                                                      category_dict[category]))

            # save plot
            prefix = "prefit" if "prefit" in args.input else "postfit" if "postfit" in args.input else "undefined"
            plot.save("plots/%s_%s_%s.%s" % (prefix, channel, category, 'png'
                                             if args.png else 'pdf'))
            plots.append(
                plot
            )  # work around to have clean up seg faults only at the end of the script


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("plot_nominal.log", logging.INFO)
    main(args)
