#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        "label": "gg#rightarrowH + qq#rightarrowH"
    },
    "ggH": {
        "style": "ggH",
        "label": "gg#rightarrowH"
    },
    "ggH_hww": {
        "style": "ggH",
        "label": "gg#rightarrowH"
    },
    "qqH": {
        "style": "qqH",
        "label": "qq#rightarrowH"
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
            "displayname": "ggH 0-jet, p_{T}^{H} [0,10]",
            "signals": ["ggH_0J_PTH_0_10_htt"]
        },
        "101": {
            "style": "inclusive",
            "displayname": "ggH 0-jet, p_{T}^{H} > 10",
            "signals": ["ggH_0J_PTH_GT10_htt"]
        },
        "102": {
            "style": "inclusive",
            "displayname": "ggH 1-jet, p_{T}^{H} [0,60]",
            "signals": ["ggH_1J_PTH_0_60_htt"]
        },
        "103": {
            "style": "inclusive",
            "displayname": "ggH 1-jet, p_{T}^{H} [60,120]",
            "signals": ["ggH_1J_PTH_60_120_htt"]
        },
        "104": {
            "style": "inclusive",
            "displayname": "ggH 1-jet, p_{T}^{H} [120,200]",
            "signals": ["ggH_1J_PTH_120_200_htt"]
        },
        "105": {
            "style": "inclusive",
            "displayname": "ggH 2-jet, mjj [0,350], p_{T}^{H} [0,60]",
            "signals": ["ggH_GE2J_MJJ_0_350_PTH_0_60_htt"]
        },
        "106": {
            "style": "inclusive",
            "displayname": "ggH 2-jet, mjj [0,350], p_{T}^{H} [60,120]",
            "signals": ["ggH_GE2J_MJJ_0_350_PTH_60_120_htt"]
        },
        "107": {
            "style": "inclusive",
            "displayname": "ggH 2-jet, mjj [0,350], p_{T}^{H} [120,200]",
            "signals": ["ggH_GE2J_MJJ_0_350_PTH_120_200_htt"]
        },
        "108": {
            "style": "inclusive",
            "displayname": "ggH p_{T}^{H} [200,300]",
            "signals": ["ggH_PTH_200_300_htt"]
        },
        "109": {
            "style":
            "inclusive",
            "displayname":
            "ggH p_{T}^{H} > 300",
            "signals": [
                "ggH_PTH_300_450_htt", "ggH_PTH_450_650_htt",
                "ggH_PTH_GT650_htt"
            ]
        },
        "110": {
            "style":
            "inclusive",
            "displayname":
            "ggH 2-jet, mjj > 350, p_{T}^{H} [0,200]",
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
            "qqH 2-jet low mjj",
            "signals": [
                "qqH_FWDH_htt", "qqH_0J_htt", "qqH_1J_htt",
                "qqH_GE2J_MJJ_0_60_htt", "qqH_GE2J_MJJ_60_120_htt",
                "qqH_GE2J_MJJ_120_350_htt"
            ]
        },
        "201": {
            "style": "inclusive",
            "displayname": "qqH p_{T}^{H} > 200",
            "signals": ["qqH_GE2J_MJJ_GT350_PTH_GT200_htt"]
        },
        "202": {
            "style":
            "inclusive",
            "displayname":
            "qqH vbftopo mjj > 700",
            "signals": [
                "qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_htt",
                "qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_htt"
            ]
        },
        "203": {
            "style":
            "inclusive",
            "displayname":
            "qqH vbftopo mjj [350,700]",
            "signals": [
                "qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_htt",
                "qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_htt"
            ]
        },
        "111": {
            "style":
            "inclusive",
            "displayname":
            "ggH 2-jet, mjj [0,350]",
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
        if self.plotConfig.settings["linear"]:
            self.painter = dd.Plot([0.5, [0.5, 0.48]],
                                   "ModTDR",
                                   r=0.04,
                                   l=0.14,
                                   width=width)
        else:
            self.painter = dd.Plot([0.5, [0.3, 0.28]],
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
                                hists[36 * i + 12 * j + 3 * k +
                                      h] = self.rootfile.get(
                                          era, channel, category,
                                          "{}".format(subprocess))
                                if not isinstance(
                                        hists[36 * i + 12 * j + 3 * k + h],
                                        ROOT.TH1):
                                    hists.rm(36 * i + 12 * j + 3 * k + h)
            else:
                for i, subprocess in enumerate(
                        self.signal_processes[process]["histnames"]):
                    for j, era in enumerate(["2016", "2017", "2018"]):
                        for k, channel in enumerate(["et", "mt", "tt", "em"]):
                            hists[12 * i + 4 * j + k] = self.rootfile.get(
                                era, channel, self.category,
                                "{}".format(subprocess))
                            if not isinstance(hists[12 * i + 4 * j + k],
                                              ROOT.TH1):
                                hists.rm(12 * i + 4 * j + k)
            # now the the smallest binning of all histograms

            best_binning = set([
                hists[min(hists.keys())].GetBinLowEdge(i)
                for i in xrange(hists[min(hists.keys())].GetNbinsX() + 2)
            ])
            logger.debug("Initial binning: {}".format(best_binning))
            for histid in hists:
                test_binning = set([
                    hists[histid].GetBinLowEdge(i)
                    for i in xrange(hists[histid].GetNbinsX() + 2)
                ])
                best_binning = test_binning.intersection(best_binning)
                logger.debug("Initial binning: {}".format(best_binning))
            binning = np.array(
                sorted([x for x in list(best_binning) if x >= 0]))
            logger.debug("Final binning: {}".format(binning))
            # apply binning to all hists
            for histid in hists:
                hists[histid] = hists[histid].Rebin(
                    len(binning) - 1,
                    "{}_rebinned".format(hists[histid].GetName()), binning)
                logger.debug("Rebinned: {}".format(hists[histid]))
        else:
            for i, subprocess in enumerate(
                    self.signal_processes[process]["histnames"]):
                logger.warning("Getting {}".format(subprocess))
                hists[i] = self.rootfile.get(self.era, self.channel,
                                             self.category, subprocess)
                if not isinstance(hists[i], ROOT.TH1):
                    hists.rm(i)
        # if no files found nothing to do here
        if len(hists.keys()) == 0:
            logger.warning(
                "No histograms for {} found --> skipping".format(process))
        # addup all existing histograms
        else:
            logger.warning("found {} histograms".format(len(hists.keys())))
            basehist = hists[min(hists.keys())]
            if len(hists.keys()) >= 2:
                for hist in hists:
                    if hists[hist] == basehist:
                        continue
                    basehist.Add(hists[hist])
            self.painter.subplot(index).add_hist(basehist,
                                                 "{}".format(process))
            self.painter.subplot(index).add_hist(basehist,
                                                 "{}_top".format(process))
            self.painter.subplot(index).setGraphStyle(
                "{}".format(process),
                "hist",
                linecolor=self.signal_processes[process]["style"],
                linewidth=3)
            self.painter.subplot(index).setGraphStyle("{}_top".format(process),
                                                      "hist",
                                                      linecolor=0)

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
                                hists[36 * i + 12 * j + 3 * k +
                                      h] = self.rootfile.get(
                                          era, channel, category,
                                          "{}".format(subprocess))
                                if not isinstance(
                                        hists[36 * i + 12 * j + 3 * k + h],
                                        ROOT.TH1):
                                    hists.rm(36 * i + 12 * j + 3 * k + h)
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
                            hists[12 * i + 4 * j + k] = self.rootfile.get(
                                era, channel, self.category, subprocess)
                            if not isinstance(hists[12 * i + 4 * j + k],
                                              ROOT.TH1):
                                hists.rm(12 * i + 4 * j + k)
            # now the the smallest binning of all histograms
            best_binning = set([
                hists[min(hists.keys())].GetBinLowEdge(i)
                for i in xrange(hists[min(hists.keys())].GetNbinsX() + 2)
            ])
            for histid in hists:
                test_binning = set([
                    hists[histid].GetBinLowEdge(i)
                    for i in xrange(hists[histid].GetNbinsX() + 2)
                ])
                best_binning = test_binning.intersection(best_binning)
            binning = np.array(
                sorted([x for x in list(best_binning) if x >= 0]))
            logger.debug("Final binning: {}".format(binning))
            # apply binning to all hists
            for histid in hists:
                logger.debug("Rebinning: {}".format(hists[histid]))
                hists[histid] = hists[histid].Rebin(
                    len(binning) - 1,
                    "{}_rebinned".format(hists[histid].GetName()), binning)
        else:
            for i, subprocess in enumerate(
                    self.background_processes[process]["histnames"]):
                logger.warning("Getting {}".format(subprocess))
                hists[i] = self.rootfile.get(self.era, self.channel,
                                             self.category,
                                             "{}".format(subprocess))
                if not isinstance(hists[i], ROOT.TH1):
                    hists.rm(i)
        if len(hists.keys()) == 0:
            logger.warning(
                "No histograms for {} found --> skipping".format(process))
        # addup all existing histograms
        else:
            logger.warning("found {} histograms".format(len(hists.keys())))
            basehist = hists[min(hists.keys())]
            if len(hists.keys()) >= 2:
                for hist in hists:
                    if hists[hist] == basehist:
                        continue
                    basehist.Add(hists[hist])
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
                            hists_data[12 * j + 3 * k + h] = self.rootfile.get(
                                era, channel, category, "data_obs")
                            hists_bkg[12 * j + 3 * k + h] = self.rootfile.get(
                                era, channel, category, "TotalBkg")
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
                        hists_data[4 * j + k] = self.rootfile.get(
                            era, channel, self.category, "data_obs")
                        hists_bkg[4 * j + k] = self.rootfile.get(
                            era, channel, self.category, "TotalBkg")
            # now the the smallest binning of all histograms
            best_binning = set([
                hists_data[min(hists_data.keys())].GetBinLowEdge(i) for i in
                xrange(hists_data[min(hists_data.keys())].GetNbinsX() + 2)
            ])
            for histid in hists_data:
                test_binning = set([
                    hists_data[histid].GetBinLowEdge(i)
                    for i in xrange(hists_data[histid].GetNbinsX() + 2)
                ])
                best_binning = test_binning.intersection(best_binning)
            binning = np.array(
                sorted([x for x in list(best_binning) if x >= 0]))
            logger.debug("Final binning: {}".format(binning))
            # apply binning to all hists
            for histid in hists_data:
                logger.debug("Rebinning: {}".format(hists_data[histid]))
                hists_data[histid] = hists_data[histid].Rebin(
                    len(binning) - 1,
                    "{}_rebinned".format(hists_data[histid].GetName()),
                    binning)
            for histid in hists_bkg:
                logger.debug("Rebinning: {}".format(hists_bkg[histid]))
                hists_bkg[histid] = hists_bkg[histid].Rebin(
                    len(binning) - 1,
                    "{}_rebinned".format(hists_bkg[histid].GetName()), binning)
            data_obs = hists_data[min(hists_data.keys())]
            total_bkg = hists_bkg[min(hists_bkg.keys())]
            for hist in hists_data:
                if hists_data[hist] == data_obs:
                    continue
                data_obs.Add(hists_data[hist])
            for hist in hists_bkg:
                if hists_bkg[hist] == total_bkg:
                    continue
                total_bkg.Add(hists_bkg[hist])

        else:
            data_obs = self.rootfile.get(self.era, self.channel, self.category,
                                         "data_obs")
            total_bkg = self.rootfile.get(self.era, self.channel,
                                          self.category, "TotalBkg")
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
                signal = self.painter.subplot(2).get_hist(
                    "{}_signal".format(sublabel))
                signal.Add(self.painter.subplot(2).get_hist("total_bkg"))
                self.painter.subplot(2).add_hist(
                    signal, "bkg_{}_signal".format(sublabel))
                self.painter.subplot(2).add_hist(
                    signal, "bkg_{}_signal_top".format(sublabel))
                self.painter.subplot(2).setGraphStyle(
                    "bkg_{}_signal".format(sublabel),
                    "hist",
                    linecolor=styles.color_dict[color[i]],
                    linewidth=3)
                self.painter.subplot(2).setGraphStyle(
                    "bkg_{}_signal_top".format(sublabel), "hist", linecolor=0)
                self.ratiolist.extend([
                    "bkg_{}_signal".format(sublabel),
                    "bkg_{}_signal_top".format(sublabel)
                ])
        elif self.isSignal:
            for process in ["qqH", "ggH", "inclusive"]:
                signal = self.painter.subplot(2).get_hist(process)
                signal.Add(self.painter.subplot(2).get_hist("total_bkg"))
                self.painter.subplot(2).add_hist(signal,
                                                 "bkg_{}".format(process))
                self.painter.subplot(2).add_hist(signal,
                                                 "bkg_{}_top".format(process))
                self.painter.subplot(2).setGraphStyle(
                    "bkg_{}".format(process),
                    "hist",
                    linecolor=styles.color_dict[process],
                    linewidth=3)
                self.painter.subplot(2).setGraphStyle(
                    "bkg_{}_top".format(process), "hist", linecolor=0)
                self.ratiolist.extend(
                    ["bkg_{}".format(process), "bkg_{}_top".format(process)])
        self.ratiolist.append("data_obs")
        self.painter.subplot(2).normalize(self.ratiolist, "total_bkg")

    def set_axis_range(self):
        self.painter.subplot(0).setYlims(
            self.plotConfig.split_dict[self.channel],
            max(2 * self.painter.subplot(0).get_hist("data_obs").GetMaximum(),
                self.plotConfig.split_dict[self.channel] * 2))
        self.painter.subplot(2).setNYdivisions(3, 5)
        self.painter.subplot(2).setNXdivisions(5, 3)

        if self.plotConfig.tag == "stxs_stage1p1_15node":
            self.painter.subplot(2).setYlims(0.45, 2.55)
            if self.isSignal and self.channel == "em":
                self.painter.subplot(0).setYlims(1, 150000000)
        else:
            self.painter.subplot(2).setYlims(0.85, 1.25)
        if not self.linear:
            self.painter.subplot(1).setYlims(
                0.1, self.plotConfig.split_dict[self.channel])
            self.painter.subplot(1).setLogY()
        

        if not self.category == "1":
            self.painter.subplot(2).setXlims(0.0, 1.0)
            self.painter.subplot(0).setXlims(0.0, 1.0)
        else:
            self.painter.subplot(0).setLogY()
            self.painter.subplot(0).setYlims(1, 4500000000)
            self.painter.subplot(2).setXlims(0.0, 28.0)
            self.painter.subplot(0).setXlims(0.0, 28.0)
            self.painter.subplot(2).setYlims(0.95, 1.3)
            # self.painter.subplot(0).setYlims(
            # self.plotConfig.split_dict[self.channel],
            # max(1.5 * self.painter.subplot(0).get_hist("data_obs").GetMaximum(),
            #     self.plotConfig.split_dict[self.channel] * 1.5))
        if self.channel == "cmb" and self.plotConfig.tag == "stxs_stage1p1_15node":
            #if self.isSignal:
            #    self.painter.subplot(0).setYlims(1, 4500000000)
            self.painter.subplot(2).setYlims(0.95, 1.13)
            if self.category == "100":
                self.painter.subplot(2).setYlims(0.95, 1.1)
            if self.category == "101":
                self.painter.subplot(2).setYlims(0.95, 1.1)
            if self.category == "102":
                self.painter.subplot(2).setYlims(0.95, 1.18)
            if self.category == "103":
                self.painter.subplot(2).setYlims(0.95, 1.18)
            if self.category == "104":
                self.painter.subplot(2).setYlims(0.95, 1.18)
            if self.category == "105":
                self.painter.subplot(2).setYlims(0.95, 1.1)
            if self.category == "106":
                self.painter.subplot(2).setYlims(0.95, 1.18)
            if self.category == "107":
                self.painter.subplot(2).setYlims(0.95, 1.18)
            if self.category == "108":
                self.painter.subplot(2).setYlims(0.95, 1.18)
            if self.category == "109":
                self.painter.subplot(2).setYlims(0.95, 1.18)
            if self.category == "110":
                self.painter.subplot(2).setYlims(0.95, 1.25)
            if self.category == "111":
                self.painter.subplot(2).setYlims(0.95, 1.1)
            if self.category == "200":
                self.painter.subplot(2).setYlims(0.90, 1.2)
            if self.category == "201":
                self.painter.subplot(2).setYlims(0.95, 1.25)
            if self.category == "202":
                self.painter.subplot(2).setYlims(0.90, 1.45)
            if self.category == "203":
                self.painter.subplot(2).setYlims(0.95, 1.2)

    def set_axis_labels(self):
        if not self.linear:
            self.painter.subplot(1).setYlabel(
                "")  # otherwise number labels are not drawn on axis
        if self.plotConfig.tag == "stxs_stage0" and self.category == "1":
            self.painter.subplot(2).setXlabel("2D discriminator bin index")
        else:
            self.painter.subplot(2).setXlabel("NN output")
        if self.plotConfig.settings["normalize_by_bin_width"]:
            self.painter.subplot(0).setYlabel("dN/d(NN output)")
        else:
            self.painter.subplot(0).setYlabel("N_{events}")

        self.painter.subplot(2).setYlabel("")
        self.painter.scaleYLabelSize(0.6)
        self.painter.scaleYTitleOffset(1.1)

    def draw_subplots(self):
        procs_to_draw_0 = ["stack", "total_bkg", "data_obs"]

        if self.isSignal:
            suffix = ["", "_top"]
            signals = []
            for suf in suffix:
                signals.extend([
                    "{}{}".format(x, suf)
                    for x in self.signal_processes.keys()
                ])
            procs_to_draw_0 = procs_to_draw_0 + signals

        self.painter.subplot(0).Draw(procs_to_draw_0)
        if not self.plotConfig.settings["linear"]:
            self.painter.subplot(1).Draw(procs_to_draw_0)
        self.painter.subplot(2).Draw(self.ratiolist)

    def set_upper_legend(self):
        suffix = ["", "_top"]
        for i in range(2):
            self.painter.add_legend(width=0.62, height=0.18)
            # set background labels
            for process in collections.OrderedDict(reversed(list(self.background_processes.items()))):
                try:
                    self.painter.legend(i).add_entry(
                        0, process, styles.legend_label_dict[process.replace(
                            "TTL", "TT").replace("VVL", "VV")], 'f')
                except BaseException:
                    pass
            # set signal
            for signal in self.signal_processes:
                index = 0 if self.linear else 1
                try:
                    self.painter.legend(i).add_entry(
                        index, "{}{}".format(signal, suffix[i]),
                        self.signal_processes[signal]["label"], 'l')
                except BaseException:
                    pass
            self.painter.legend(i).add_entry(0, "total_bkg", "Bkg. unc.", 'f')
            self.painter.legend(i).add_entry(0, "data_obs", "Observed", 'PEL')
            self.painter.legend(i).setNColumns(3)
        self.painter.legend(0).Draw()
        self.painter.legend(1).setAlpha(0.0)
        self.painter.legend(1).Draw()

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
        suffix = ["", "_top"]
        for i in range(2):
            self.painter.add_legend(reference_subplot=2,
                                    pos=1,
                                    width=0.7,
                                    height=0.14)
            self.painter.legend(i + 2).add_entry(0, "data_obs", "Observed",
                                                 'PEL')
            self.painter.legend(i + 2).add_entry(0, "total_bkg", "Bkg. unc.",
                                                 'f')
            if self.isSignal and self.plotConfig.settings["exact_signals"]:
                main_signal_label = ""
                if len(
                        get_signal_for_category(
                            self.category)["displayname"].split(", ")) > 2:
                    main_signal_label = "#splitline{%s}{%s (#mu=%s) + bkg.}" % (
                        ", ".join(
                            get_signal_for_category(
                                self.category)["displayname"].split(", ")[:2]),
                        get_signal_for_category(
                            self.category)["displayname"].split(", ")[2],
                        mu_dict[self.category])
                else:
                    main_signal_label = "#splitline{%s}{(#mu=%s) + bkg.}" % (
                        get_signal_for_category(self.category)["displayname"],
                        mu_dict[self.category])
                self.painter.legend(i + 2).add_entry(
                    int(not self.linear),
                    "{}{}".format("main_signal",
                                  suffix[0]), main_signal_label, 'l')
                self.painter.legend(i + 2).add_entry(
                    int(not self.linear),
                    "{}{}".format("ggH_rest_signal", suffix[i]),
                    "ggH{} + bkg.".format(
                        " (other)" if "ggH" in get_signal_for_category(
                            self.category)["displayname"] else ""), 'l')
                self.painter.legend(i + 2).add_entry(
                    int(not self.linear),
                    "{}{}".format("qqH_rest_signal", suffix[i]),
                    "qqH{} + bkg.".format(
                        " (other)" if "qqH" in get_signal_for_category(
                            self.category)["displayname"] else ""), 'l')
                self.painter.legend(i + 2).setNColumns(2)
            elif self.isSignal:
                self.painter.legend(i + 2).add_entry(
                    int(not self.linear), "{}{}".format("ggH", suffix[i]),
                    "{} + bkg.".format(signal_labels["ggH"]["label"]), 'l')
                self.painter.legend(i + 2).add_entry(
                    int(not self.linear), "{}{}".format("qqH", suffix[i]),
                    "{} + bkg.".format(signal_labels["qqH"]["label"]), 'l')
                self.painter.legend(i + 2).add_entry(
                    int(not self.linear), "{}{}".format("inclusive", suffix[i]),
                    "{} + bkg.".format(signal_labels["inclusive"]["label"]), 'l')
                self.painter.legend(i + 2).setNColumns(2) 
        self.painter.legend(3).setAlpha(0.0)
        self.painter.legend(2).setAlpha(0.0)
        self.painter.legend(2).Draw()
        self.painter.legend(3).Draw()


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
            "single_category": args.single_category
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

    def setup_dummy(self, single_category, channel):
        if self.tag == "stxs_stage0" and single_category == "1":
            # special for 2D category
            return ROOT.TH1F("dummy_{}_{}".format(single_category, channel),
                             "dummy_{}_{}".format(single_category,
                                                  channel), 28, 0.0, 28.0)
        else:
            return ROOT.TH1F("dummy_{}_{}".format(single_category, channel),
                             "dummy_{}_{}".format(single_category,
                                                  channel), 5, 0.0, 1.0)

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
                if self.channels == ["cmb"] and self.era == "all":
                    
                    single_plot.add_background(
                        "REST", styles.legend_label_dict["REST"],
                        styles.color_dict["REST"], [
                            "VVL", "W", "TTL", "ZL", "qqH_hww", "ggH_hww",
                            "VH_htt", "ZH_htt", "WH_htt", "ttH_htt"
                        ])
                    single_plot.add_background(
                        "jetFakes", styles.legend_label_dict["jetFakesCMB"],
                        styles.color_dict["QCD"], ["QCD", "jetFakes"])
                    single_plot.add_background("EMB",styles.legend_label_dict["EMBCMB"], styles.color_dict["EMB"],["EMB"])
                    
                else:
                    for process in bkg_processes:
                        single_plot.add_background(
                            process, styles.legend_label_dict[process],
                            styles.color_dict[process], [process])

                # if category is not a background category, include signals
                if category not in self.background_categories:
                    self.categories[channel][category][
                        "inclusive"] = self.setup_dummy(category, channel)
                    if not self.channels == ["cmb"] and not self.era == "all":
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
                        color = "inclusive"
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
                                               styles.color_dict[color],
                                               main_signals, True)
                        single_plot.add_signal(
                            "ggH_rest_signal", "ggH{}".format(
                                " (other)" if "ggH" in get_signal_for_category(
                                    category)["displayname"] else ""),
                            styles.color_dict["ggH"], merge_signals_ggH, False)
                        single_plot.add_signal(
                            "qqH_rest_signal", "qqH{}".format(
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
                            styles.color_dict["dummy"], ["qqH_htt", "ggH_htt"], True)
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
        #plot.print_plot_settings()
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
        if plotConfig.settings["linear"]:
            index = 0
        else:
            index = 1
        for i in [index, 2]:
            for signal in plot.signal_processes:
                plot.add_signal_hist(signal, i)

        ##################
        # get observed data
        # and total background histograms
        # blind data is option is set
        ##################
        plot.add_data()

        # stack background processes
        plot.painter.create_stack(plot.background_processes, "stack")

        # normalize stacks by bin-width
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
        # draw additional labels
        ##################
        plot.painter.DrawCMS()
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
    setup_logging("{}_plot_shapes.log".format(args.era), logging.DEBUG)
    main(args)
