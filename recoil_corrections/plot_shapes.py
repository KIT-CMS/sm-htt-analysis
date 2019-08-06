#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser as rootfile_parser
import Dumbledraw.styles as styles
import ROOT

import argparse
import copy
import yaml

import logging
logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        ""
    )
    parser.add_argument("-e", "--era", type=str, required=True, help="Era")
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        required=True,
        help="Directory of root files with shapes of processes")
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
    channel_dict = {
        "mm": "#mu#mu",
    }
    category_dict = {
        "mm_0jet": "0-jet",
        "mm_1jet": "1-jet",
        "mm_ge2jet": "#geq 2-jet",
    }
    processes = [
        "QCD", "VVT", "VVL", "W", "TTT", "TTL", "ZTT", "ZL"
    ]
    legend_processes = copy.deepcopy(processes)
    legend_processes.reverse()

    if "2016" in args.era:
        era = "Run2016"
    elif "2017" in args.era:
        era = "Run2017"
    elif "2018" in args.era:
        era = "Run2018"
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    plots = []
    for plottype in ["prefit", "postfit"]:
        for category in category_dict:
            filename = args.input_dir+ "/" + category + "/postfit_shapes.root"
            rootfile = rootfile_parser.Rootfile_parser(filename)
            rootfile._hist_hash = "{category}{plottype}/{process}"
            rootfile._type = plottype

            # create plot
            width = 600
            plot = dd.Plot(
                [0.3, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)

            # get background histograms
            print "Getting shapes"
            for process in processes:
                plot.add_hist(
                    rootfile.get(era, "mm", category, process), process, "procs")
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict[process])
            print "Finished getting shapes"


            # get observed data and total processes histograms
            plot.add_hist(rootfile.get(era, "mm", category, "data_obs"), "data_obs")
            plot.add_hist(rootfile.get(era, "mm", category, "TotalProcs"), "total_procs")

            plot.subplot(0).setGraphStyle("data_obs", "e0")
            plot.setGraphStyle(
                "total_procs",
                "e2",
                markersize=0,
                fillcolor=styles.color_dict["unc"],
                linecolor=0)

            # assemble ratio
            plot.subplot(2).normalize(["data_obs"], "total_procs")

            # stack background processes
            plot.create_stack(processes, "stack")

            # set axes limits and labels
            plot.subplot(0).setYlims(1.0, float(10**10))
            plot.subplot(2).setYlims(0.45, 2.05)
            plot.subplot(0).setLogY()
            plot.subplot(2).setXlabel("MET #parallel Z")
            plot.subplot(0).setYlabel("N_{events}")
            plot.subplot(2).setYlabel("")
            #plot.scaleXTitleSize(0.8)
            #plot.scaleXLabelSize(0.8)
            #plot.scaleYTitleSize(0.8)
            plot.scaleYLabelSize(0.8)
            #plot.scaleXLabelOffset(2.0)
            plot.scaleYTitleOffset(1.1)

            # draw subplots. Argument contains names of objects to be drawn in corresponding order.
            procs_to_draw = ["stack", "total_procs", "data_obs"]
            plot.subplot(0).Draw(procs_to_draw)
            plot.subplot(2).Draw(["total_procs", "data_obs"])

            # create legends
            for i in range(2):
                plot.add_legend(width=0.6, height=0.15)
                for process in legend_processes:
                    plot.legend(i).add_entry(
                        0, process, styles.legend_label_dict[process.replace("TTL", "TT").replace("VVL", "VV")], 'f')
                plot.legend(i).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i).add_entry(0, "total_procs", "Total unc.", 'f')
                plot.legend(i).setNColumns(3)
            plot.legend(0).Draw()
            plot.legend(1).setAlpha(0.0)
            plot.legend(1).Draw()
            for i in range(2):
                plot.add_legend(reference_subplot=2, pos=1, width=0.5, height=0.03)
                plot.legend(i + 2).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i + 2).add_entry(0, "total_procs", "Total unc.", 'f')
                plot.legend(i + 2).setNColumns(4)
            plot.legend(2).Draw()
            plot.legend(3).setAlpha(0.0)
            plot.legend(3).Draw()

            # draw additional labels
            plot.DrawCMS()
            if "2016" in args.era:
                plot.DrawLumi("35.9 fb^{-1} (2016, 13 TeV)")
            elif "2017" in args.era:
                plot.DrawLumi("41.5 fb^{-1} (2017, 13 TeV)")
            elif "2018" in args.era:
                plot.DrawLumi("59.7 fb^{-1} (2018, 13 TeV)")
            else:
                logger.critical("Era {} is not implemented.".format(args.era))
                raise Exception

            plot.DrawChannelCategoryLabel(
                "%s, %s" % (channel_dict["mm"], category_dict[category]),
                begin_left=None)

            # save plot
            plot.save("%s_plots_metrecoilfit/%s_%s_%s_%s.%s" % (args.era, args.era, "mm", category, plottype, "png"))
            plot.save("%s_plots_metrecoilfit/%s_%s_%s_%s.%s" % (args.era, args.era, "mm", category, plottype, "pdf"))
            plots.append(plot)  # work around to have clean up seg faults only at the end of the script


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_prefit_postfit_shapes_recoil.log".format(args.era), logging.INFO)
    main(args)

