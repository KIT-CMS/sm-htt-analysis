#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser as rootfile_parser
import Dumbledraw.styles as styles

import argparse
import copy
import ROOT

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
        "ee": ["m_vis", "d0_e", "dZ_e"],
        "mm": ["m_vis", "d0_m", "dZ_m"],
        "et": ["d0_te", "dZ_te", "d0_t", "dZ_t"],
        "mt": ["d0_tm", "dZ_tm", "d0_t", "dZ_t", "d0_f", "dZ_f", "d0_tt", "dZ_tt"],
        "tt": ["d0_t2", "dZ_t2"]
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
        "d0_e": "#rightarrowe",
        "dZ_e": "#rightarrowe",
        "d0_m": "#rightarrowm",
        "dZ_m": "#rightarrowm",
        "d0_te": "#rightarrow#tau#rightarrowe",
        "dZ_te": "#rightarrow#tau#rightarrowe",
        "d0_tm": "#rightarrow#tau#rightarrowm",
        "dZ_tm": "#rightarrow#tau#rightarrowm",
        "d0_t":  "#rightarrow#tau#rightarrow#tau_{h}",
        "dZ_t":  "#rightarrow#tau#rightarrow#tau_{h}",
        "d0_t2": "#rightarrow#tau#rightarrow#tau_{h}",
        "dZ_t2": "#rightarrow#tau#rightarrow#tau_{h}",
        "d0_f":  "fake#rightarrow#tau_{h}",
        "dZ_f":  "fake#rightarrow#tau_{h}",
        "d0_tt": "fake#rightarrow#tau_{h}",
        "dZ_tt": "fake#rightarrow#tau_{h}",
        "m_vis": "inclusive"
    }
    variable_dict = {
        "d0_e": "d0_1",
        "dZ_e": "dZ_1",
        "d0_m": "d0_1",
        "dZ_m": "dZ_1",
        "d0_te": "d0_1",
        "dZ_te": "dZ_1",
        "d0_tm": "d0_1",
        "dZ_tm": "dZ_1",
        "d0_t":  "d0_2",
        "dZ_t":  "dZ_2",
        "d0_t2": "d0_2",
        "dZ_t2": "dZ_2",
        "d0_f":  "d0_2",
        "dZ_f":  "dZ_2",
        "d0_tt": "d0_2",
        "dZ_tt": "dZ_2",
        "m_vis": "m_vis"
    }
    split_dict = {
        "ee": 10000000,
        "em": 10000000,
        "et": 10,
        "mm": 100000000,
        "mt": 10,
        "tt": 10
    }

    MC_processes = {
        "ee": ["HTT", "EWK", "QCD", "VV", "W", "TT", "ZJ", "ZTT", "ZL"],
        "em": ["HTT", "EWK", "QCD", "VV", "W", "TT", "ZJ", "ZTT", "ZL"],
        "et": ["HTT", "EWK", "QCD", "VV", "W", "TTT", "TTJ", "ZJ", "ZTT", "ZL"],
        "mm": ["HTT", "EWK", "QCD", "VV", "W", "TT", "ZJ", "ZTT", "ZL"],
        "mt": ["HTT", "EWK", "QCD", "VV", "W", "TTT", "TTJ", "ZJ", "ZTT", "ZL"],
        "tt": ["HTT", "EWK", "QCD", "VV", "W", "TTT", "TTJ", "ZJ", "ZTT", "ZL"]
    }
    legend_MC_processes={}
    for channel in args.channels:
        legend_MC_processes[channel] = copy.deepcopy(MC_processes[channel])
        legend_MC_processes[channel].reverse()

    rootfile = ROOT.TFile(args.input, "READ")

    plots = []

    for channel in args.channels:
        for category in channel_categories[channel]:
            plot = dd.Plot([0.5, [0.35, 0.33]], "ModTDR", r=0.04, l=0.14)
            for process in MC_processes[channel]:
                #print "#{channel}#{channel}_{category}#{process}#smhtt#Run2016#{var}#125#".format(channel=channel, category=category, process=process, var=variable_dict[category])
                plot.add_hist(
                    rootfile.Get("#{channel}#{channel}_{category}#{process}#smhtt#Run2016#{var}#125#".format(channel=channel, category=category, process=process, var=variable_dict[category])), process, "MC_single")
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict["ggH" if process == "HTT" else process])
            plot.add_hist(
                rootfile.Get("#{channel}#{channel}_{category}#data_obs#smhtt#Run2016#{var}#125#".format(channel=channel, category=category, var=variable_dict[category])), "data_obs")
            plot.add_hist(
                rootfile.Get("#{channel}#{channel}_{category}#MC#smhtt#Run2016#{var}#125#".format(channel=channel, category=category, var=variable_dict[category])), "MC")
            plot.setGraphStyle(
                "MC", "hist", linecolor=1, linewidth=3)
	    plot.setGraphStyle(
                "data_obs", "e0")

            plot.subplot(2).normalize(["MC", "data_obs"], "data_obs")
            plot.subplot(0).normalizeByBinWidth()
            plot.subplot(1).normalizeByBinWidth()

            plot.create_stack(MC_processes[channel], "stack")

            plot.subplot(0).setYlims(split_dict[channel], 2 * plot.subplot(0).get_hist("MC").GetMaximum())
            #plot.subplot(0).setYlims(10, 10000000)
            plot.subplot(1).setYlims(1.0, split_dict[channel])
            plot.subplot(2).setYlims(0.6, 1.4)
            plot.subplot(2).setXlabel(variable_dict[category])
            plot.subplot(0).setYlabel("N_{events}")
            plot.subplot(1).setYlabel("")
            plot.subplot(2).setYlabel("Ratio to data")

            #plot.scaleXTitleSize(0.8)
            #plot.scaleXLabelSize(0.8)
            plot.scaleYTitleSize(0.9)
            #plot.scaleYLabelSize(0.8)
            #plot.scaleXLabelOffset(2.0)
            plot.scaleYTitleOffset(1.3)
            #plot.setXlims(-0.02, 0.02)
            plot.subplot(1).setLogY()

            #plot.subplot(2).setNYdivisions(3, 5)

            # draw subplots. Argument contains names of objects to be drawn in corresponding order.
            plot.subplot(1).Draw(["stack", "data_obs"])
            plot.subplot(0).Draw(["stack", "data_obs"])
            plot.subplot(2).Draw(["MC", "data_obs"])

            # create legends
            suffix = ["", "_top"]
            plot.add_legend(width=0.48, height=0.15)
            
            label_dict=styles.label_dict
            label_dict["EWK"]="EWKZ"
            label_dict["ZL"]=label_dict["ZL"].replace(" (l#rightarrow#tau_{h})", "")
            label_dict["ZJ"]=label_dict["ZJ"].replace("#tau_{h}", "l")
            for process in legend_MC_processes[channel]:
                plot.legend(0).add_entry(0, process,
                                         styles.label_dict[process.replace(
                                             "EWK", "EWKZ")], 'f')
            plot.legend(0).add_entry(0, "MC", "MC", 'l')
            plot.legend(0).add_entry(0, "data_obs", "Data", 'PE')
            plot.legend(0).setNColumns(3)
            plot.legend(0).Draw()

            # draw additional labels
            plot.DrawCMS()
            plot.DrawLumi("35.9 fb^{-1} (13 TeV)")
            plot.DrawChannelCategoryLabel("%s, %s" % (channel_dict[channel],
                                                      category_dict[category]))

            # save plot
            prefix = "prefit" if "prefit" in args.input else "postfit" if "postfit" in args.input else "undefined"
            plot.save("quantile-method/%s_%s.%s" % (channel, category, 'png'
                                             if args.png else 'pdf'))
            
            # plot zoomed version
            plot.setXlims(-0.02, 0.02)
            plot.scaleYTitleSize(1.0)
            plot.scaleYTitleOffset(1.0)
            plot.subplot(1).Draw(["stack", "data_obs"])
            plot.subplot(0).Draw(["stack", "data_obs"])
            plot.subplot(2).Draw(["MC", "data_obs"])
            plot.legend(0).Draw()
            plot.DrawCMS()
            plot.DrawLumi("35.9 fb^{-1} (13 TeV)")
            plot.DrawChannelCategoryLabel("%s, %s" % (channel_dict[channel],
                                                      category_dict[category]))
            plot.save("quantile-method/zoom_%s_%s.%s" % (channel, category, 'png'
                                             if args.png else 'pdf'))
            
            plots.append(
                plot
            )  # work around to have clean up seg faults only at the end of the script


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("plot_nominal.log", logging.INFO)
    main(args)
