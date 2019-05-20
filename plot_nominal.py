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
    parser.add_argument("--comparison", action="store_true", help="Plot Embedded - MC comparison. --emb has to be set.")

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
        "--categories",
        nargs="+",
        type=str,
        required=False, default=None,
        help="Categories")
    parser.add_argument("--era", type=str, default="Run2018", help="Era")
    parser.add_argument(
        "--lumi", type=float, default=None, help="Integrated Luminosity")
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
        "-c",
        "--channels", nargs="+", type=str, required=True, help="Channel")
    parser.add_argument(
        "--analysis", type=str, default="smhtt", help="Analysis")
    parser.add_argument(
        "--shapes",
        type=str,
        default=None,
        help="ROOT files with shapes of processes")
    parser.add_argument(
        "--x-label", type=str, default=None, help="Label on x-axis")
    parser.add_argument("--chi2", action="store_true", help="Print chi2 value")
    parser.add_argument(
        "--num-processes",
        type=int,
        default=24,
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
    "nicks_blacklist": ["noplot"],
    "analysis_modules": ["Ratio"],
    "ratio_result_nicks": ["ratio_Bkg", "ratio_Data"],
    "y_subplot_lims": [0.62, 1.5],
    "y_label": "N_{evts}",
    "y_subplot_label": "#scale[0.8]{Ratio to Bkg.}",
    "subplot_lines": [0.8, 1.0, 1.2]
}

logvars = ["nbtag","njets","jpt_1","jpt_2"]


