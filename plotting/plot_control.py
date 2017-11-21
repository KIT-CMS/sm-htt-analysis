#!/usr/bin/env python
# -*- coding: utf-8 -*-

import HiggsAnalysis.KITHiggsToTauTau.plotting.higgsplot as higgsplot

import argparse
from copy import deepcopy

import logging
logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Plot categories using HarryPlotter from shapes produced by shape-producer module."
    )

    parser.add_argument(
        "-v",
        "--variables",
        nargs="+",
        type=str,
        required=True,
        help="Variable on x-axis")
    parser.add_argument(
        "-c",
        "--categories",
        nargs="+",
        type=str,
        required=True,
        help="Categories")
    parser.add_argument("--era", type=str, default="Run2016", help="Era")
    parser.add_argument("--mass", type=str, default="125", help="Mass")
    parser.add_argument("--channel", type=str, required=True, help="Channel")
    parser.add_argument(
        "--analysis", type=str, default="smhtt", help="Analysis")
    parser.add_argument(
        "--shapes",
        type=str,
        default="shapes.root",
        help="ROOT files with shapes of processes")
    parser.add_argument(
        "--x-label", type=str, default=None, help="Label on x-axis")
    parser.add_argument(
        "--num-processes",
        type=int,
        default=10,
        help="Number of processes used for plotting")
    parser.add_argument(
        "--scale-signal",
        type=int,
        default=1,
        help="Scale the signal yield by this factor")

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


config_template = {
    "colors": ["#000000", "#000000"],
    "filename": "",
    "files": [None],
    "labels": ["", ""],
    "legend": [0.23, 0.68, 0.9, 0.83],
    "legend_cols": 3,
    "legend_markers": ["ELP", "ELP"],
    "stacks": ["ratio_bkg", "ratio_data"],
    "markers": ["E2", "E"],
    "formats": ["pdf", "png"],
    "title": "",
    "lumis": [35.87],
    "energies": [13],
    "year": "2016",
    "analysis_modules": ["ScaleHistograms", "Ratio"],
    "ratio_result_nicks": ["ratio_Bkg", "ratio_Data"],
    "y_subplot_lims": [0.0, 2.0],
    "y_rel_lims": [0.9, 1.3],
    "y_subplot_label": "#scale[0.8]{Ratio to Bkg.}",
    "subplot_lines": [0.5, 1.0, 1.5]
}


def main(args):
    bkg_processes_names = ["ztt", "zl", "zj", "wj", "ttt", "ttj",
                           "qcd", "vv"]  # enforced by HarryPlotter
    bkg_processes = ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ",
                     "QCD", "VV"]  # names in ROOT file
    signal_processes_names = ["htt125", "ggh125",
                              "qqh125"]  # enforced by HarryPlotter
    signal_processes = ["HTT", "qqH", "ggH"]  # name in ROOT file

    scale_signal = args.scale_signal
    config_template["scales"] = scale_signal
    config_template["scale_nicks"] = signal_processes_names
    if scale_signal != 1:
        postfix = "_" + str(scale_signal)
    else:
        postfix = ""
    signal_processes_labels = [
        label + postfix for label in signal_processes_names
    ]

    categories = args.categories
    channel = args.channel
    analysis = args.analysis
    era = args.era
    mass = args.mass
    variables = args.variables

    configs = []
    for category in categories:
        for variable in variables:
            config = deepcopy(config_template)
            config["files"] = [args.shapes]
            config["markers"] = ["HIST"] * len(bkg_processes_names) + [
                "LINE"
            ] * len(signal_processes_names) + ["E"] + config["markers"]
            config["legend_markers"] = ["F"] * len(
                bkg_processes_names) + ["L"] * len(signal_processes_names) + [
                    "ELP"
                ] + config["legend_markers"]
            config[
                "labels"] = bkg_processes_names + signal_processes_labels + [
                    "data"
                ] + config["labels"]
            config["colors"] = bkg_processes_names + signal_processes_names + [
                "data"
            ] + config["colors"]
            config["nicks"] = bkg_processes_names + signal_processes_names + [
                "data"
            ]
            config["x_expressions"] = [
                "#" + "#".join([
                    channel, category, process, analysis, era, variable, mass
                ]) + "#" for process in bkg_processes + signal_processes
            ] + [
                "#" + "#".join([
                    channel, category, "data_obs", analysis, era, variable,
                    mass
                ]) + "#"
            ]
            config["filename"] = "_".join(
                [channel, category, analysis, era, variable, mass])
            if not args.x_label == None:
                config["x_label"] = args.x_label
            else:
                config["x_label"] = "_".join([channel, variable])
            config["title"] = "_".join(["channel", channel])
            config["stacks"] = ["mc"] * len(
                bkg_processes_names) + signal_processes_names + [
                    "data"
                ] + config["stacks"]
            config["ratio_denominator_nicks"] = [
                " ".join(bkg_processes_names)
            ] * 2
            config["ratio_numerator_nicks"] = [
                " ".join(bkg_processes_names), "data"
            ]
            configs.append(config)

    for key in configs[0]:
        print(key, configs[0][key])
    higgsplot.HiggsPlotter(
        list_of_config_dicts=configs,
        list_of_args_strings=[""],
        n_processes=args.num_processes)


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("plot_nominal.log", logging.DEBUG)
    main(args)
