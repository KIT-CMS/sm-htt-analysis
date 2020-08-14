#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser as rootfile_parser
import Dumbledraw.styles as styles
import ROOT

import argparse
import copy

import logging
logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Plot Combined m_sv")
    parser.add_argument("-i",
                        "--input",
                        type=str,
                        required=True,
                        help="ROOT file with shapes of processes")

    parser.add_argument("--combine-backgrounds",
                        action="store_true",
                        help="If set, backgrounds are combined ")
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
    files = []
    # create plot
    width = 600
    plot = dd.Plot([[0.30, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)
    bkg_processes = ["VVL", "TTL", "ZL", "jetFakes", "EMB", "QCD", "W"]
    minor_signals = [
        "ZH125", "ZHWW125", "WH125", "qqHWW125", "WHWW125", "ttH125",
        "ggHWW125"
    ]
    minor_signals = [
        "ZH_htt", "ZH_hww", "WH_htt", "qqH_hww", "WH_hww", "ttH_htt", "ggH_hww"
    ]
    background_mapping = {
        "EMB": ["EMB"],
        "REST": [
            "VVL", "W", "TTL", "ZL", "ZH_htt", "ZH_hww", "WH_htt", "qqH_hww",
            "WH_hww", "ttH_htt", "ggH_hww"
        ],
        "jetFakesCMB": ["QCD", "jetFakes"]
    }
    total_bkg = {}
    total_bkg["all"] = None
    total_bkg["data"] = None
    total_bkg["ggH"] = None
    total_bkg["qqH"] = None
    total_bkg["total_signal"] = None
    if args.combine_backgrounds:
        for process in background_mapping.keys():
            total_bkg[process] = None
    else:
        for process in bkg_processes:
            total_bkg[process] = None

    for channel in ["em", "et", "mt", "tt"]:
        for era in ["2016", "2017", "2018"]:
            # if channel == "et" and era == "2016":
            #     continue
            category = "300"
            files.append(rootfile_parser.Rootfile_parser(args.input))
            if "em" == channel:
                bkg_processes_temp = ["QCD", "VVL", "W", "TTL", "ZL", "EMB"]
            else:
                bkg_processes_temp = ["VVL", "TTL", "ZL", "jetFakes", "EMB"]
            for process in bkg_processes_temp:
                histogram = files[-1].get(era, channel, category, process)
                if not isinstance(histogram, ROOT.TH1):
                    continue
                if total_bkg["all"] is None:
                    total_bkg["all"] = histogram.Clone()
                else:
                    total_bkg["all"].Add(histogram)
                if args.combine_backgrounds:
                    for cmb_background in background_mapping.keys():
                        if process in background_mapping[cmb_background]:
                            logger.debug("Adding {} to {}".format(
                                process, cmb_background))
                            if total_bkg[cmb_background] is None:
                                total_bkg[cmb_background] = histogram.Clone()
                            else:
                                total_bkg[cmb_background].Add(histogram)
                else:
                    if total_bkg[process] is None:
                        total_bkg[process] = histogram.Clone()
                    else:
                        total_bkg[process].Add(histogram)
            if args.combine_backgrounds:
                for process in minor_signals:
                    histogram = files[-1].get(era, channel, category, process)
                    if total_bkg["REST"] is None:
                        total_bkg["REST"] = histogram.Clone()
                    else:
                        total_bkg["REST"].Add(histogram)
            # get data
            if total_bkg["data"] is None:
                total_bkg["data"] = files[-1].get(era, channel, category,
                                                  "data_obs")
            else:
                total_bkg["data"].Add(files[-1].get(era, channel, category,
                                                    "data_obs"))
            # get signal
            for signal in ["ggH", "qqH"]:
                if total_bkg["total_signal"] is None:
                    total_bkg["total_signal"] = files[-1].get(
                        era, channel, category,
                        "{}_htt".format(signal)).Clone()
                else:
                    total_bkg["total_signal"].Add(files[-1].get(
                        era, channel, category, "{}_htt".format(signal)))
                if total_bkg[signal] is None:
                    total_bkg[signal] = files[-1].get(
                        era, channel, category,
                        "{}_htt".format(signal)).Clone()
                else:
                    total_bkg[signal].Add(files[-1].get(
                        era, channel, category, "{}_htt".format(signal)))
    for process in total_bkg.keys():
        if total_bkg[process] is None and process in bkg_processes:
            total_bkg.pop(process)
            bkg_processes.remove(process)
    if args.combine_backgrounds:
        bkg_processes = background_mapping.keys()
    for process in bkg_processes:
        plot.add_hist(total_bkg[process], process, "bkg")
        plot.setGraphStyle(process,
                           "hist",
                           fillcolor=styles.color_dict[process])

    plot.add_hist(total_bkg["all"], "total_bkg")
    plot.setGraphStyle("total_bkg",
                       "e2",
                       markersize=0,
                       fillcolor=styles.color_dict["unc"],
                       linecolor=0)

    plot.add_hist(total_bkg["data"], "data_obs")
    plot.subplot(0).get_hist("data_obs").GetXaxis().SetMaxDigits(4)
    plot.subplot(0).setGraphStyle("data_obs", "e0")
    plot.subplot(0).setGraphStyle("data_obs", "e0")

    plot.subplot(0).setGraphStyle(signal,
                                  "hist",
                                  linecolor=styles.color_dict[signal],
                                  linewidth=3)
    plot.subplot(0).add_hist(total_bkg["total_signal"], "inclusive")
    plot.subplot(0).setGraphStyle("inclusive",
                                  "hist",
                                  fillcolor=styles.color_dict["inclusive"])
    plot.subplot(0).add_hist(total_bkg["total_signal"], "inclusive_line")
    plot.subplot(0).setGraphStyle("inclusive_line",
                                  "hist",
                                  linecolor=styles.color_dict["inclusive"],
                                  linewidth=3)
    stack = bkg_processes + ["inclusive"]

    plot.create_stack(stack, "stack")

    # build ratio
    plot.subplot(1).add_hist(
        plot.subplot(0).get_hist("inclusive"), "inclusive_ratio")
    plot.subplot(1).add_hist(
        plot.subplot(0).get_hist("total_bkg"), "total_bkg_ratio")
    plot.subplot(1).add_hist(
        plot.subplot(0).get_hist("data_obs"), "data_obs_ratio")
    signal = plot.subplot(1).get_hist("inclusive_ratio")
    signal.Add(plot.subplot(1).get_hist("total_bkg_ratio"))
    plot.subplot(1).setGraphStyle("inclusive_ratio",
                                  "hist",
                                  linecolor=styles.color_dict["inclusive"],
                                  linewidth=2)
    plot.subplot(1).setGraphStyle("total_bkg_ratio",
                                  "e2",
                                  markersize=0,
                                  fillcolor=styles.color_dict["unc"],
                                  linecolor=0)
    plot.subplot(1).setGraphStyle("data_obs", "e0")

    plot.subplot(1).normalize(
        ["inclusive_ratio", "total_bkg_ratio", "data_obs_ratio"],
        "total_bkg_ratio")

    # set axes limits and labels
    plot.subplot(0).setYlims(
        0.0, (2.0 * plot.subplot(0).get_hist("data_obs").GetMaximum()))
    plot.subplot(1).setYlims(0.9, 1.29)
    # plot.subplot(0).setXlims(80.0, 180)
    # plot.subplot(1).setXlims(80.0, 180)
    plot.subplot(1).setXlabel("m_{SV}(#tau#tau) (GeV)")

    plot.subplot(0).setYlabel("Events")
    plot.subplot(1).setYlabel("Ratio")

    plot.scaleYLabelSize(0.75)
    plot.scaleXLabelSize(0.75)
    plot.scaleYTitleSize(0.75)
    plot.scaleXTitleSize(0.75)

    procs_to_draw = ["stack", "total_bkg", "data_obs", "inclusive_line"]
    plot.subplot(0).Draw(procs_to_draw)
    plot.subplot(1).Draw(
        ["inclusive_ratio", "total_bkg_ratio", "data_obs_ratio"])
    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()
    plot.add_legend(width=0.65, height=0.20, pos=3)
    for process in legend_bkg_processes:
        plot.legend(0).add_entry(
            0, process,
            styles.legend_label_dict[process.replace("TTL", "TT").replace(
                "VVL", "VV").replace("NLO", "")], 'f')
    plot.legend(0).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
    plot.legend(0).add_entry(0, "inclusive",
                             "qq#rightarrowH + gg#rightarrowH (#mu=0.88)", 'f')
    plot.legend(0).add_entry(0, "inclusive_line",
                             "qq#rightarrowH + gg#rightarrowH (#mu=0.88)", 'l')
    plot.legend(0).add_entry(0, "data_obs", "Observed", 'PE2L')
    plot.legend(0).setNColumns(2)
    plot.legend(0).Draw()

    plot.add_legend(reference_subplot=1, width=0.65, height=0.03, pos=1)
    plot.legend(1).add_entry(1, "total_bkg_ratio", "Bkg. unc.", 'f')
    plot.legend(1).add_entry(1, "inclusive_ratio",
                             "qq#rightarrowH + gg#rightarrowH (#mu=0.88)", 'l')
    plot.legend(1).add_entry(1, "data_obs_ratio", "Observed", 'PE2L')
    plot.legend(1).setNColumns(3)
    plot.legend(1).setAlpha(0.0)
    plot.legend(1).Draw()

    plot.add_line(reference_subplot=1,
                  xmin=80,
                  ymin=1,
                  xmax=180,
                  ymax=1,
                  color=1,
                  linestyle=7)
    plot.line(0).Draw()

    # draw additional labels
    plot.DrawCMS(preliminary=False)
    plot.DrawLumi("137.2 fb^{-1} (13 TeV)", textsize=0.5)

    posChannelCategoryLabelLeft = None
    plot.DrawChannelCategoryLabel(
        "e^{}#mu^{} + e^{}#tau_{h} + #mu^{}#tau_{h} + #tau_{h}^{}#tau_{h}^{} ((ggH + qqH) > 0.80)",
        textsize=0.03)
    subname = "prefit" if "prefit" in args.input else "postfit"
    plot.save("m_sv_plot/plot_{}.png".format(subname))
    plot.save("m_sv_plot/plot_{}.pdf".format(subname))


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("m_sv_plot_shapes.log", logging.CRITICAL)
    main(args)
