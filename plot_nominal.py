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
    parser.add_argument("--emb", action="store_true", help="Embedded prefix")
    parser.add_argument("--ff", action="store_true", help="Use fake-factors")
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
        required=False, default=None,
        help="Categories")
    parser.add_argument("--era", type=str, default="Run2017ReReco31Mar", help="Era")
    parser.add_argument(
        "--lumi", type=float, default=41.5, help="Integrated Luminosity")
    parser.add_argument("--mass", type=str, default="125", help="Mass")
    parser.add_argument(
        "--additional-arguments",
        type=str,
        default="",
        help="Additional higgsplot.py arguments")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="plots",
        help="Output directory for plots")
    parser.add_argument(
        "--y-log",
        action="store_true",
        default=False,
        help="Use logarithmic y-axis")
    parser.add_argument(
        "--channels", nargs="+", type=str, required=True, help="Channel")
    parser.add_argument(
        "--analysis", type=str, default="smhtt", help="Analysis")
    parser.add_argument(
        "--shapes",
        type=str,
        default="Run2017-analysis/shapes.root",
        help="ROOT files with shapes of processes")
    parser.add_argument(
        "--x-label", type=str, default=None, help="Label on x-axis")
    parser.add_argument("--chi2", action="store_true", help="Print chi2 value")
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
    "colors": ["#B7B7B7", "#000000"],
    "filename": "",
    "files": [None],
    "labels": ["", ""],
    "legend": [0.4, 0.52, 0.88, 0.83],
    "legend_cols": 2,
    "legend_markers": ["ELP", "ELP"],
    "stacks": ["ratio_bkg", "ratio_data"],
    "markers": ["E2", "P"],
    "formats": ["pdf", "png"],
    "title": "",
    "cms": True,
    "extra_text": "Preliminary",
    "energies": [13],
    "year": "2017",
    "nicks_blacklist": ["noplot"],
    "analysis_modules": ["Ratio"],
    "ratio_result_nicks": ["ratio_Bkg", "ratio_Data"],
    "y_subplot_lims": [0.8, 1.2],
    "y_label": "N_{evts}",
    "y_subplot_label": "#scale[0.8]{Ratio to Bkg.}",
    "subplot_lines": [0.9, 1.0, 1.1]
}

logvars = []


