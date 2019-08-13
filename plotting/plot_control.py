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
    parser.add_argument("--emb", action="store_true", help="Embedded prefix")
    parser.add_argument("--ff", action="store_true", help="Use fake-factors")
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

    parser.add_argument("--filename-prefix", type=str, default="", help="filename prefix")
    parser.add_argument("--www", action="store_true", help="webplotting")
    parser.add_argument("--www-dir", type=str, default=None,
        help='Directory structure where the plots will be uploaded. {date} expressions will be replaced by date.')
    parser.add_argument("--www-no-overwrite", action='store_true', default=False, help="Don't overwrite remote file. [Default: %(default)s]")
    parser.add_argument("--no-overwrite", "--keep-both", "--keep", "-k", action='store_true', default=False, help="Don't overwrite output file. [Default: %(default)s]")
    parser.add_argument("--log-level", default="debug", help="log level. [Default: %(default)s]")
    parser.add_argument("--redo-cache", action="store_true",
                        help="Do not use inputs from cached trees, but overwrite them. [Default: False for absolute paths, True for relative paths]")
    parser.add_argument("--no-signal", action="store_true", help="Drop the signals")

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
    "colors": ["#B7B7B7", "#000000"],
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
    "y_subplot_lims": [0.62, 1.5],
    "subplot_lines": [0.8, 1.0, 1.2],
    # "y_subplot_lims": [0.0, 2.0],
    # "subplot_lines": [0.5, 1.0, 1.5]
    "y_rel_lims": [0.9, 1.3],
    "y_subplot_label": "#scale[0.8]{Ratio to Bkg.}",
}


def main(args):
    bkg_processes_names = ["ztt", "zl", "zj", "wj", "ttt", "ttj",
                           "qcd", "vv", "ewk"]  # enforced by HarryPlotter
    bkg_processes = ["ZTT", "ZL", "ZJ", "W", "TTT", "TTJ",
                     "QCD", "VV", "EWKZ"]  # names in ROOT file
    signal_processes_names = ["htt125", "ggh125",
                              "qqh125"]  # enforced by HarryPlotter
    signal_processes = ["HTT", "qqH", "ggH"]  # name in ROOT file

    if args.emb and args.ff:
        bkg_processes_names = [
         "emb", "zll", "ttl", "vvl", "fakes"
        ]
        bkg_processes = ["EMB", "ZL", "TTL", "VVL", "jetFakes"]
    elif args.emb:
        bkg_processes_names = ["emb", "zll","zj", "ttl", "ttj","vvl", "vvj", "w", "qcd"]
        bkg_processes = ["EMB", "ZL", "ZJ","TTL", "TTJ","VVL", "VVJ", "W", "QCD"]
    elif args.ff:
        bkg_processes_names = [
            "ztt", "zll", "ttt", "ttl", "vvt", "vvl", "fakes"
        ]  # enforced by HarryPlotter
        bkg_processes = ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL", "jetFakes"]
    else:
        bkg_processes_names = [
            "ztt", "zll","zj","ttl", "ttt","ttj","vvl","vvt","vvj","w","qcd"]
        bkg_processes = ["ZTT", "ZL", "ZJ","TTL","TTT", "TTJ", "VVL","VVT","VVJ","W","QCD"]

    if args.no_signal:
        signal_processes_names = []
        signal_processes = []

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

    if args.www:
        config_template['www'] = ''
    if args.www_dir:
        config_template['www_dir'] = args.www_dir
    if args.www_no_overwrite:
        config_template['www_no_overwrite'] = True
        config_template['no_overwrite'] = True
    if args.no_overwrite:
        config_template['no_overwrite'] = True
    if args.redo_cache:
        config_template['redo_cache'] = True

    if args.filename_prefix != '':
        args.filename_prefix = args.filename_prefix if args.filename_prefix[0] == '_' else '_' + args.filename_prefix
    categories = args.categories
    channel = args.channel
    analysis = args.analysis
    era = args.era

    if "2016" in era:
        config_template['lumi'] = [35.9]
        config_template['year'] = '2016'
    elif "2017" in era:
        config_template['lumi'] = [41.5]
        config_template['year'] = '2017'
    elif "2018" in era:
        config_template['lumi'] = [59.7]
        config_template['year'] = '2018'

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
                [channel, category, analysis, era, variable, mass]) + args.filename_prefix
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

    config["colors"] = [x if (x != 'ttl') else "kit_blau_3" for x in config["colors"]]
    for key in configs[0]:
        print(key, configs[0][key])
    higgsplot.HiggsPlotter(
        list_of_config_dicts=configs,
        list_of_args_strings=[""],
        n_processes=args.num_processes)


if __name__ == "__main__":
    args = parse_arguments()
    if args.log_level == 'debug':
        ll = logging.DEBUG
    else:
        ll = logging.INFO
    setup_logging("plot_control.log", ll)
    main(args)
