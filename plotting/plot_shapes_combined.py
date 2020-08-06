#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser as rootfile_parser
import Dumbledraw.styles as styles
import ROOT
import numpy as np

import argparse
import distutils.util
import logging
import json
import collections
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
                        help="...folder where the plots are saved to ")
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
    parser.add_argument(
        "--exact-signals",
        action="store_true",
        help=
        "if set, the stxs_stage1 signal is used for the plot instead of the inclusive signal"
    )
    parser.add_argument(
        "--combine-backgrounds",
        action="store_true",
        help=
        "if set, all backgrounds are combined into 3 bg categories (embedding, jetfakes, rest)"
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


signal_labels = {
    "inclusive": {
        "style": "inclusive",
        "label": "gg#rightarrowH + qq#rightarrowH (#mu=0.88)"
    },
    "ggH": {
        "style": "ggH",
        "label": "gg#rightarrowH (#mu=0.98)"
    },
    "ggH_hww": {
        "style": "ggH",
        "label": "gg#rightarrowH"
    },
    "qqH": {
        "style": "qqH",
        "label": "qq#rightarrowH (#mu=0.79)"
    },
    "qqH_hww": {
        "style": "qqH",
        "label": "qq#rightarrowH"
    },
    "VH": {
        "style": "VH",
        "label": "qq#rightarrowVH"
    },
    "ttH": {
        "style": "ttH",
        "label": "ttH"
    },
    "HWW": {
        "style": "HWW",
        "label": "H#rightarrowWW"
    }
}

mu_dict = {
    "200": "-1.27",
    "201": "1.35",
    "202": "1.26",
    "203": "0.12",
    "100": "-1.14",
    "101": "-0.44",
    "102": "1.74",
    "103": "2.77",
    "104": "2.11",
    "105": "1.33",
    "106": "1.33",
    "107": "1.33",
    "108": "1.8",
    "109": "2.56",
    "110": "1.33",
    "111": "1.33"
}


def get_signal_for_category(category):
    category_mapping = {
        "100": {
            "style": "inclusive",
            "displayname": "gg#rightarrowH 0-jet, p_{T}^{H} [0,10]",
            "signals": ["ggH_0J_PTH_0_10_htt"]
        },
        "101": {
            "style": "inclusive",
            "displayname": "gg#rightarrowH 0-jet, p_{T}^{H} > 10",
            "signals": ["ggH_0J_PTH_GT10_htt"]
        },
        "102": {
            "style": "inclusive",
            "displayname": "gg#rightarrowH 1-jet, p_{T}^{H} [0,60]",
            "signals": ["ggH_1J_PTH_0_60_htt"]
        },
        "103": {
            "style": "inclusive",
            "displayname": "gg#rightarrowH 1-jet, p_{T}^{H} [60,120]",
            "signals": ["ggH_1J_PTH_60_120_htt"]
        },
        "104": {
            "style": "inclusive",
            "displayname": "gg#rightarrowH 1-jet, p_{T}^{H} [120,200]",
            "signals": ["ggH_1J_PTH_120_200_htt"]
        },
        "105": {
            "style": "inclusive",
            "displayname": "gg#rightarrowH 2-jet, mjj [0,350], p_{T}^{H} [0,60]",
            "signals": ["ggH_GE2J_MJJ_0_350_PTH_0_60_htt"]
        },
        "106": {
            "style": "inclusive",
            "displayname": "gg#rightarrowH 2-jet, mjj [0,350], p_{T}^{H} [60,120]",
            "signals": ["ggH_GE2J_MJJ_0_350_PTH_60_120_htt"]
        },
        "107": {
            "style": "inclusive",
            "displayname": "gg#rightarrowH 2-jet, mjj [0,350], p_{T}^{H} [120,200]",
            "signals": ["ggH_GE2J_MJJ_0_350_PTH_120_200_htt"]
        },
        "108": {
            "style": "inclusive",
            "displayname": "gg#rightarrowH p_{T}^{H} [200,300]",
            "signals": ["ggH_PTH_200_300_htt"]
        },
        "109": {
            "style":
            "inclusive",
            "displayname":
            "gg#rightarrowH p_{T}^{H} > 300",
            "signals": [
                "ggH_PTH_300_450_htt", "ggH_PTH_450_650_htt",
                "ggH_PTH_GT650_htt"
            ]
        },
        "110": {
            "style":
            "inclusive",
            "displayname":
            "gg#rightarrowH 2-jet, mjj > 350, p_{T}^{H} [0,200]",
            "signals": [
                "ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_htt",
                "ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_htt",
                "ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_htt",
                "ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_htt"
            ]
        },
        "200": {
            "style":
            "inclusive",
            "displayname":
            "qq#rightarrowH 2-jet low mjj",
            "signals": [
                "qqH_FWDH_htt", "qqH_0J_htt", "qqH_1J_htt",
                "qqH_GE2J_MJJ_0_60_htt", "qqH_GE2J_MJJ_60_120_htt",
                "qqH_GE2J_MJJ_120_350_htt"
            ]
        },
        "201": {
            "style": "inclusive",
            "displayname": "qq#rightarrowH p_{T}^{H} > 200",
            "signals": ["qqH_GE2J_MJJ_GT350_PTH_GT200_htt"]
        },
        "202": {
            "style":
            "inclusive",
            "displayname":
            "qq#rightarrowH vbftopo mjj > 700",
            "signals": [
                "qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_htt",
                "qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_htt"
            ]
        },
        "203": {
            "style":
            "inclusive",
            "displayname":
            "qq#rightarrowH vbftopo mjj [350,700]",
            "signals": [
                "qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_htt",
                "qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_htt"
            ]
        },
        "111": {
            "style":
            "inclusive",
            "displayname":
            "gg#rightarrowH 2-jet, mjj [0,350]",
            "signals": [
                "ggH_GE2J_MJJ_0_350_PTH_0_60_htt",
                "ggH_GE2J_MJJ_0_350_PTH_60_120_htt",
                "ggH_GE2J_MJJ_0_350_PTH_120_200_htt"
            ]
        },
    }
    return category_mapping[category]


def get_label_for_category(category, tag):
    category_labels = {
        "1": "ggH",
        "2": "qqH",
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
    if tag == "stxs_stage1p1":
        category_labels.update({
            "100": "ggH 0-jet",
            "101": "ggH 1-jet p_{T}^{H} [0,120]",
            "102": "ggH 1-jet p_{T}^{H} [120,200]",
            "103": "ggH #geq 2-jet",
            "104": "ggH p_{T}^{H} > 200",
            "200": "qqH 2J low mjj",
            "201": "qqH p_{T}^{H}>200",
            "202": "qqH vbftopo mjj>700",
            "203": "qqH vbftopo mjj [350,700]",
        })
    elif tag == "stxs_stage1p1cut":
        category_labels.update({
            "100": "ggH 0-jet",
            "101": "ggH 1-jet p_{T}^{H} [0,120]",
            "102": "ggH 1-jet p_{T}^{H} [120,#infty]",
            "103": "ggH #geq 2-jet",
            "104": "ggH p_{T}^{H} #gt 200",
            "200": "qqH 2J",
            "201": "qqH p_{T}^{H} #gt 200",
            "202": "qqH vbftopo_highmjj",
            "203": "qqH vbftopo lowmjj",
        })
    elif tag == "stxs_stage1p1_15node":
        category_labels.update({
            "100": "ggH 0-jet, p_{T}^{H} [0,10]",
            "101": "ggH 0-jet, p_{T}^{H} > 10",
            "102": "ggH 1-jet, p_{T}^{H} [0,60]",
            "103": "ggH 1-jet, p_{T}^{H} [60,120]",
            "104": "ggH 1-jet, p_{T}^{H} [120,200]",
            "105": "ggH 2-jet, mjj [0,350], p_{T}^{H} [0,60]",
            "106": "ggH 2-jet, mjj [0,350], p_{T}^{H} [60,120]",
            "107": "ggH 2-jet, mjj [0,350], p_{T}^{H} [120,200]",
            "108": "ggH p_{T}^{H} [200,300]",
            "109": "ggH p_{T}^{H} > 300",
            "110": "ggH 2-jet, mjj > 350, p_{T}^{H} [0,200]",
            "111": "ggH 2-jet, mjj [0,350], p_{T}^{H} [0,200]",
            "200": "qqH 2-jet low mjj",
            "201": "qqH p_{T}^{H} > 200",
            "202": "qqH vbftopo mjj > 700",
            "203": "qqH vbftopo mjj [350,700]",
        })
    elif tag == "stxs_stage0":
        category_labels.update({"1": "2D ggH/qqH category"})
    return category_labels[category]


class plot():
    def __init__(self, category, era, channel, title, plotConfig, rootfile):
        self.category = category
        self.channel = channel
        self.era = era
        self.plottitle = title
        self.background_processes = collections.OrderedDict()
        self.signal_processes = collections.OrderedDict()
        self.plotConfig = plotConfig
        if int(self.category) == 1 or int(self.category) >= 100:
            self.isSignal = True
        else:
            self.isSignal = False
        self.rootfile = rootfile
        self.mainsignal = []
        self.linear = self.plotConfig.settings["linear"]
        self.id = "{}_{}_{}".format(self.era, self.channel, self.category)
        self.ratiolist = []
        width = 600
        if category == "1":
            width = 750
        if self.isSignal:
            self.painter = dd.Plot([[0.5, 0.48]],
                                   "ModTDR",
                                   r=0.04,
                                   l=0.14,
                                   width=width)
        else:
            self.painter = dd.Plot([[0.3, 0.28]],
                                   "ModTDR",
                                   r=0.04,
                                   l=0.14,
                                   width=width)

    def __call__(self):
        return self.painter

    def add_background(self, process, label, style, histnames):
        self.background_processes[process] = {
            "label": label,
            "style": style,
            "histnames": histnames
        }

    def add_signal(self, process, label, style, histnames, main=False):
        self.signal_processes[process] = {
            "label": label,
            "style": style,
            "main": main,
            "linewidth": 3,
            "linecolor": style,
            "histnames": histnames
        }

    def print_plot_settings(self):
        logger.info(" ---- {} - {} - {} -----".format(self.era, self.channel,
                                                      self.category))
        logger.info(" ---- signals -----")
        logger.info(json.dumps(self.signal_processes, indent=4))
        logger.info(" ---- Backgrounds -----")
        logger.info(json.dumps(self.background_processes, indent=4))

    def add_signal_hist(self, process, index):
        hists = {}
        if self.era == "all" and self.channel == "cmb":
            if self.category == "111":
                for i, subprocess in enumerate(
                        self.signal_processes[process]["histnames"]):
                    for j, era in enumerate(["2016", "2017", "2018"]):
                        for k, channel in enumerate(["et", "mt", "tt", "em"]):
                            for h, category in enumerate(["105", "106",
                                                          "107"]):
                                histid = "{}-{}-{}-{}".format(era,channel,category,subprocess)
                                hists[histid] = {
                                    "era": era,
                                    "channel": channel,
                                    "category": category,
                                    "process": subprocess
                                }
            else:
                for i, subprocess in enumerate(
                        self.signal_processes[process]["histnames"]):
                    for j, era in enumerate(["2016", "2017", "2018"]):
                        for k, channel in enumerate(["et", "mt", "tt", "em"]):
                            histid = "{}-{}-{}-{}".format(era,channel,self.category,subprocess)
                            hists[histid] = {
                                "era": era,
                                "channel": channel,
                                "category": self.category,
                                "process": subprocess
                            }
        elif self.era == "all" and self.channel != "cmb":
            if self.category == "111":
                for i, subprocess in enumerate(
                        self.signal_processes[process]["histnames"]):
                    for j, era in enumerate(["2016", "2017", "2018"]):
                        for h, category in enumerate(["105", "106",
                                                        "107"]):
                            histid = "{}-{}-{}-{}".format(era,self.channel,category,subprocess)
                            hists[histid] = {
                                "era": era,
                                "channel": self.channel,
                                "category": self.category,
                                "process": subprocess
                            }
            else:
                for i, subprocess in enumerate(
                        self.signal_processes[process]["histnames"]):
                    for j, era in enumerate(["2016", "2017", "2018"]):
                        if self.channel == "em" and self.category in [
                                "15", "21"
                        ]:
                            continue
                        if self.channel == "tt" and self.category in [
                                "13", "15", "19"
                        ]:
                            continue
                        if self.channel == "mt" and self.category in ["19"]:
                            continue
                        if self.channel == "et" and self.category in ["19"]:
                            continue
                        histid = "{}-{}-{}-{}".format(era,self.channel,self.category,subprocess)
                        hists[histid] = {
                            "era": era,
                            "channel": self.channel,
                            "category": self.category,
                            "process": subprocess
                        }
        else:
            for i, subprocess in enumerate(
                    self.signal_processes[process]["histnames"]):
                histid = "{}-{}-{}-{}".format(self.era,self.channel,self.category,subprocess)
                hists[histid] = {
                    "era": self.era,
                    "channel": self.channel,
                    "category": self.category,
                    "process": subprocess
                }
        for histid in hists:
            hists[histid]["rootfile"] = self.rootfile.get(hists[histid]["era"],  hists[histid]["channel"],
                                             hists[histid]["category"], hists[histid]["process"])
            if not isinstance(hists[histid]["rootfile"], ROOT.TH1):
                hists.rm(histid)
        # if no files found nothing to do here
        if len(hists.keys()) == 0:
            logger.warning(
                "No histograms for {} found --> skipping".format(process))
        else:
            # rebin 
            best_binning = set([
                hists[min(hists.keys())]["rootfile"].GetBinLowEdge(i)
                for i in xrange(hists[min(hists.keys())]["rootfile"].GetNbinsX() + 2)
            ])
            logger.debug("Initial binning: {}".format(best_binning))
            for histid in hists:
                test_binning = set([
                    hists[histid]["rootfile"].GetBinLowEdge(i)
                    for i in xrange(hists[histid]["rootfile"].GetNbinsX() + 2)
                ])
                best_binning = test_binning.intersection(best_binning)
                logger.debug("Initial binning: {}".format(best_binning))
            binning = np.array(
                sorted([x for x in list(best_binning) if x >= 0]))
            if self.category == 1:
                np.append(binning, 28.0)
            else:
                np.append(binning, 1.0)
            logger.debug("Final binning: {}".format(binning))
            # apply binning to all hists
            for histid in hists:
                hists[histid]["rootfile"] = hists[histid]["rootfile"].Rebin(
                    len(binning) - 1,
                    "{}_rebinned".format(hists[histid]["rootfile"].GetName()), binning)
                logger.debug("Rebinned: {}".format(hists[histid]["rootfile"]))
                logger.warning("found {} histograms".format(len(hists.keys())))
            basehist = hists[min(hists.keys())]["rootfile"]
            if len(hists.keys()) >= 2:
                for hist in hists:
                    if hists[hist]["rootfile"] == basehist:
                        continue
                    else:
                        basehist.Add(hists[hist]["rootfile"])
            self.painter.subplot(index).add_hist(basehist,
                                                 "{}".format(process))
            if process == "inclusive" and self.category == "1":
                self.painter.subplot(index).setGraphStyle(
                    "{}".format(process),
                    "hist",
                    fillcolor=self.signal_processes[process]["style"])
                self.painter.subplot(index).add_hist(basehist,
                                                 "{}_ratio".format(process))
                self.painter.subplot(index).setGraphStyle(
                    "{}_ratio".format(process),
                    "hist",
                    linecolor=self.signal_processes[process]["style"],
                    linewidth=2)
            else:
                self.painter.subplot(index).setGraphStyle(
                "{}".format(process),
                "hist",
                linecolor=self.signal_processes[process]["style"],
                linewidth=2)

    def add_background_hist(self, process, index):
        hists = {}
        if self.era == "all" and self.channel == "cmb":
            if self.category == "111":
                for i, subprocess in enumerate(
                        self.background_processes[process]["histnames"]):
                    for j, era in enumerate(["2016", "2017", "2018"]):
                        for k, channel in enumerate(["et", "mt", "tt", "em"]):
                            for h, category in enumerate(["105", "106",
                                                          "107"]):
                                histid = "{}-{}-{}-{}".format(era, channel, category, subprocess)
                                hists[histid] = {
                                    "era": era,
                                    "channel": channel,
                                    "category": category,
                                    "process": subprocess
                                }
            else:
                for i, subprocess in enumerate(
                        self.background_processes[process]["histnames"]):
                    for j, era in enumerate(["2016", "2017", "2018"]):
                        for k, channel in enumerate(["et", "mt", "tt", "em"]):
                            if channel == "em" and self.category in [
                                    "15", "21"
                            ]:
                                continue
                            if channel == "tt" and self.category in [
                                    "13", "15", "19"
                            ]:
                                continue
                            if channel == "mt" and self.category in ["19"]:
                                continue
                            if channel == "et" and self.category in ["19"]:
                                continue
                            histid = "{}-{}-{}-{}".format(era, channel, self.category, subprocess)
                            hists[histid] = {
                                "era": era,
                                "channel": channel,
                                "category": self.category,
                                "process": subprocess
                            }
            
        elif self.era == "all" and self.channel != "cmb":
            if self.category == "111":
                for i, subprocess in enumerate(
                        self.background_processes[process]["histnames"]):
                    for j, era in enumerate(["2016", "2017", "2018"]):
                        for h, category in enumerate(["105", "106",
                                                        "107"]):
                            histid = "{}-{}-{}-{}".format(era, self.channel, category, subprocess)
                            hists[histid] = {
                                "era": era,
                                "channel": self.channel,
                                "category": category,
                                "process": subprocess
                            }
            else:
                for i, subprocess in enumerate(
                        self.background_processes[process]["histnames"]):
                    for j, era in enumerate(["2016", "2017", "2018"]):
                        if self.channel == "em" and self.category in [
                                "15", "21"
                        ]:
                            continue
                        if self.channel == "tt" and self.category in [
                                "13", "15", "19"
                        ]:
                            continue
                        if self.channel == "mt" and self.category in ["19"]:
                            continue
                        if self.channel == "et" and self.category in ["19"]:
                            continue
                        histid = "{}-{}-{}-{}".format(era, self.channel, self.category, subprocess)
                        hists[histid] = {
                            "era": era,
                            "channel": self.channel,
                            "category": self.category,
                            "process": subprocess
                        }
        else:
            for i, subprocess in enumerate(
                    self.background_processes[process]["histnames"]):
                histid = "{}-{}-{}-{}".format(self.era, self.channel, self.category, subprocess)
                hists[histid] = {
                    "era": self.era,
                    "channel": self.channel,
                    "category": self.category,
                    "process": subprocess
                }
        for histid in hists:
            hists[histid]["rootfile"] = self.rootfile.get(hists[histid]["era"],  hists[histid]["channel"],
                                             hists[histid]["category"], hists[histid]["process"])
            if not isinstance(hists[histid]["rootfile"], ROOT.TH1):
                hists.rm(histid)
        if len(hists.keys()) == 0:
            logger.warning(
                "No histograms for {} found --> skipping".format(process))
        # addup all existing histograms
        else:
            logger.warning("found {} histograms".format(len(hists.keys())))
            # now the the smallest binning of all histograms
            best_binning = set([
                hists[min(hists.keys())]["rootfile"].GetBinLowEdge(i)
                for i in xrange(hists[min(hists.keys())]["rootfile"].GetNbinsX() + 2)
            ])
            for histid in hists:
                test_binning = set([
                    hists[histid]["rootfile"].GetBinLowEdge(i)
                    for i in xrange(hists[histid]["rootfile"].GetNbinsX() + 2)
                ])
                best_binning = test_binning.intersection(best_binning)
            binning = np.array(
                sorted([x for x in list(best_binning) if x >= 0]))
            if self.category == 1:
                np.append(binning, 28.0)
            else:
                np.append(binning, 1.0)
            logger.debug("Final binning: {}".format(binning))
            # apply binning to all hists
            for histid in hists:
                logger.debug("Rebinning: {}".format(hists[histid]["rootfile"]))
                hists[histid]["rootfile"] = hists[histid]["rootfile"].Rebin(
                    len(binning) - 1,
                    "{}_rebinned".format(hists[histid]["rootfile"].GetName()), binning)
            basehist = hists[min(hists.keys())]["rootfile"]
            if len(hists.keys()) >= 2:
                for hist in hists:
                    if hists[hist]["rootfile"] == basehist:
                        continue
                    else:
                        basehist.Add(hists[hist]["rootfile"])
            self.painter.subplot(index).add_hist(basehist, process, "bkg")
            self.painter.subplot(index).setGraphStyle(
                "{}".format(process),
                "hist",
                fillcolor=self.background_processes[process]["style"])

    def add_data(self):
        hists_data = {}
        hists_bkg = {}
        if self.era == "all" and self.channel == "cmb":
            if self.category == "111":
                for j, era in enumerate(["2016", "2017", "2018"]):
                    for k, channel in enumerate(["et", "mt", "tt", "em"]):
                        for h, category in enumerate(["105", "106", "107"]):
                            histid = "{}-{}-{}-{}".format(era,channel,category)
                            hists_data[histid] = {
                                "era": era,
                                "channel": channel,
                                "category": category
                            }
                            hists_bkg[histid] = {
                                "era": era,
                                "channel": channel,
                                "category": category
                            }
            else:
                for j, era in enumerate(["2016", "2017", "2018"]):
                    for k, channel in enumerate(["et", "mt", "tt", "em"]):
                        if channel == "em" and self.category in ["15", "21"]:
                            continue
                        if channel == "tt" and self.category in [
                                "13", "15", "19"
                        ]:
                            continue
                        if channel == "mt" and self.category in ["19"]:
                            continue
                        if channel == "et" and self.category in ["19"]:
                            continue
                        histid = "{}-{}-{}".format(era, channel, self.category)
                        hists_data[histid] = {
                                "era": era,
                                "channel": channel,
                                "category": self.category
                            }
                        hists_bkg[histid] = {
                            "era": era,
                            "channel": channel,
                            "category": self.category
                        }
        elif self.era == "all" and self.channel != "cmb":
            if self.category == "111":
                for j, era in enumerate(["2016", "2017", "2018"]):
                    for h, category in enumerate(["105", "106", "107"]):
                        histid = "{}-{}-{}".format(era, self.channel, category)
                        hists_data[histid] = {
                                "era": era,
                                "channel": self.channel,
                                "category": category
                            }
                        hists_bkg[histid] = {
                            "era": era,
                            "channel": self.channel,
                            "category": category
                        }
            else:
                for j, era in enumerate(["2016", "2017", "2018"]):
                    if self.channel == "em" and self.category in ["15", "21"]:
                        continue
                    if self.channel == "tt" and self.category in [
                            "13", "15", "19"
                    ]:
                        continue
                    if self.channel == "mt" and self.category in ["19"]:
                        continue
                    if self.channel == "et" and self.category in ["19"]:
                        continue
                    histid = "{}-{}-{}".format(era, self.channel, self.category)
                    hists_data[histid] = {
                                "era": era,
                                "channel": self.channel,
                                "category": self.category
                            }
                    hists_bkg[histid] = {
                        "era": era,
                        "channel": self.channel,
                        "category": self.category
                    }
        else:
            histid = "{}-{}-{}".format(self.era, self.channel, self.category)
            hists_data[histid] = {
                "era": self.era,
                "channel": self.channel,
                "category": self.category
            }
            hists_bkg[histid] = {
                "era": self.era,
                "channel": self.channel,
                "category": self.category
            }
        for histid in hists_data:
            hists_data[histid]["rootfile"] = self.rootfile.get(hists_data[histid]["era"],  hists_data[histid]["channel"],
                                             hists_data[histid]["category"], "data_obs")
            hists_bkg[histid]["rootfile"] = self.rootfile.get(hists_bkg[histid]["era"],  hists_bkg[histid]["channel"],
                                             hists_bkg[histid]["category"], "TotalBkg")
        # now the the smallest binning of all histograms
        best_binning = set([
            hists_data[min(hists_data.keys())]["rootfile"].GetBinLowEdge(i) for i in
            xrange(hists_data[min(hists_data.keys())]["rootfile"].GetNbinsX() + 2)
        ])
        for histid in hists_data:
            test_binning = set([
                hists_data[histid]["rootfile"].GetBinLowEdge(i)
                for i in xrange(hists_data[histid]["rootfile"].GetNbinsX() + 2)
            ])
            best_binning = test_binning.intersection(best_binning)
        binning = np.array(
            sorted([x for x in list(best_binning) if x >= 0]))
        if self.category == 1:
            np.append(binning, 28.0)
        else:
            np.append(binning, 1.0)
        logger.debug("Final binning: {}".format(binning))
        # apply binning to all hists
        for histid in hists_data:
            logger.debug("Rebinning: {}".format(hists_data[histid]["rootfile"]))
            hists_data[histid]["rootfile"] = hists_data[histid]["rootfile"].Rebin(
                len(binning) - 1,
                "{}_rebinned".format(hists_data[histid]["rootfile"].GetName()),
                binning)
        for histid in hists_bkg:
            logger.debug("Rebinning: {}".format(hists_bkg[histid]["rootfile"]))
            hists_bkg[histid]["rootfile"] = hists_bkg[histid]["rootfile"].Rebin(
                len(binning) - 1,
                "{}_rebinned".format(hists_bkg[histid]["rootfile"].GetName()), binning)
        data_obs = hists_data[min(hists_data.keys())]["rootfile"]
        total_bkg = hists_bkg[min(hists_bkg.keys())]["rootfile"]
        for hist in hists_data:
            if hists_data[hist]["rootfile"] == data_obs:
                continue
            data_obs.Add(hists_data[hist]["rootfile"])
        for hist in hists_bkg:
            if hists_bkg[hist]["rootfile"] == total_bkg:
                continue
            total_bkg.Add(hists_bkg[hist]["rootfile"])

        
        if self.plotConfig.settings["blind_data"]:
            self.blind_data(data_obs)
        self.painter.add_hist(data_obs, "data_obs")
        self.painter.add_hist(total_bkg, "total_bkg")

        self.painter.subplot(0).setGraphStyle("data_obs", "e0")
        self.painter.setGraphStyle("total_bkg",
                                   "e2",
                                   markersize=0,
                                   fillcolor=styles.color_dict["unc"],
                                   linecolor=0)

    def blind_data(self, data_obs):
        if self.category == "1":
            # special case for 2D discriminant
            for i in xrange(data_obs.GetNbinsX() + 1):
                if data_obs.GetBinLowEdge(i) in [
                        4.0, 5.0, 6.0
                ] or data_obs.GetBinLowEdge(i) >= 10.0:
                    data_obs.SetBinContent(i, 0.0)
                    data_obs.SetBinError(i, 0.0)
        elif self.isSignal:
            for i in xrange(data_obs.GetNbinsX() + 1):
                if data_obs.GetBinLowEdge(i) + data_obs.GetBinWidth(i) > 0.5:
                    data_obs.SetBinContent(i, 0.0)
                    data_obs.SetBinError(i, 0.0)

    def assemble_ratio(self):
        self.ratiolist = ["total_bkg"]
        if self.isSignal and self.plotConfig.settings["exact_signals"]:
            color = [self.mainsignal["style"], "ggH", "qqH"]
            for i, sublabel in enumerate(["main", "ggH_rest", "qqH_rest"]):
                signal = self.painter.subplot(1).get_hist(
                    "{}_signal".format(sublabel))
                signal.Add(self.painter.subplot(1).get_hist("total_bkg"))
                self.painter.subplot(1).add_hist(
                    signal, "bkg_{}_signal".format(sublabel))
                self.painter.subplot(1).setGraphStyle(
                    "bkg_{}_signal".format(sublabel),
                    "hist",
                    linecolor=styles.color_dict[color[i]],
                    linewidth=2)
                self.ratiolist.append("bkg_{}_signal".format(sublabel))
        elif self.isSignal:
            for process in ["qqH", "ggH", "inclusive"]:
                signal = self.painter.subplot(1).get_hist(process)
                signal.Add(self.painter.subplot(1).get_hist("total_bkg"))
                self.painter.subplot(1).add_hist(signal,
                                                 "bkg_{}".format(process))
                self.painter.subplot(1).setGraphStyle(
                    "bkg_{}".format(process),
                    "hist",
                    linecolor=styles.color_dict[process],
                    linewidth=2)
                self.ratiolist.append("bkg_{}".format(process))
        self.ratiolist.append("data_obs")
        self.painter.subplot(1).normalize(self.ratiolist, "total_bkg")

    def set_axis_range(self):
        self.painter.subplot(0).setYlims(
            self.plotConfig.split_dict[self.channel],
            max(2 * self.painter.subplot(0).get_hist("data_obs").GetMaximum(),
                self.plotConfig.split_dict[self.channel] * 2))
        self.painter.subplot(1).setNYdivisions(3, 5)
        self.painter.subplot(1).setNXdivisions(5, 3)
        self.painter.subplot(1).setYlims(0.85, 1.25)
        if not self.linear:
            self.painter.subplot(1).setYlims(
                0.1, self.plotConfig.split_dict[self.channel])
            self.painter.subplot(1).setLogY()
        
        if self.category == "1":
            self.painter.subplot(0).setYlims(
            self.plotConfig.split_dict[self.channel],
            max(1.5 * self.painter.subplot(0).get_hist("data_obs").GetMaximum(),
                self.plotConfig.split_dict[self.channel] * 1.5))
            # self.painter.subplot(0).setLogY()
            # self.painter.subplot(0).setYlims(1, 4500000000)
            self.painter.subplot(1).setXlims(0.0, 28.0)
            self.painter.subplot(0).setXlims(0.0, 28.0)
            if self.era == "all" and self.channel == "cmb":
                self.painter.subplot(1).setYlims(0.95, 1.3)
            else:
                self.painter.subplot(1).setYlims(0.85, 2.65)

        if self.plotConfig.tag == "stxs_stage1p1_15node":
            if self.era == "all" and self.channel == "cmb":
                self.painter.subplot(1).setYlims(0.95, 1.13)
                if self.category == "100":
                    self.painter.subplot(1).setYlims(0.95, 1.1)
                if self.category == "101":
                    self.painter.subplot(1).setYlims(0.95, 1.1)
                if self.category == "102":
                    self.painter.subplot(1).setYlims(0.95, 1.18)
                if self.category == "103":
                    self.painter.subplot(1).setYlims(0.95, 1.18)
                if self.category == "104":
                    self.painter.subplot(1).setYlims(0.95, 1.18)
                if self.category == "105":
                    self.painter.subplot(1).setYlims(0.95, 1.1)
                if self.category == "106":
                    self.painter.subplot(1).setYlims(0.95, 1.18)
                if self.category == "107":
                    self.painter.subplot(1).setYlims(0.95, 1.18)
                if self.category == "108":
                    self.painter.subplot(1).setYlims(0.95, 1.18)
                if self.category == "109":
                    self.painter.subplot(1).setYlims(0.90, 1.18)
                if self.category == "110":
                    self.painter.subplot(1).setYlims(0.95, 1.25)
                if self.category == "111":
                    self.painter.subplot(1).setYlims(0.95, 1.1)
                if self.category == "200":
                    self.painter.subplot(1).setYlims(0.90, 1.2)
                if self.category == "201":
                    self.painter.subplot(1).setYlims(0.95, 1.25)
                if self.category == "202":
                    self.painter.subplot(1).setYlims(0.90, 1.45)
                if self.category == "203":
                    self.painter.subplot(1).setYlims(0.95, 1.2)
            elif self.isSignal:
                self.painter.subplot(0).setLogY()
                self.painter.subplot(1).setYlims(0.45, 2.55)
                self.painter.subplot(0).setYlims(1, 4500000000)
    
    def set_axis_labels(self):
        if not self.linear:
            self.painter.subplot(1).setYlabel(
                "")  # otherwise number labels are not drawn on axis
        if self.plotConfig.tag == "stxs_stage0" and self.category == "1":
            self.painter.subplot(1).setXlabel("")
            self.painter.subplot(1).setXlabel("2D discriminator bin index")
            #self.painter.subplot(1).setNXdivisions(28, 0)
            #self.painter.subplot(1).changeXLabels(["Bin {}".format(x) for x in xrange(29)])
        else:
            self.painter.subplot(1).setXlabel("NN output")
        if self.plotConfig.settings["normalize_by_bin_width"]:
            self.painter.subplot(0).setYlabel("dN/d(NN output)")
        else:
            self.painter.subplot(0).setYlabel("N_{events}")

        self.painter.subplot(1).setYlabel("Ratio")
        #self.painter.scaleYLabelSize(0.6)
        self.painter.scaleYTitleOffset(1.1)

    def rescale_upper_plot(self):
        scaling = {}
        signalsteps = [7, 12, 16, 19, 21, 28]
        for i,edge in enumerate(signalsteps[:-1]):
            scaling[i] = {
                "interval" :[edge, signalsteps[i+1]],
                "sf" :1.0 }
        # first calculate the sf for the different steps
        maxheight = self.painter.subplot(0).get_hist("data_obs").GetMaximum()*0.4
        k = 0
        for interval in scaling:
            content = []
            for i in xrange(self.painter.subplot(0).get_hist("data_obs").GetNbinsX() + 1):
                binedge = self.painter.subplot(0).get_hist("data_obs").GetBinLowEdge(i)
                if binedge >= scaling[interval]["interval"][0] and binedge < scaling[interval]["interval"][1]:
                    content.append(self.painter.subplot(0).get_hist("data_obs").GetBinContent(i))
            sf = round(maxheight / max(content), 0)
            if sf > 5:
                sf = 5 * round((maxheight / max(content))/5)
            scaling[interval]["sf"] = sf
        
        # now set the labels of the scalefactor
        # the plot starts at ~3/28 and ends at ~27/28
        for i,interval in enumerate(scaling):
            step = 0.03042 * scaling[interval]["interval"][0] + 0.1211 
            self.painter.DrawText(step, 0.72,"x {}".format(int(scaling[interval]["sf"])), textsize=0.025)

        for hist_name in self.painter.subplot(0)._hists.keys():
            histogram = self.painter.subplot(0).get_hist(hist_name)
            for i in xrange(histogram.GetNbinsX() + 1):
                bin = histogram.GetBinContent(i)
                binerror = histogram.GetBinError(i)
                binedge = histogram.GetBinLowEdge(i)
                sf = 1.0
                for interval in scaling:
                     if binedge >= scaling[interval]["interval"][0]:
                        sf = scaling[interval]["sf"]
                histogram.SetBinContent(i, bin*sf)
                histogram.SetBinError(i, binerror*sf)

    def draw_subplots(self):
        procs_to_draw_0 = ["stack", "total_bkg", "data_obs"]

        if self.isSignal:
            procs_to_draw_0 += self.signal_processes.keys()
            if self.category == "1":
                procs_to_draw_0.remove("inclusive")
        self.painter.subplot(0).Draw(procs_to_draw_0)
        self.painter.subplot(1).Draw(self.ratiolist)

    def set_upper_legend(self):
        height = 0.15
        if not self.isSignal and self.plotConfig.settings["combine_backgrounds"]:
            height = 0.10
        self.painter.add_legend(width=0.62, height=height)
        # set background labels
        for process in collections.OrderedDict(reversed(list(self.background_processes.items()))):
            try:
                self.painter.legend(0).add_entry(
                    0, process, styles.legend_label_dict[process.replace(
                        "TTL", "TT").replace("VVL", "VV")], 'f')
            except BaseException:
                pass
        # set signal
        for signal in self.signal_processes:
            if self.category == "1" and signal=="inclusive":
                self.painter.legend(0).add_entry(
                    0, signal,
                    self.signal_processes[signal]["label"], 'f')
            else:
                try:
                    self.painter.legend(0).add_entry(
                        0, signal,
                        self.signal_processes[signal]["label"], 'l')
                except BaseException:
                    pass
        self.painter.legend(0).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
        self.painter.legend(0).add_entry(0, "data_obs", "Observed", 'PEL')
        self.painter.legend(0).setNColumns(3)
        self.painter.legend(0).Draw()

        if args.chi2test:
            f = ROOT.TFile(args.input, "read")
            background = f.Get("htt_{}_{}_Run{}_{}/TotalBkg".format(
                self.channel, self.category, self.era,
                "prefit" if "prefit" in args.input else "postfit"))
            data = f.Get("htt_{}_{}_Run{}_{}/data_obs".format(
                self.channel, self.category, self.era,
                "prefit" if "prefit" in args.input else "postfit"))
            chi2 = data.Chi2Test(background, "UW CHI2/NDF")
            self.painter.DrawText(0.7, 0.3,
                                  "\chi^{2}/ndf = " + str(round(chi2, 3)))

    def set_ratio_legend(self):
        if self.isSignal:
            height = 0.10
            ncol = 3
            width = 0.70
        elif self.category == "1":
            height = 0.10
            ncol = 3
            width = 0.56
        else:
            # for background categories, there are only two entries
            height = 0.05
            ncol = 2
            width = 0.46
        self.painter.add_legend(reference_subplot=1,
                                pos=1,
                                width=width,
                                height=height)
        self.painter.legend(1).setNColumns(ncol)
        self.painter.legend(1).add_entry(1, "data_obs", "Observed",
                                                'PEL')
        self.painter.legend(1).add_entry(1, "total_bkg", "Bkg. unc.",
                                                'f')
        if self.isSignal and self.plotConfig.settings["exact_signals"]:
            main_signal_label = ""
            if len(
                    get_signal_for_category(
                        self.category)["displayname"].split(", ")) > 2:
                main_signal_label = "#splitline{%s}{%s (#mu=%s)}" % (
                    ", ".join(
                        get_signal_for_category(
                            self.category)["displayname"].split(", ")[:2]),
                    get_signal_for_category(
                        self.category)["displayname"].split(", ")[2],
                    mu_dict[self.category])
            else:
                main_signal_label = "#splitline{%s}{(#mu=%s)}" % (
                    get_signal_for_category(self.category)["displayname"],
                    mu_dict[self.category])
            self.painter.legend(1).add_entry(
                1,"main_signal", main_signal_label, 'l')
            self.painter.legend(1).add_entry(
                1, "ggH_rest_signal", 
                "gg#rightarrowH {}".format(
                    " (other)" if "ggH" in get_signal_for_category(
                        self.category)["displayname"] else ""), 'l')
            self.painter.legend(1).add_entry(
                1, "qqH_rest_signal",
                "qq#rightarrowH {}".format(
                    " (other)" if "qqH" in get_signal_for_category(
                        self.category)["displayname"] else ""), 'l')
        elif self.isSignal:
            self.painter.legend(1).add_entry(
                1, "ggH",
                "{}".format(signal_labels["ggH"]["label"]), 'l')
            self.painter.legend(1).add_entry(
                1, "qqH",
                "{}".format(signal_labels["qqH"]["label"]), 'l')
            self.painter.legend(1).add_entry(
                1, "inclusive_ratio",
                "{}".format(signal_labels["inclusive"]["label"]), 'l')
        self.painter.legend(1).setAlpha(0.0)
        self.painter.legend(1).Draw()

    def draw_lines(self):
        # add vertical lines to highlight the qqH binning
        if self.category == "1":
            # line in the ratio
            self.painter.add_line(reference_subplot=1, xmin=0, ymin=1, xmax=28, ymax=1, color=1, linestyle=7)
            height =  max(self.painter.subplot(0).get_hist("data_obs").GetMaximum(),
                self.plotConfig.split_dict[self.channel])
            subplot_min = self.painter.subplot(1).get_hist("total_bkg").GetMinimum()
            subplot_max = self.painter.subplot(1).get_hist("total_bkg").GetMaximum()
            if self.channel == "cmb" and self.era == "all":
                subplot_min = 0.95
                subplot_max = 1.65
            
            signalsteps = [7, 12, 16, 19, 21]
            for i,edge in enumerate(signalsteps):
                self.painter.add_line(0, xmin=edge, ymin=0, xmax=edge, ymax=height, color=16, linestyle=7, linewidth=2)
                self.painter.add_line(1, xmin=edge, ymin=round(subplot_min, 3), xmax=edge, ymax=0.7*round(subplot_max, 3),color=16, linestyle=7, linewidth=2)
        else:
            # plot the 1 line in the ratio all other plots
            self.painter.add_line(reference_subplot=1, xmin=0, ymin=1, xmax=1, ymax=1, color=1, linestyle=7)
        for i in xrange(len(self.painter._lines)):
            self.painter.line(i).Draw()

class plotConfigurator():
    def __init__(self, tag, channels, era, inputfile):
        self.tag = tag
        self.channels = channels
        self.inputfile = inputfile
        self.settings = {
            "train_emb": args.train_emb,
            "train_ff": args.train_ff,
            "linear": args.linear,
            "normalize_by_bin_width": args.normalize_by_bin_width,
            "embedding": args.embedding,
            "fake_factor": args.fake_factor,
            "exact_signals": args.exact_signals,
            "blind_data": args.blind_data,
            "blinded_shapes": args.blinded_shapes,
            "single_category": args.single_category,
            "combine_backgrounds": args.combine_backgrounds
        }
        self.background_categories = [
            "12", "15", "11", "13", "14", "16", "17", "19", "20", "21"
        ]
        self.channel_labels = {
            "ee":
            "ee",
            "em":
            "e#mu",
            "et":
            "e#tau_{h}",
            "mm":
            "#mu#mu",
            "mt":
            "#mu#tau_{h}",
            "tt":
            "#tau_{h}#tau_{h}",
            "cmb":
            "e^{}#mu^{} + e^{}#tau_{h} + #mu^{}#tau_{h} + #tau_{h}^{}#tau_{h}^{}"
        }
        self.categories = {}
        self.detailed_signals = [
            'ggH_1J_PTH_120_200_htt', 'ggH_GE2J_MJJ_0_350_PTH_120_200_htt',
            'ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_htt',
            'ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_htt',
            'ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_htt',
            'ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_htt',
            'ggH_PTH_200_300_htt', 'ggH_PTH_300_450_htt',
            'ggH_PTH_450_650_htt', 'ggH_PTH_GT650_htt', 'qqH_1J_htt',
            'qqH_GE2J_MJJ_0_60_htt', 'qqH_GE2J_MJJ_120_350_htt',
            'qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_htt',
            'qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_htt',
            'qqH_GE2J_MJJ_60_120_htt', 'qqH_GE2J_MJJ_GT350_PTH_GT200_htt',
            'qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_htt',
            'qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_htt'
        ]
        self.labels = {}
        self.split_dict = {}
        self.background_processes = []
        self.plots = []
        if era not in ["2016", "2017", "2018", "all"]:
            logger.critical("Era {} is not implemented.".format(args.era))
            raise Exception
        else:
            self.era = era

        # run setup commands
        self.setup_split_value()
        self.setup_categories(self.settings["single_category"])
        self.setup_plots()

    def setup_split_value(self):
        if self.settings["linear"]:
            split_value = 0
        else:
            if self.settings["normalize_by_bin_width"]:
                split_value = 10001
            else:
                split_value = 101
        self.split_dict = {c: split_value for c in self.channels}

    def setup_categories(self, single_category):
        if single_category != "":
            for channel in self.channels:
                self.categories[channel] = {single_category: {}}
        else:
            default_categories = {
                "et": {
                    "12": {},
                    "15": {},
                    "11": {},
                    "13": {},
                    "14": {},
                    "16": {}
                },
                "mt": {
                    "12": {},
                    "15": {},
                    "11": {},
                    "13": {},
                    "14": {},
                    "16": {}
                },
                "tt": {
                    "12": {},
                    "17": {},
                    "16": {}
                },
                "em": {
                    "12": {},
                    "13": {},
                    "14": {},
                    "16": {},
                    "19": {}
                },
                "cmb": {
                    "12": {},
                    "15": {},
                    "11": {},
                    "13": {},
                    "14": {},
                    "16": {},
                    "19": {}
                }
            }
            for channel in self.channels:
                self.categories[channel] = default_categories[channel]
            if self.settings["train_emb"]:  # swap ztt for embedding
                for chn in self.channels:
                    del self.categories[chn]["12"]
                    self.categories[chn]["20"] = {}
            if self.settings["train_ff"]:
                for chn in set(self.channels).intersection(
                        set(["mt", "et", "tt", "cmb"])):
                    # no change for em
                    if chn == "tt":
                        del self.categories[chn]["17"]
                    else:
                        del self.categories[chn]["11"]
                        del self.categories[chn]["14"]
                    self.categories[chn]["21"] = {}  # add ff
            if self.tag == "stxs_stage0":
                signalcats = ["1"]  # only 2D Category
            elif self.tag == "stxs_stage1p1":
                signalcats = [str(100 + i) for i in range(5)
                              ] + [str(200 + i) for i in range(4)]
            elif self.tag == "stxs_stage1p1_15node":
                signalcats = [str(100 + i) for i in range(11)
                              ] + [str(200 + i) for i in range(4)]
            elif self.tag == "stxs_stage1p1cut":
                signalcats = [str(100 + i) for i in range(5)
                              ] + [str(200 + i) for i in range(4)]
            else:
                signalcats = []
            for channel in self.channels:
                for signal in signalcats:
                    self.categories[channel][signal] = {}

    def setup_plots(self):
        for channel in self.channels:
            for category in self.categories[channel]:
                single_plot = plot(
                    category, self.era, channel,
                    get_label_for_category(category, self.tag), self,
                    rootfile_parser.Rootfile_parser(self.inputfile))

                bkg_processes = ["VVL", "TTL", "ZL", "jetFakes", "EMB"]
                if not self.settings["fake_factor"] and self.settings[
                        "embedding"]:
                    bkg_processes = [
                        "QCD", "VVJ", "W", "TTJ", "ZJ", "ZL", "EMB"
                    ]
                if not self.settings["embedding"] and self.settings[
                        "fake_factor"]:
                    bkg_processes = [
                        "VVT", "VVJ", "TTT", "TTJ", "ZJ", "ZL", "jetFakes",
                        "ZTT"
                    ]
                if not self.settings["embedding"] and not self.settings[
                        "fake_factor"]:
                    bkg_processes = [
                        "QCD", "VVT", "VVL", "VVJ", "W", "TTT", "TTL", "TTJ",
                        "ZJ", "ZL", "ZTT"
                    ]
                if channel == "em" and self.settings["embedding"]:
                    bkg_processes = ["VVL", "W", "TTL", "ZL", "QCD", "EMB"]
                elif channel == "em" and not self.settings["embedding"]:
                    bkg_processes = ["VVL", "W", "TTL", "ZL", "QCD", "ZTT"]
                elif channel == "cmb":
                    bkg_processes = [
                        "VVL", "W", "TTL", "ZL", "QCD", "EMB", "jetFakes"
                    ]
                if self.settings["combine_backgrounds"]:
                    single_plot.add_background(
                        "REST", styles.legend_label_dict["REST"],
                        styles.color_dict["REST"], [
                            "VVL", "W", "TTL", "ZL", "qqH_hww", "ggH_hww",
                            "VH_htt", "ZH_htt", "WH_htt", "ttH_htt"
                        ])
                    single_plot.add_background(
                        "jetFakesCMB", styles.legend_label_dict["jetFakesCMB"],
                        styles.color_dict["QCD"], ["QCD", "jetFakes"])
                    single_plot.add_background("EMB",styles.legend_label_dict["EMBCMB"], styles.color_dict["EMB"],["EMB"])
                else:
                    for process in bkg_processes:
                        single_plot.add_background(
                            process, styles.legend_label_dict[process],
                            styles.color_dict[process], [process])

                # if category is not a background category, include signals
                if category not in self.background_categories:
                    if not self.settings["combine_backgrounds"]:
                        single_plot.add_signal(
                            "ttH", signal_labels["ttH"]["label"],
                            styles.color_dict[signal_labels["ttH"]["style"]],
                            ["ttH_htt"], False)
                        single_plot.add_signal(
                            "VH", signal_labels["VH"]["label"],
                            styles.color_dict[signal_labels["VH"]["style"]],
                            ["VH_htt", "ZH_htt", "WH_htt"], False)
                        single_plot.add_signal(
                            "HWW", signal_labels["HWW"]["label"],
                            styles.color_dict[signal_labels["HWW"]["style"]],
                            ["qqH_hww", "ggH_hww"], False)
                    if self.settings["exact_signals"]:
                        main_signals = get_signal_for_category(
                            category)["signals"]
                        merge_signals_ggH = [
                            x for x in self.detailed_signals
                            if x not in main_signals and "ggH" in x
                        ]
                        merge_signals_qqH = [
                            x for x in self.detailed_signals
                            if x not in main_signals and "qqH" in x
                        ]
                        main_signal_label = ""
                        if len(
                                get_signal_for_category(category)
                            ["displayname"].split(", ")) > 2:
                            main_signal_label = "#splitline{%s}{%s (#mu=%s)}" % (
                                ", ".join(
                                    get_signal_for_category(category)
                                    ["displayname"].split(", ")[:2]),
                                get_signal_for_category(
                                    category)["displayname"].split(", ")[2],
                                mu_dict[category])
                        else:
                            main_signal_label = "#splitline{%s}{(#mu=%s)}" % (
                                get_signal_for_category(category)
                                ["displayname"], mu_dict[category])
                        single_plot.mainsignal = get_signal_for_category(
                            category)
                        single_plot.add_signal("main_signal",
                                               main_signal_label,
                                               styles.color_dict["inclusive"],
                                               main_signals, True)
                        single_plot.add_signal(
                            "ggH_rest_signal", "gg#rightarrowH {}".format(
                                " (other)" if "ggH" in get_signal_for_category(
                                    category)["displayname"] else ""),
                            styles.color_dict["ggH"], merge_signals_ggH, False)
                        single_plot.add_signal(
                            "qqH_rest_signal", "qq#rightarrowH {}".format(
                                " (other)" if "qqH" in get_signal_for_category(
                                    category)["displayname"] else ""),
                            styles.color_dict["qqH"], merge_signals_qqH, False)
                    else:
                        single_plot.mainsignal.extend(["ggH_htt", "qqH_htt", "inclusive"])
                        single_plot.add_signal(
                            "ggH", signal_labels["ggH"]["label"],
                            styles.color_dict["ggH"], ["ggH_htt"], True)
                        single_plot.add_signal(
                            "qqH", signal_labels["qqH"]["label"],
                            styles.color_dict["qqH"], ["qqH_htt"], True)
                        single_plot.add_signal(
                            "inclusive", signal_labels["inclusive"]["label"],
                            styles.color_dict["inclusive"], ["qqH_htt", "ggH_htt"], True)
                self.plots.append(single_plot)


def main(args):

    logger.debug("Arguments: {}".format(args))
    logger.debug("Setting up the plot")
    plotConfig = plotConfigurator(args.categories, args.channels, args.era,
                                  args.input)
    for plot in plotConfig.plots:
        channel = plot.channel
        category = plot.category
        era = plot.era
        plot.print_plot_settings()
        logger.debug(
            "Getting shapes for channel: {} / category: {} / era: {}".format(
                channel, category, era))

        ##################
        # get background histograms
        #################
        for background in plot.background_processes:
            plot.add_background_hist(background, 0)

        ##################
        # get signal histograms
        ##################
        for signal in plot.signal_processes:
            plot.add_signal_hist(signal, 0)
            plot.add_signal_hist(signal, 1)

        ##################
        # get observed data
        # and total background histograms
        # blind data is option is set
        ##################
        plot.add_data()

        #######################
        # Rescale top plot, only for stage0 and the signal category !
        # also add inclusive signal as histogram to the plot
        #######################
        stack = plot.background_processes
        if plot.category == "1":
            plot.rescale_upper_plot()
            stack["inclusive"] = plot.signal_processes['inclusive']

        ###########################
        # stack background processes
        ############################
        plot.painter.create_stack(stack, "stack")

        ###########################
        # normalize stacks by bin-width if set
        ###########################
        if plotConfig.settings["normalize_by_bin_width"]:
            plot.painter.subplot(0).normalizeByBinWidth()
            plot.painter.subplot(1).normalizeByBinWidth()

        ##################
        # setup ratio plot
        ##################
        plot.assemble_ratio()

        ##################
        # setup axis range
        ##################
        plot.set_axis_range()

        ##################
        # setup axis labels
        ##################
        plot.set_axis_labels()

        ##################
        # draw subplots.
        ##################
        plot.draw_subplots()

        ##################
        # create legends #
        ##################

        plot.set_upper_legend()

        plot.set_ratio_legend()

        ##################
        # plot line in top plot
        ##################
        
        plot.draw_lines()

        ##################
        # draw additional labels
        ##################
        plot.painter.DrawCMS(preliminary=False)
        if era == "2016":
            plot.painter.DrawLumi("35.9 fb^{-1} (2016, 13 TeV)", textsize=0.5)
        elif era == "2017":
            plot.painter.DrawLumi("41.5 fb^{-1} (2017, 13 TeV)", textsize=0.5)
        elif era == "2018":
            plot.painter.DrawLumi("59.7 fb^{-1} (2018, 13 TeV)", textsize=0.5)
        elif era == "all":
            # (35.9 + 41.5 + 59.7)
            plot.painter.DrawLumi("137.2 fb^{-1} (13 TeV)", textsize=0.5)
        else:
            logger.critical("Era {} is not implemented.".format(args.era))
            raise Exception

        plot.painter.DrawChannelCategoryLabel(
            "%s, %s" % (plotConfig.channel_labels[channel],
                        get_label_for_category(category, plotConfig.tag)),
            begin_left=None,
            textsize=0.026)
        
        # save plot
        postfix = "prefit" if "prefit" in plotConfig.inputfile else "postfit" if "postfit" in plotConfig.inputfile else "undefined"
        plot.painter.save(
            "%s/%s_%s_%s_%s.%s" %
            (args.outputfolder, era, channel, category, postfix, "png"))
        plot.painter.save(
            "%s/%s_%s_%s_%s.%s" %
            (args.outputfolder, era, channel, category, postfix, "pdf"))
        # work around to have clean up seg faults only at the end of the
        # script
        #plots.append(plot)


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_plot_shapes.log".format(args.era), logging.CRITICAL)
    main(args)
