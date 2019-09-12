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
    parser.add_argument("-o", "--outputfolder", type=str, required=True, help="...yourself")
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
        "--categories",
        type=str,
        required=True,
        help="Select categorization.")
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
        "--train-emb",
        type=lambda x:bool(distutils.util.strtobool(x)),
        default=True,
        help="Use fake factor training category")
    parser.add_argument(
        "--train-ff",
        type=lambda x:bool(distutils.util.strtobool(x)),
        default=True,
        help="Use fake factor training category")
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
    stxs_stage1p1_cats = [str(100+i) for i in range(4)] + [str(200+i) for i in range(4)]
    print(args)
    if args.gof_variable != None:
        channel_categories = {
            "et": ["300"],
            "mt": ["300"],
            "tt": ["300"],
            "em": ["300"]
        }
    else:
        channel_categories = {
            #"et": ["ztt", "zll", "w", "tt", "ss", "misc"],
            "et": ["12", "15", "11", "13", "14", "16"],
            #"mt": ["ztt", "zll", "w", "tt", "ss", "misc"],
            "mt": ["12", "15", "11", "13", "14", "16"],
            #"tt": ["ztt", "noniso", "misc"]
            "tt": ["12", "17", "16"],
            #"em": ["ztt", "tt", "ss", "misc", "db"]
            "em": ["12", "13", "14", "16", "19"]
        }
        if args.train_emb: #swap ztt for embedding
            for chn in ["em","mt","et","tt"]:
                channel_categories[chn].remove("12")
                channel_categories[chn].append("20")
        if args.train_ff:
            for chn in ["mt","et","tt"]: # no change for em
                if chn == "tt":
                    channel_categories[chn].remove("17")
                else:
                    channel_categories[chn].remove("11")
                    channel_categories[chn].remove("14")
                channel_categories[chn].append("21") # add ff
        if args.categories == "stxs_stage0":
            for channel in ["et", "mt", "tt", "em"]:
                channel_categories[channel] += ["1", "2"]
        elif args.categories == "stxs_stage1p1":
            for channel in ["et", "mt", "tt", "em"]:
                channel_categories[channel] += stxs_stage1p1_cats
        elif args.categories == "backgrounds":
            pass
        else:
            logger.critical("Selected unkown STXS categorization {}",
                            args.categories)
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
        category_dict = {"300": "inclusive"}
    else:
        category_dict = {
            "1": "ggh",
            "100": "ggh 0-jet",
            "101": "ggh 1-jet p_{T}^{H} [0,120]",
            "102": "ggh 1-jet p_{T}^{H} [120,#infty]",
            "103": "ggh #geq 2-jet",
            "2": "qqh",
            "200": "qqh #leq 1-jet",
            "201": "qqh #geq 2-jet m_{jj} [0,350]",
            "202": "qqh #geq 2-jet m_{jj} [350,#infty] p_{T}^{H} [0,200]",
            "203": "qqh #geq 2-jet m_{jj} [350,#infty] p_{T}^{H} [200,#infty]",
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
    if args.linear == True:
        split_value = 0
    else:
        if args.normalize_by_bin_width:
            split_value = 10001
        else:
            split_value = 101

    split_dict = {c: split_value for c in ["et", "mt", "tt", "em"]}

    bkg_processes = [
        "VVL", "TTL", "ZL", "jetFakes", "EMB"
    ]
    if not args.fake_factor and args.embedding:
        bkg_processes = [
            "QCD", "VVJ", "W", "TTJ", "ZJ", "ZL", "EMB"
        ]
    if not args.embedding and args.fake_factor:
        bkg_processes = [
            "VVT", "VVJ", "TTT", "TTJ", "ZJ", "ZL", "jetFakes", "ZTT"
        ]
    if not args.embedding and not args.fake_factor:
        bkg_processes = [
            "QCD", "VVT", "VVL", "VVJ", "W", "TTT", "TTL", "TTJ", "ZJ", "ZL", "ZTT"
        ]
    all_bkg_processes = [b for b in bkg_processes]
    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()

    if "2016" in args.era:
        era = "Run2016"
    elif "2017" in args.era:
        era = "Run2017"
    elif "2018" in args.era:
        era = "Run2018"
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception
    print(channel_categories)
    plots = []
    for channel in args.channels:
        for category in channel_categories[channel]:
            print "Plot for category: ",category
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
            if args.linear == True:
                plot = dd.Plot(
                    [0.3, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)
            else:
                plot = dd.Plot(
                    [0.5, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)

            # get background histograms
            for process in bkg_processes:
                try:
                    plot.add_hist(
                        rootfile.get(era, channel, category, process), process, "bkg")
                    plot.setGraphStyle(
                        process, "hist", fillcolor=styles.color_dict[process])
                except:
                    pass

            # get signal histograms
            plot_idx_to_add_signal = [0,2] if args.linear else [1,2]
            for i in plot_idx_to_add_signal:
                try:
                    plot.subplot(i).add_hist(
                        rootfile.get(era, channel, category, "ggH"), "ggH")
                    plot.subplot(i).add_hist(
                        rootfile.get(era, channel, category, "ggH"), "ggH_top")
                    plot.subplot(i).add_hist(
                        rootfile.get(era, channel, category, "qqH"), "qqH")
                    plot.subplot(i).add_hist(
                        rootfile.get(era, channel, category, "qqH"), "qqH_top")
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

                    HWWhist = rootfile.get(era, channel, category, "ggHWW125")
                    if isinstance(rootfile.get(era, channel, category, "ggHWW125"), ROOT.TH1):
                        HWWhist = rootfile.get(era, channel, category, "ggHWW125").Clone("ggHWW125")
                    qqHWWhist = rootfile.get(era, channel, category, "qqHWW125")
                    if isinstance(qqHWWhist,ROOT.TH1) and HWWhist:
                        HWWhist.Add(qqHWWhist)
                    elif qqHWWhist:
                        HWWhist = qqHWWhist
                    plot.subplot(i).add_hist(HWWhist, "HWW")
                    plot.subplot(i).add_hist(HWWhist, "HWW_top")
                except:
                    pass

            # get observed data and total background histograms
            # NOTE: With CMSSW_8_1_0 the TotalBkg definition has changed.
            print("plot.add_hist(rootfile.get("+era+", "+channel+", "+category+', "data_obs")')
            plot.add_hist(
                rootfile.get(era, channel, category, "data_obs"), "data_obs")
            total_bkg = rootfile.get(era, channel, category, "TotalBkg")
            ggHHist = rootfile.get(era, channel, category, "ggH")
            qqHHist = rootfile.get(era, channel, category, "qqH")
            total_bkg.Add(ggHHist, -1)
            if qqHHist:
                total_bkg.Add(qqHHist, -1)
            plot.add_hist(total_bkg, "total_bkg")

            plot.subplot(0).setGraphStyle("data_obs", "e0")
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                "ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
            plot.subplot(0 if args.linear else 1).setGraphStyle("ggH_top", "hist", linecolor=0)
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                "qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
            plot.subplot(0 if args.linear else 1).setGraphStyle("qqH_top", "hist", linecolor=0)
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                "VH", "hist", linecolor=styles.color_dict["VH"], linewidth=3)
            plot.subplot(0 if args.linear else 1).setGraphStyle("VH_top", "hist", linecolor=0)
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                "ttH", "hist", linecolor=styles.color_dict["ttH"], linewidth=3)
            plot.subplot(0 if args.linear else 1).setGraphStyle("ttH_top", "hist", linecolor=0)
            plot.subplot(0 if args.linear else 1).setGraphStyle(
                "HWW", "hist", linecolor=styles.color_dict["HWW"], linewidth=3)
            plot.subplot(0 if args.linear else 1).setGraphStyle("HWW_top", "hist", linecolor=0)
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
            if bkg_qqH:
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

            plot.subplot(2).setYlims(0.45, 2.05)
            if category in ["1", "2"] + stxs_stage1p1_cats:
                plot.subplot(0).setLogY()
                plot.subplot(0).setYlims(0.1, 150000000)
                if channel == "em":
                    plot.subplot(0).setYlims(1, 150000000)

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
                plot.subplot(2).setXlabel("NN output")
            if args.normalize_by_bin_width:
                plot.subplot(0).setYlabel("dN/d(NN output)")
            else:
                plot.subplot(0).setYlabel("N_{events}")

            plot.subplot(2).setYlabel("")

            #plot.scaleXTitleSize(0.8)
            #plot.scaleXLabelSize(0.8)
            #plot.scaleYTitleSize(0.8)
            plot.scaleYLabelSize(0.8)
            #plot.scaleXLabelOffset(2.0)
            plot.scaleYTitleOffset(1.1)

            #plot.subplot(2).setNYdivisions(3, 5)

            #if not channel == "tt" and category in ["11", "12", "13", "14", "15", "16"]:
            #    plot.subplot(2).changeXLabels(["0.2", "0.4", "0.6", "0.8", "1.0"])

            # draw subplots. Argument contains names of objects to be drawn in corresponding order.
            procs_to_draw = ["stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top", "VH", "VH_top", "ttH", "ttH_top", "HWW", "HWW_top", "data_obs"] if args.linear else ["stack", "total_bkg", "data_obs"]
            plot.subplot(0).Draw(procs_to_draw)
            if args.linear != True:
                plot.subplot(1).Draw([
                    "stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top",
                    "VH", "VH_top", "ttH", "ttH_top", "HWW", "HWW_top", "data_obs"
                ])
            plot.subplot(2).Draw([
                "total_bkg", "bkg_ggH", "bkg_ggH_top", "bkg_qqH",
                "bkg_qqH_top", "data_obs"
            ])

            # create legends
            suffix = ["", "_top"]
            for i in range(2):

                plot.add_legend(width=0.6, height=0.15)
                for process in legend_bkg_processes:
                    try:
                        plot.legend(i).add_entry(
                            0, process, styles.legend_label_dict[process.replace("TTL", "TT").replace("VVL", "VV")], 'f')
                    except:
                        pass
                plot.legend(i).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
                plot.legend(i).add_entry(0 if args.linear else 1, "ggH%s" % suffix[i], "gg#rightarrowH", 'l')
                plot.legend(i).add_entry(0 if args.linear else 1, "qqH%s" % suffix[i], "qq#rightarrowH", 'l')
                plot.legend(i).add_entry(0 if args.linear else 1, "VH%s" % suffix[i], "qq#rightarrowVH", 'l')
                try:
                    plot.legend(i).add_entry(0 if args.linear else 1, "ttH%s" % suffix[i], "ttH", 'l')
                    plot.legend(i).add_entry(0 if args.linear else 1, "HWW%s" % suffix[i], "H#rightarrowWW", 'l')
                except:
                    pass
                plot.legend(i).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i).setNColumns(3)
            plot.legend(0).Draw()
            plot.legend(1).setAlpha(0.0)
            plot.legend(1).Draw()

            if args.chi2test:
                import ROOT as r
                f = r.TFile(args.input, "read")
                background = f.Get("htt_{}_{}_Run{}_{}/TotalBkg".format(
                    channel, category, args.era, "prefit"
                    if "prefit" in args.input else "postfit"))
                data = f.Get("htt_{}_{}_Run{}_{}/data_obs".format(
                    channel, category, args.era, "prefit"
                    if "prefit" in args.input else "postfit"))
                chi2 = data.Chi2Test(background, "UW CHI2/NDF")
                plot.DrawText(0.7, 0.3,
                              "\chi^{2}/ndf = " + str(round(chi2, 3)))

            for i in range(2):
                plot.add_legend(
                    reference_subplot=2, pos=1, width=0.5, height=0.03)
                plot.legend(i + 2).add_entry(0, "data_obs", "Data", 'PE')
                plot.legend(i + 2).add_entry(0 if args.linear else 1, "ggH%s" % suffix[i],
                                             "ggH+bkg.", 'l')
                plot.legend(i + 2).add_entry(0 if args.linear else 1, "qqH%s" % suffix[i],
                                             "qqH+bkg.", 'l')
                plot.legend(i + 2).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
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
                "%s, %s" % (channel_dict[channel], category_dict[category]),
                begin_left=None)

            # save plot
            postfix = "prefit" if "prefit" in args.input else "postfit" if "postfit" in args.input else "undefined"
            plot.save("%s/%s_%s_%s_%s.%s" % (args.outputfolder, args.era, channel, args.gof_variable if args.gof_variable is not None else category, postfix, "png" if args.png else "pdf"))
            plots.append(
                plot
            )  # work around to have clean up seg faults only at the end of the script


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_plot_shapes.log".format(args.era), logging.INFO)
    main(args)