def main(args):

    if args.emb and args.ff:
        bkg_processes_names = [
         "emb", "zll", "ttl", "vvl", "fakes"
        ]
        signal=["ggH125","qqH125"]
        signal_names=["ggh","qqh"]

        bkg_processes = ["EMB", "ZL", "TTL", "VVL", "jetFakes"]  # names in ROOT file
    elif args.emb:
        bkg_processes_names = ["emb", "zll","zj", "ttl", "ttj","vvl", "vvj", "w", "qcd"]
        signal_names=["ggh","qqh"]
        bkg_processes = ["EMB", "ZL", "ZJ","TTL", "TTJ","VVL", "VVJ", "W", "QCD"]
        signal=["ggH125","qqH125"]
    elif args.ff:
        bkg_processes_names = [
            "ztt", "zll", "ttt", "ttl", "vvt", "vvl", "ewk", "fakes"
        ]  # enforced by HarryPlotter
        bkg_processes = ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL", "EWK", "jetFakes"]  # names in ROOT file
    else:
        bkg_processes_names = [
            "ztt", "zll","zj","ttl", "ttt","ttj","vvl","vvt","vvj","w","qcd"]
        signal_names=["ggh","qqh"]
        bkg_processes = ["ZTT", "ZL", "ZJ","TTL","TTT", "TTJ", "VVL","VVT","VVJ","W","QCD"]
        signal=["ggH125","qqH125"]
    channels = args.channels
    analysis = args.analysis
    era = args.era
    if args.lumi is None:
        if "2016" in era:
            lumi = 35.9
        elif "2017" in era:
            lumi = 41.5
        elif "2018" in era:
            lumi = 59.7
    else:
        lumi=args.lumi
    output_dir = args.output_dir
    y_log = args.y_log
    mass = args.mass
    variables = args.variables
    categories = [c for c in args.categories] if args.categories is not None else None
    if "all" in variables:
        variables = ["mt_1","mt_2", "pt_1","pt_2", "eta_1", "eta_2", "m_vis", "ptvis", "npv", "njets", "nbtag", "jpt_1", "jpt_2", "jeta_1", "jeta_2", "met", "mjj", "dijetpt", "pZetaMissVis", "m_1", "m_2", "decayMode_1", "decayMode_2", "iso_1", "iso_2", "rho", "mt_tot", "d0_1", "d0_2", "dZ_1", "dZ_2"]

    configs = []
    for channel in channels:
        if args.categories is None:
            categories = [channel+"_"+v for v in variables]
        shapes = args.shapes if args.shapes is not None else "shapes_{}.root".format(channel)
        if "em" in channel:
            bkg_processes = [p for p in bkg_processes if p not in ["ZJ", "TTJ", "VVJ"]]
            bkg_processes_names = [p for p in bkg_processes_names if p not in ["zj", "ttj", "vvj"]]
        if len(variables)==1:
            variables=[variables[0]]*len(categories)
        for variable, category in zip(variables, categories):
            config = deepcopy(config_template)

            if args.chi2:
                config["analysis_modules"].append("AddHistograms")
                config["analysis_modules"].append("Chi2Test")
                config["add_nicks"] = [" ".join(bkg_processes_names)]
                config["add_result_nicks"] = ["tot_background_noplot"]
                config["chi2test_nicks"] = ["tot_background_noplot data"]
                config["chi2test_compare"] = ["UW CHI2/NDF"]

            config["files"] = [shapes]
            config["lumis"] = [lumi]
            config["year"] = era.strip("Run")
            config["output_dir"] = output_dir+"/"+channel
            config["y_log"] = True if ((variable in logvars) or y_log) else False
            config["y_rel_lims"] = [5, 500] if (variable in logvars) else [0.9, 1.5]
            config["markers"] = ["HIST"] * len(bkg_processes_names) + ["LINE"]*len(signal_names) + ["P"] + ["E2"] + ["LINE"]*len(signal_names) + ["P"]
            config["legend_markers"] = ["F"] * (len(bkg_processes_names))  +  ["LINE"]*len(signal_names) +  ["ELP"] + ["E2"] + ["L"]*len(signal_names) + ["P"]
            config["labels"] = bkg_processes_names + signal_names + ["data"
                                                      ] + [""]*len(signal_names) + config["labels"]
            config["colors"] = bkg_processes_names + signal_names + ["data"
                                                      ] + ["#B7B7B7"] + signal_names + ["#000000"]
            config["nicks"] = bkg_processes_names + signal_names + ["data"]
            config["x_expressions"] = [
                "#" + "#".join([
                    channel, category, process, analysis, era, variable, mass
                ]) + "#" for process in bkg_processes+signal
            ] + [
                "#" + "#".join([
                    channel, category, "data_obs", analysis, era, variable,
                    mass
                ]) + "#"
            ]
            if args.emb == False:
                config["filename"] = "_".join(
                    [channel, category, analysis, era, variable, mass])
            else:
                config["filename"] = "_".join(
                    [channel, category, analysis, era, variable, mass,"emb"])
            if args.comparison:
                config["filename"] = "_".join(
                    [channel, category, analysis, era, variable, mass,"comparison"])
            if args.ff:
                config["filename"] = config["filename"]+"_ff"
            if not args.x_label == None:
                config["x_label"] = args.x_label
            else:
                config["x_label"] = "_".join([channel, variable])
            config["title"] = "_".join(["channel", channel, category])
            config["stacks"] = ["mc"] * len(bkg_processes_names) + signal_names + [
                "data"
            ] + [x+"Ratio" for x in signal_names] + config["stacks"]
            config["ratio_denominator_nicks"] = [
                " ".join(bkg_processes_names)
            ] * (2+len(signal_names))
            config["ratio_numerator_nicks"] = [" ".join(bkg_processes_names)] + [" ".join(bkg_processes_names+[signal_names[0]])]+ [" ".join(bkg_processes_names+[signal_names[1]])] + ["data"]
            config["ratio_result_nicks"] = ["bkg_ratio"] + [x+"_ratio" for x in signal_names] + ["data_ratio"]
            if args.comparison:
                config["markers"] = ["HIST"] + ["LINE"] + ["HIST"] * (len(bkg_processes_names)-1) +  ["EX0"] + ["E2", "EX0"] + ["EX0"]
                config["legend_markers"] = ["F"] + ["L"]  + ["F"]  * (len(bkg_processes_names)-1)  + ["PEX0"] +  ["F", "PEX0"] + ["PEX0"]
                config["labels"] = [bkg_processes_names[0]] + ["Z #rightarrow #tau#tau (simulation)"] + bkg_processes_names[1:] + ["data"
                                                          ] +  ["Bkg. (embedded) unc.",  "Obs./Bkg. (simulation)", "Obs./Bkg. (embedded)"]
                config["colors"] = [bkg_processes_names[0]] + ["#C70039"] + bkg_processes_names[1:] + ["data"
                                                          ] + ["#B7B7B7", " #C70039 ", "#000000"]

                                                          #~ ] + ["#B7B7B7", "#ce661c", "#000000"]
                config["subplot_legend"] =  [
                                            0.195,
                                            0.77,
                                            0.92,
                                            0.93
                                        ],
                config["subplot_legend_cols"] = 3
                config["subplot_legend_fontsize"] = 0.06
                config["y_subplot_label"] = ""
                config["legend_fontsize"] = 0.044
                bkg_processes_names_noplot = ["ztt_noplot","ttt_noplot","vvt_noplot"] + [x+"_noplot" for x in bkg_processes_names if not "emb" in x]
                config["nicks"] = bkg_processes_names + bkg_processes_names_noplot + ["data"]
                config["analysis_modules"].append("AddHistograms")
                config["add_nicks"] = [" ".join(bkg_processes_names_noplot)]
                config["add_result_nicks"] = ["ztt"]
                config["add_result_position"] = 1
                config["x_expressions"] = [
                    "#" + "#".join([
                        channel, category, process, analysis, era, variable, mass
                    ]) + "#" for process in bkg_processes
                ] + [
                    "#" + "#".join([
                        channel, category, process, analysis, era, variable, mass
                    ]) + "#" for process in ["ZTT","TTT","VVT"] + [x for x in bkg_processes if x!="EMB"]
                ] + [
                    "#" + "#".join([
                        channel, category, "data_obs", analysis, era, variable,
                        mass
                    ]) + "#"
                ]
                config["stacks"] = ["mc"] + ["ztt"] + ["mc"] * (len(bkg_processes_names)-1) + ["data"] + config_template["stacks"] + ["ratio_data_zttmc"]
                config["ratio_denominator_nicks"] = [" ".join(bkg_processes_names)] + [" ".join(bkg_processes_names_noplot)] + [" ".join(bkg_processes_names)]
                config["ratio_numerator_nicks"] = [
                    " ".join(bkg_processes_names), "data", "data"
                ]
                config["ratio_result_nicks"] = ["ratio_Bkg", "ratio_Data_to_MC", "ratio_Data"]
            configs.append(config)

    higgsplot.HiggsPlotter(
        list_of_config_dicts=configs,
        list_of_args_strings=[args.additional_arguments],
        n_processes=args.num_processes)


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("plot_nominal.log", logging.DEBUG)
    main(args)
