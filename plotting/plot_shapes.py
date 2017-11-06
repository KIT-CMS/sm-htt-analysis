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
        "Plot categories using HarryPlotter from shapes created by CombineHarvester."
    )

    parser.add_argument(
        "-f",
        "--folders",
        nargs="+",
        type=str,
        required=True,
        help="Folders to be plotted in input file")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="ROOT files with shapes of processes")
    parser.add_argument(
        "--title", type=str, default="#mu#tau", help="Plot title")
    parser.add_argument(
        "--x-label",
        type=str,
        default="Exclusive probability",
        help="Plot x label")
    parser.add_argument(
        "--num-processes",
        type=int,
        default=10,
        help="Number of processes used for plotting")

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
    "analysis_modules": ["Ratio"],
    "ratio_result_nicks": ["ratio_Bkg", "ratio_Data"],
    "y_subplot_lims": [0.5, 1.5],
    "y_rel_lims": [0.9, 1.3],
    "y_subplot_label": "#scale[0.8]{Ratio to Bkg.}",
    "subplot_lines": [0.5, 1.0, 1.5]
}


def main(args):
    bkg_processes_names = ["ztt", "zl", "zj", "wj", "ttt", "ttj",
                           "qcd"]  # enforced by HarryPlotter
    bkg_processes = ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ",
                     "QCD"]  # names in ROOT file
    signal_processes_names = ["htt125"]  # enforced by HarryPlotter
    signal_processes = ["HTT"]  # name in ROOT file

    configs = []
    for folder in args.folders:
        config = deepcopy(config_template)
        config["files"] = [args.input]
        config["markers"] = ["HIST"] * len(bkg_processes_names) + [
            "LINE"
        ] * len(signal_processes_names) + ["E"] + config["markers"]
        config["legend_markers"] = ["F"] * len(bkg_processes_names) + [
            "L"
        ] * len(signal_processes_names) + ["ELP"] + config["legend_markers"]
        config["labels"] = bkg_processes_names + signal_processes_names + [
            "data"
        ] + config["labels"]
        config["colors"] = bkg_processes_names + signal_processes_names + [
            "data"
        ] + config["colors"]
        config[
            "nicks"] = bkg_processes_names + signal_processes_names + ["data"]
        config["folders"] = [folder]
        config[
            "x_expressions"] = bkg_processes + signal_processes + ["data_obs"]
        config["filename"] = folder
        config["x_label"] = args.x_label
        config["title"] = args.title
        config["stacks"] = ["mc"] * len(
            bkg_processes_names) + signal_processes_names + [
                "data"
            ] + config["stacks"]
        config["ratio_denominator_nicks"] = [" ".join(bkg_processes_names)] * 2
        config["ratio_numerator_nicks"] = [
            " ".join(bkg_processes_names), "data"
        ]

        if "HTT" in folder:
            config["y_log"] = True
            config["y_lims"] = [1e0, 1e6]

        configs.append(config)

    higgsplot.HiggsPlotter(
        list_of_config_dicts=configs,
        list_of_args_strings=[""],
        n_processes=args.num_processes)


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("plot_shapes.log", logging.DEBUG)
    main(args)