def main(args):
	'''
    if args.emb:
        bkg_processes_names = [
         "emb", "zll","ttl", "tt", "vv","w", "qcd"
        ]
        bkg_processes = ["EMB", "ZLL", "TT", "VV", "W", "QCD"]  # names in ROOT file

    else:
        bkg_processes_names = [
            "ztt", "zll", "tt", "vv", "ewk", "w", "qcd"
        ]  # enforced by HarryPlotter
        bkg_processes = ["ZTT", "ZLL", "TT", "VV", "EWK", "W", "QCD"]  # names in ROOT file
    '''
    if args.emb:
        bkg_processes_names = [
         "emb", "zl","zj", "ttl", "ttj", "vvl", "vvj","w", "qcd"
        ]
        bkg_processes = ["EMB", "ZL", "ZJ", "TTL", "TTJ", "VVL", "VVJ", "W", "QCD"]  # names in ROOT file

    else:
        bkg_processes_names = [
            "ztt", "zl","zj", "ttt", "ttj", "vvt", "vvj", "ewk", "w", "qcd"
        ]  # enforced by HarryPlotter
        bkg_processes = ["ZTT", "ZL", "ZJ", "TTT", "TTJ", "VVT", "VVJ", "EWK", "W", "QCD"]  # names in ROOT file
    if args.ff:
		bkg_processes = [x for x in bkg_processes if x not in ["ZJ","TTJ","VVJ","W","QCD"]]
		bkg_processes_names = [x for x in bkg_processes_names if x not in ["zj","ttj","vvj","w","qcd"]]
		bkg_processes.append("jetFakes")
		bkg_processes_names.append("fakes")
	
    qcd_scale_factors = {"mt": 1.0, "et": 1.0, "tt": 1.0, "em": 1.0}
    channels = args.channels
    analysis = args.analysis
    era = args.era
    output_dir = args.output_dir
    y_log = args.y_log
    mass = args.mass
    variables = args.variables
    if args.categories is None:
        args.categories = [channels[0]+"_"+v for v in variables]
    categories = [c for c in args.categories]
    #~ categories = [args.categories[0].replace("m_vis", v) for v in variables]
    if "all" in variables:
        variables = ["mt_1","mt_2", "pt_1","pt_2", "eta_1", "eta_2", "m_vis", "ptvis", "npv", "njets", "nbtag", "jpt_1", "jpt_2", "jeta_1", "jeta_2", "met", "mjj", "dijetpt", "pZetaMissVis", "m_1", "m_2", "decayMode_1", "decayMode_2", "iso_1", "iso_2", "rho", "mt_tot", "d0_1", "d0_2", "dZ_1", "dZ_2"]

    args.categories = [channels[0]+"_"+v for v in variables]
    categories = [c for c in args.categories]

    configs = []
    for channel in channels:
        for variable, category in zip(variables, categories):
            config = deepcopy(config_template)

            if args.chi2:
                config["analysis_modules"].append("AddHistograms")
                config["analysis_modules"].append("Chi2Test")
                config["add_nicks"] = [" ".join(bkg_processes_names)]
                config["add_result_nicks"] = ["tot_background_noplot"]
                config["chi2test_nicks"] = ["tot_background_noplot data"]
                config["chi2test_compare"] = ["UW CHI2/NDF"]

            config["files"] = [args.shapes]
            config["lumis"] = [args.lumi]
            config["output_dir"] = output_dir+"/"+channel
            config["y_log"] = True if (variable in logvars) else False
            config["y_rel_lims"] = [0.9, 50] if y_log else [0.9, 1.3]
            #~ config["y_lims"] = [10.,2e11]
            config["markers"] = ["HIST"] * len(bkg_processes_names) + ["P"] + config["markers"]
            config["legend_markers"] = ["F"] * (len(bkg_processes_names))  + ["ELP"] + config["legend_markers"]
            config["labels"] = bkg_processes_names + ["data"
                                                      ] + config["labels"]
            config["colors"] = bkg_processes_names + ["data"
                                                      ] + config["colors"]
            config["nicks"] = bkg_processes_names + ["data"]
            config["x_expressions"] = [
                "#" + "#".join([
                    channel, category, process, analysis, "Run2017ReReco31Mar", variable, mass
                ]) + "#" for process in bkg_processes
            ] + [
                "#" + "#".join([
                    channel, category, "data_obs", analysis, "Run2017ReReco31Mar", variable,
                    mass
                ]) + "#"
            ]
            if args.emb == False:
                config["filename"] = "_".join(
                    [channel, category, analysis, "Run2017ReReco31Mar", variable, mass])
            else:
                config["filename"] = "_".join(
                    [channel, category, analysis, "Run2017ReReco31Mar", variable, mass,"emb"])
            if args.ff:
				config["filename"] = config["filename"]+"_ff"
            if not args.x_label == None:
                config["x_label"] = args.x_label
            else:
                config["x_label"] = "_".join([channel, variable])
            #~ config["title"] = "_".join(["channel", channel])
            config["stacks"] = ["mc"] * len(bkg_processes_names) + [
                "data"
            ] + config["stacks"]
            config["ratio_denominator_nicks"] = [
                " ".join(bkg_processes_names)
            ] * 2
            config["ratio_numerator_nicks"] = [
                " ".join(bkg_processes_names), "data"
            ]
            #config["scale_factors"] = [1.0  if x != "qcd" else qcd_scale_factors[channel] for x in bkg_processes_names] + [1.0]
            configs.append(config)

    for key in configs[0]:
        print(key, configs[0][key])
    higgsplot.HiggsPlotter(
        list_of_config_dicts=configs,
        list_of_args_strings=[args.additional_arguments],
        n_processes=args.num_processes)


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("plot_nominal.log", logging.DEBUG)
    main(args)
