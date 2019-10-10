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
    parser = argparse.ArgumentParser(description="Plot categories using Dumbledraw from shapes produced by shape-producer module.")
    parser.add_argument("-e", "--era", type=str, required=True, help="Era")
    parser.add_argument("-v", "--variable", type=str, required=True, help="Variable used as final discriminator")
    parser.add_argument("-i", "--input", type=str, required=True, help="ROOT file with shapes of processes")
    parser.add_argument("-t", "--shape-type", type=str, required=True, choices=['prefit','postfit'], help="Type of shapes to consider")
    parser.add_argument("--normalize-by-bin-width", action="store_true", help="Normelize plots by bin width")
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
        "em": "e#mu",
        "et": "e#tau_{h}",
        "mt": "#mu#tau_{h}",
        "tt": "#tau_{h}#tau_{h}"
    }
    signal_categories = {
        "2": "#leq 1 jet p_{T}^{H} [200,#infty)",
        "3": "0 jet p_{T}^{H} [0,200)",
        "4": "1 jet p_{T}^{H} [0,120)",
        "5": "1 jet p_{T}^{H} [120,200)",
        "6": "#geq 2 jet m_{jj} [0,350)",
        "7": "#geq 2 jet m_{jj} [350,#infty) p_{T}^{H} [0,200)",
        "8": "#geq 2 jet m_{jj} [350,#infty) p_{T}^{H} [200,#infty)",
    }
    category_dict = {
        "em": signal_categories.copy(),
        "et": signal_categories.copy(),
        "mt": signal_categories.copy(),
        "tt": signal_categories.copy(),
    }
    category_dict["em"].update({"1" : "t#bar{t} control"})
    category_dict["et"].update({"1" : "W + jets control"})
    category_dict["mt"].update({"1" : "W + jets control"})

    bkg_processes = ["VVL", "TTL", "ZL", "jetFakes", "EMB"]
    bkg_processes_em = ["VVL", "TTL", "ZL", "W", "QCD", "EMB"]

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
    for channel in sorted(channel_dict):
        for category in sorted(category_dict[channel]):
            print "channel, category",channel,category

            rootfile = rootfile_parser.Rootfile_parser(args.input)
            rootfile._type = args.shape_type
            if channel == "em":
                bkgs = bkg_processes_em
            else:
                bkgs = bkg_processes
            legend_bkg_processes = copy.deepcopy(bkgs)
            legend_bkg_processes.reverse()

            # create plot
            width = 600
            plot = dd.Plot([0.3, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)
            print "plot created"

            # get background histograms
            for process in bkgs:
                try:
                    bg = rootfile.get(era, channel, category, process)
                    if isinstance(bg,ROOT.TH1):
                        plot.add_hist(bg, process, "bkg")
                        plot.setGraphStyle(process, "hist", fillcolor=styles.color_dict[process])
                except:
                    pass
            print "got bgs"

            # get signal histograms
            plot_idx_to_add_signal = [0,2]
            for i in plot_idx_to_add_signal:
                try:
                    plot.subplot(i).add_hist(rootfile.get(era, channel, category, "ggH125"), "ggH")
                    plot.subplot(i).add_hist(rootfile.get(era, channel, category, "ggH125"), "ggH_top")
                    plot.subplot(i).add_hist(rootfile.get(era, channel, category, "qqH125"), "qqH")
                    plot.subplot(i).add_hist(rootfile.get(era, channel, category, "qqH125"), "qqH_top")
                    if isinstance(rootfile.get(era, channel, category, "ZH125"), ROOT.TH1):
                        VHhist = rootfile.get(era, channel, category, "ZH125").Clone("VH")
                    WHhist = rootfile.get(era, channel, category, "WH125")
                    if isinstance(WHhist,ROOT.TH1) and VHhist:
                        VHhist.Add(WHhist)
                    elif WHhist:
                        VHhist = WHhist
                    plot.subplot(i).add_hist(VHhist, "VH")
                    plot.subplot(i).add_hist(VHhist, "VH_top")

                    if isinstance(rootfile.get(era, channel, category, "ttH125"), ROOT.TH1):
                        plot.subplot(i).add_hist(rootfile.get(era, channel, category, "ttH125"), "ttH")
                        plot.subplot(i).add_hist(rootfile.get(era, channel, category, "ttH125"), "ttH_top")

                    ggHWWhist = rootfile.get(era, channel, category, "ggHWW125")
                    qqHWWhist = rootfile.get(era, channel, category, "qqHWW125")
                    if isinstance(ggHWWhist, ROOT.TH1):
                        HWWhist = rootfile.get(era, channel, category, "ggHWW125").Clone("ggHWW125")
                    if isinstance(qqHWWhist,ROOT.TH1) and isinstance(HWWhist,ROOT.TH1):
                        HWWhist.Add(qqHWWhist)
                    elif isinstance(qqHWWhist,ROOT.TH1):
                        HWWhist = qqHWWhist
                    if isinstance(HWWhist,ROOT.TH1):
                        plot.subplot(i).add_hist(HWWhist, "HWW")
                        plot.subplot(i).add_hist(HWWhist, "HWW_top")
                except:
                    pass
            print "got signals"

            # get observed data and total background histograms
            plot.add_hist(rootfile.get(era, channel, category, "data_obs"), "data_obs")
            total_bkg = rootfile.get(era, channel, category, "TotalBkg")
            ggHHist = rootfile.get(era, channel, category, "ggH125")
            qqHHist = rootfile.get(era, channel, category, "qqH125")
            plot.add_hist(total_bkg, "total_bkg")

            plot.subplot(0).setGraphStyle("data_obs", "e0")
            plot.subplot(0).setGraphStyle("ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
            plot.subplot(0).setGraphStyle("ggH_top", "hist", linecolor=0)
            plot.subplot(0).setGraphStyle("qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
            plot.subplot(0).setGraphStyle("qqH_top", "hist", linecolor=0)
            plot.subplot(0).setGraphStyle("VH", "hist", linecolor=styles.color_dict["VH"], linewidth=3)
            plot.subplot(0).setGraphStyle("VH_top", "hist", linecolor=0)
            plot.subplot(0).setGraphStyle("ttH", "hist", linecolor=styles.color_dict["ttH"], linewidth=3)
            plot.subplot(0).setGraphStyle("ttH_top", "hist", linecolor=0)
            plot.subplot(0).setGraphStyle("HWW", "hist", linecolor=styles.color_dict["HWW"], linewidth=3)
            plot.subplot(0).setGraphStyle("HWW_top", "hist", linecolor=0)
            plot.setGraphStyle("total_bkg", "e2", markersize=0, fillcolor=styles.color_dict["unc"], linecolor=0)
            print "data + signal bg"

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
            plot.subplot(2).setGraphStyle("bkg_ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
            plot.subplot(2).setGraphStyle("bkg_ggH_top", "hist", linecolor=0)
            plot.subplot(2).setGraphStyle("bkg_qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
            plot.subplot(2).setGraphStyle("bkg_qqH_top", "hist", linecolor=0)
            plot.subplot(2).normalize([ "total_bkg", "bkg_ggH", "bkg_ggH_top", "bkg_qqH", "bkg_qqH_top", "data_obs"], "total_bkg")
            print "made ratio"

            # stack background processes
            plot.create_stack(bkgs, "stack")
            print "created stack"

            # normalize stacks by bin-width
            if args.normalize_by_bin_width:
                plot.subplot(0).normalizeByBinWidth()
                plot.subplot(1).normalizeByBinWidth()
            print "normalized by bin width"

            # set axes limits and labels
            plot.subplot(0).setYlims(0.0, 2 * plot.subplot(0).get_hist("total_bkg").GetMaximum())
            plot.subplot(2).setYlims(0.45, 2.05)
            plot.subplot(2).setXlabel(styles.x_label_dict[channel][args.variable])
            if args.normalize_by_bin_width:
                plot.subplot(0).setYlabel("dN/d(%s)"%styles.x_label_dict[channel][args.variable])
            else:
                plot.subplot(0).setYlabel("N_{events}")

            plot.subplot(2).setYlabel("")
            plot.scaleYLabelSize(0.8)
            plot.scaleYTitleOffset(1.1)
            print "labels & limits"

            # draw subplots. Argument contains names of objects to be drawn in corresponding order.
            procs_to_draw = ["stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top", "VH", "VH_top", "ttH", "ttH_top", "HWW", "HWW_top", "data_obs"]
            plot.subplot(0).Draw(procs_to_draw)
            plot.subplot(2).Draw(["total_bkg", "bkg_ggH", "bkg_ggH_top", "bkg_qqH", "bkg_qqH_top", "data_obs"])
            print "hists drawn"

            # create legends
            suffix = ["", "_top"]
            for i in range(2):

                plot.add_legend(width=0.6, height=0.15)
                for process in legend_bkg_processes:
                    try:
                        plot.legend(i).add_entry(0, process, styles.legend_label_dict[process.replace("TTL", "TT").replace("VVL", "VV")], 'f')
                    except:
                        pass
                plot.legend(i).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
                plot.legend(i).add_entry(0, "ggH%s" % suffix[i], "gg#rightarrowH", 'l')
                plot.legend(i).add_entry(0, "qqH%s" % suffix[i], "qq#rightarrowH", 'l')
                plot.legend(i).add_entry(0, "VH%s" % suffix[i], "qq#rightarrowVH", 'l')
                try:
                    plot.legend(i).add_entry(0, "ttH%s" % suffix[i], "ttH", 'l')
                    plot.legend(i).add_entry(0, "HWW%s" % suffix[i], "H#rightarrowWW", 'l')
                except:
                    pass
                plot.legend(i).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i).setNColumns(3)
            plot.legend(0).Draw()
            plot.legend(1).setAlpha(0.0)
            plot.legend(1).Draw()

            for i in range(2):
                plot.add_legend(
                    reference_subplot=2, pos=1, width=0.5, height=0.03)
                plot.legend(i + 2).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i + 2).add_entry(0, "ggH%s" % suffix[i], "ggH+bkg.", 'l')
                plot.legend(i + 2).add_entry(0, "qqH%s" % suffix[i], "qqH+bkg.", 'l')
                plot.legend(i + 2).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
                plot.legend(i + 2).setNColumns(4)
            plot.legend(2).Draw()
            plot.legend(3).setAlpha(0.0)
            plot.legend(3).Draw()
            print "legends created"

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

            plot.DrawChannelCategoryLabel("%s, %s" % (channel_dict[channel], category_dict[channel][category]), begin_left=None)
            print "additional labes drawn"

            # save plot
            postfix = args.shape_type
            plot.save("%s_plots_cutbased/%s_%s_%s_%s.%s" % (args.era, args.era, channel, category, postfix, "pdf"))
            plot.save("%s_plots_cutbased/%s_%s_%s_%s.%s" % (args.era, args.era, channel, category, postfix, "png"))
            plots.append(plot)  # work around to have clean up seg faults only at the end of the script


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_plot_shapes_cutbased.log".format(args.era), logging.INFO)
    main(args)

