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
        "et": ["0jet", "boosted", "vbf"],
        "mt": ["0jet", "boosted", "vbf"],
        "tt": ["0jet", "boosted", "vbf"]
    }
    channel_dict = {
        "ee": "ee",
        "em": "e#mu",
        "et": "e#tau_{h}",
        "mm": "#mu#mu",
        "mt": "#mu#tau_{h}",
        "tt": "#tau_{h}#tau_{h}"
    }
    category_dict = {"0jet": "0 Jet", "boosted": "Boosted", "vbf": "VBF"}

    bkg_processes = ["EWK", "QCD", "VV", "W", "TTT", "TTJ", "ZJ", "ZL", "ZTT"]
    sig_processes = ["ggH", "qqH"]
    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()

    rootfile = rootfile_parser.Rootfile_parser(args.input)

    plots = []

    for channel in args.channels:
        for category in channel_categories[channel]:
            plot = dd.Plot(
                [], "ModTDR", r=0.04, l=0.14, width=1200, height=600)

            for process in bkg_processes:
                plot.add_hist(
                    rootfile.get(channel, category, process), process)
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict[process])

            for process in sig_processes:
                plot.add_hist(
                    rootfile.get(channel, category, process), process)
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict[process])
                plot.add_hist(
                    rootfile.get(channel, category, process),
                    process + "_line")
                plot.setGraphStyle(
                    process + "_line",
                    "hist",
                    linecolor=styles.color_dict[process],
                    linewidth=3)

            plot.add_hist(
                rootfile.get(channel, category, "data_obs"), "data_obs")

            plot.add_hist(
                rootfile.get(channel, category, "TotalBkg"), "total_bkg")
            plot.setGraphStyle(
                "total_bkg",
                "e2",
                markersize=0,
                fillcolor=styles.color_dict["unc"],
                linecolor=0,
                fillstyle=3001 if args.png else 1001)

            plot.create_stack(bkg_processes + sig_processes, "stack")

            plot.subplot(0).setYlims(
                0.1, 10 * plot.subplot(0).get_hist("total_bkg").GetMaximum())
            plot.subplot(0).setXlabel(args.x_label)
            plot.subplot(0).setYlabel("N_{events}")
            plot.subplot(0).setLogY()
            plot.subplot(0).Draw(
                ["stack", "qqH_line", "ggH_line", "total_bkg", "data_obs"])

            plot.DrawCMS()
            plot.DrawLumi("35.9 fb^{-1} (13 TeV)")
            plot.DrawChannelCategoryLabel("%s, %s" % (channel_dict[channel],
                                                      category_dict[category]))

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
